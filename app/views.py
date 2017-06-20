import gc
from flask import render_template, flash, redirect, request, session, Flask
from flask import url_for
#from flask.ext.login import LoginManager
from flask_login import LoginManager
from app import app
#from flask.ext.pymongo import PyMongo
from flask_pymongo import PyMongo, pymongo
import hashlib
#from flask.ext.login import login_user, logout_user, login_required

from flask_login import login_user, logout_user, login_required
#from .forms import LoginForm
from .user import User
from .recommender import Recommender
from .movie import Movie, LocalMovie

from flask_paginate import Pagination

import omdb
import json, requests


mongo = PyMongo(app)
#mongo.db.users.createIndex({'name':1})
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message = u"You are now logged in"



#user_movie_list = ['Movie1', 'Movie2']
#movie_list = ['Lord of the rings', "The Hobbit", "Matrix", 'Titanic', 'Life', 'Kung Fu Panda', 'X-men']

@app.route('/')
@app.route('/index')
def index():
    #get the number of users
    number = mongo.db.users.find({'name':{'$exists':True}}).count()

    #get the number of movies
    number_of_movies = mongo.db.movie_db.find({'Title':{'$exists':True}}).count()
    plural = False
    if number > 1:
        plural = True

    try:
        session['username']
    except KeyError:
        return render_template("/index.html",
                               user_number=number,
                               movie_number=number_of_movies,
                               plural_check=plural)

    return render_template("/index.html",
                           username=session['username'],
                           user_number=number,
                           movie_number=number_of_movies,
                           plural_check=plural)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        #check if the user exists in the data base
        #None if not
        user_typed = users.find_one({'name': request.form['username']})
        print(user_typed)

        if user_typed is None:
            return render_template("login.html",
                                   error = "User does not exist")

        elif hashlib.sha224((request.form['pass']).encode('utf-8')).hexdigest() == user_typed['pass']:
            session['username'] = request.form['username']
            session['logged_in'] = True
            user_object = User(user_typed['name'])
            login_user(user_object)

            return redirect(url_for('recommender'))
        flash('Bad password', 'danger')
        return render_template("login.html")

    return render_template('/login.html',
                            title = 'LOGIN')


@app.route('/profile')
@login_required
def profile():
    movies = mongo.db.users.find_one({"name":session['username']})['movies']
    return render_template('/profile.html',
                           username = session['username'])


@app.route('/logout')
@login_required
def logout():
   logout_user()
   session.pop('username', None)
   session['logged_in']= False
   return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    #logout_user()
    #session.pop('username', None)
    #session['logged_in'] = False

    first = True
    if request.method == 'POST':
        users = mongo.db.users
        user_exists = mongo.db.users.find_one({'name': request.form['username']})
        first = False

        if user_exists is None and len(request.form['username']) >= 3 and len(request.form['pass']) >= 3:
            hashed_password = hashlib.sha224((request.form['pass']).encode('utf-8')).hexdigest()
            users.insert({'name': request.form['username'], 'pass': hashed_password, 'movies':[]})
            session['username'] = request.form['username']

            flash("Registration succesful", 'success')
            return render_template('/register.html',
                                    registration = True)

        elif len(request.form['username']) < 3:
            return render_template('/register.html',
                                   registration=False,
                                   error="Username length should be > 3")

        elif len(request.form['pass']) < 3:
            return render_template('/register.html',
                                   registration=False,
                                   error="Password length should be > 3")

        return render_template('/register.html',
                               registration=False,
                               error="This user already exists")

    return render_template('/register.html',
                           title='REGISTER')


@app.route('/recommender',  methods=['GET', 'POST'])
@login_required
def recommender():

    movie_db = mongo.db.movie_collection
    movie_data = mongo.db.movie_db
    movie_list = [movie['Title'] for movie in movie_data.find({"Title": {'$exists': True}}).sort("Title", pymongo.ASCENDING)]

    #print(movie_list)
    users = mongo.db.users
    data = {}

    user_mv = users.find_one({"name": session['username']})['movies']

    movies = []

    if user_mv:
        movies = [x['movie'] for x in users.find_one({"name": session['username']})['movies']]
    #user_movie_list = []
    if request.method == 'POST':
        if session['username']:
            mov = request.form['movie']
            rating = request.form['rating']
            title = movie_data.find_one({'Title': mov})['Title']
            _rating = movie_data.find_one({'Title': mov})['IMDb_rating']
            poster = movie_data.find_one({'Title': mov})['Poster']
            plot = movie_data.find_one({'Title': mov})['Plot']
            genre = movie_data.find_one({'Title': mov})['Genre']
            omdb_movie = LocalMovie(title, _rating, poster, plot, genre)

            if mov not in movies:
                users.find_and_modify(query={"name":session['username']},
                                    update={"$push": {"movies" : {'movie':mov, 'rating':rating}}})

                print("Movie info" + "\n")
                # where mov is the movie added by the user
                if not movie_db.find_one({'name': mov}):
                    movie_db.insert({'name': mov, 'ratings': [{'rating':rating, 'user':session['username']}]})
                else:
                    movie_db.find_and_modify(
                        query = {"name": mov},
                        update={"$push": {"ratings":{'user':session['username'], 'rating':rating}}})

            else:
                #print(users.find({"name": session['username'],'movies.movie':{'$exists':True}}))
                #users.find_and_modify(query={"name": session['username'],'movies.movie':{'$exists':True}},
                                      #update={"$set": {movie: rating}})
                #users.update({"name":session['username'], { '$set': {"movies[movie]" : rating} })
                ##users.update({'name': session['username'], "movies.movie" : mov}, { '$set': {"rating" : rating} })

                #users.find_and_modify(query={"name": session['username'], 'movies.movie': mov},
                    #update={"$set": {"movies.movie.rating": rating}})

                users.update({
                    "name": session['username'],
                    "movies": {"$elemMatch": {"movie": mov}}},
                    {"$set": {"movies.$.rating": rating}}
                )


                #print("MORE INFO")
                #print(users.find_one({"name": session['username'],
                    #"movies": {"$elemMatch": {"movie": mov}}}))

            if user_mv:
                movies = [x['movie'] for x in users.find_one({"name": session['username']})['movies']]
                #print("MORE INFO")
                #print(movies)


    #find each document that has a 'movies' field,
    #with size not 0
    for doc in users.find({'movies':{'$exists':True, '$not': {'$size': 0}}}):
        #insert the data in a dictionary {'movie': rating}
        #that will be used as input for the recommender system
        data[doc['name']] = {z['movie']:z['rating'] for z in doc['movies']}

    print("DATA INFO")
    print(data)

    r = Recommender(data)

    try:
        #print(r.recommend(session['username']))
        recommendations = [touple[0] for touple in r.recommend(session['username'])]
        omdb_movies = [Movie(mov) for mov in recommendations]

    #check if there are movies in the input data set
    except KeyError:
        text = 'You need to add some movies'
        omdb_movies = []

    #check if there are output recommendations
    except IndexError:
        text = "No more recommendations"
        omdb_movies = []

    return render_template("/recommender.html",
                           user=session['username'],
                           movies=movie_list,
                           user_movies=movies,
                           recommenations=omdb_movies)



