import gc
from flask import render_template, flash, redirect, request, session, Flask
from flask import url_for
#from flask.ext.login import LoginManager
from flask_login import LoginManager
from app import app
#from flask.ext.pymongo import PyMongo
from flask_pymongo import PyMongo
import hashlib
#from flask.ext.login import login_user, logout_user, login_required

from flask_login import login_user, logout_user, login_required
from .forms import LoginForm
from .user import User
from .recommender import Recommender


mongo = PyMongo(app)
#mongo.db.users.createIndex({'name':1})
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message = u"You are now logged in"


movie_list = ['Lord of the rings', "The Hobbit", "Movie", 'Movie1', 'movie2', 'movie3', 'movie4']
user_movie_list = ['Movie1', 'Movie2']

@app.route('/')
@app.route('/index')
def index():
    number = mongo.db.users.find({'name':{'$exists':True}}).count()
    plural = False
    if number > 1:
        plural = True

    try:
        session['username']
    except KeyError:
        return render_template("/index.html",
                               user_number=number,
                               plural_check=plural)

    return render_template("/index.html",
                           username=session['username'],
                           user_number=number,
                           plural_check=plural)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
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
    users = mongo.db.users
    data = {}

    user_mv = users.find_one({"name": session['username']})['movies']


    #print(movie_list)
    movies = []

    #print("INFO")
    #print([x['movie'] for x in users.find_one({"name": session['username']})['movies']])
    if user_mv:
        movies = [x['movie'] for x in users.find_one({"name": session['username']})['movies']]
    #user_movie_list = []
    if request.method == 'POST':
        if session['username']:
            mov = request.form['movie']
            rating = request.form['rating']
            if mov not in movies:
                users.find_and_modify(query={"name":session['username']},
                                    update={"$push": {"movies" : {'movie':mov, 'rating':rating}}})

                print("Movie info" + "\n")
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


    for doc in users.find({'movies':{'$exists':True, '$not': {'$size': 0}}}):
        data[doc['name']] = {z['movie']:z['rating'] for z in doc['movies']}

    print("DATA INFO")
    print(data)

    r = Recommender(data)

    try:
        print(r.recommend(session['username']))
        recommendations = [touple[0] for touple in r.recommend(session['username'])]
        print(recommendations)
    except KeyError:
        text = 'You need to add some movies'
    except IndexError:
        text = "No more recommendations"

    return render_template("/recommender.html",
                           user=session['username'],
                           movies = movie_list,
                           user_movies = movies)



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
    user_list = [user['name'] for user in users.find({'name':{'$exists':True}})]
    print(user_list)
    return render_template("/users.html",
                           users=user_list)

@login_manager.user_loader
def load_user(id):
    return User(id)