'''
@app.route('/recommender',  methods=['GET', 'POST'])
@login_required
def recommender():
    users = mongo.db.users
    user_mv = users.find_one({"name": session['username']})['movies']
    #print(movie_list)
    movies = []
    print("INFO")
    print([x['movie'] for x in users.find_one({"name": session['username']})['movies']])
    if user_mv:
        movies = list(k for d in user_mv for k in d.keys())
    #user_movie_list = []
    if request.method == 'POST':
        if session['username']:
            movie = request.form['movie']
            rating = request.form['rating']
            if movie not in movies:
                users.find_and_modify(query={"name":session['username']},
                                    update={"$push": {"movies" : {'movie':movie, 'rating':rating}}})
            else:
                print(users.find({"name": session['username'],'movies.movie':{'$exists':True}}))
                #users.find_and_modify(query={"name": session['username'],'movies.movie':{'$exists':True}},
                                      #update={"$set": {movie: rating}})
                #users.update({"name":session['username'], { '$set': {"movies[movie]" : rating} })
                users.update({'name': session['username'], }, { '$set': {"movies.movie" : rating} })
            if user_mv:
                movies = list(k for d in users.find_one({"name": session['username']})['movies']['movie'] for k in d.keys())
            #print(movies)
    return render_template("/recommender.html",
                           user=session['username'],
                           movies = movie_list,
                           user_movies = movies)
'''


@app.route('/users')
@login_required
def users():
    users = mongo.db.users

    #query and transform to list
    user_list = [user['name'] for user in users.find({'name':{'$exists':True}})]
    print(user_list)



    search = False
    q = request.args.get('q')
    if q:
        search = True

    page = request.args.get('page', type=int, default=1)

    ITEMS_PER_PAGE = 3
    #get the current item number
    i = (page - 1) * ITEMS_PER_PAGE
    entries = user_list[i:i+ITEMS_PER_PAGE]

    pagination = Pagination(page=page, total=len(user_list), search=search, record_name='movies', per_page=ITEMS_PER_PAGE, css_framework='bootstrap3')

    return render_template("/users.html",
                           users=entries,
                           pagination=pagination,
                           page=page,
                           per_page=ITEMS_PER_PAGE)

@app.route('/movies')
@login_required
def movies():
    movie_data = mongo.db.movie_db
    movie_list = [movie['Title'] for movie in movie_data.find({"Title":{'$exists':True}}).sort("Title", pymongo.ASCENDING)]
    omdb_movies = [Movie(mov) for mov in movie_list]

    search = False
    q = request.args.get('q')
    if q:
        search = True

    page = request.args.get('page', type=int, default=1)

    ITEMS_PER_PAGE = 5
    #get the current item number
    i = (page - 1) * ITEMS_PER_PAGE
    entries = omdb_movies[i:i+ITEMS_PER_PAGE]

    pagination = Pagination(page=page, total=len(movie_list), search=search, record_name='movies', per_page=ITEMS_PER_PAGE, css_framework='bootstrap3')

    return render_template("/movies.html",
                           movies=entries,
                           pagination=pagination,
                           page=page,
                           per_page=5)


@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if request.method == 'POST':
        movies = mongo.db.movie_db

        movie_from_form = request.form['movie']
        try:
            omdb_movie = Movie(movie_from_form)
            if not movies.find_one({"Title":omdb_movie.name}) and omdb_movie.status:
                #where omdb_movie is an instance of Movie
                movies.insert({'Title': omdb_movie.name, 'IMDb_rating': omdb_movie.IMDb_rating, 'Poster': omdb_movie.poster, 'Plot':omdb_movie.plot, 'Genre': omdb_movie.genre})
                print("OMDB", omdb_movie.genre)
                flash('Movie was added', 'success')
            else:
                flash('Movie already exists', 'danger')
        except:
            flash('Something happened:', 'danger')

    return render_template("add_movie.html")



@login_manager.user_loader
def load_user(id):
    return User(id)

