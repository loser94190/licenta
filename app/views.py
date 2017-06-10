import gc
from flask import render_template, flash, redirect, request, session, Flask
from flask import url_for
from flask.ext.login import LoginManager

from app import app
#from flask.ext.pymongo import PyMongo
from flask_pymongo import PyMongo
import hashlib
from flask.ext.login import login_user, logout_user, login_required
from .forms import LoginForm
from .user import User


mongo = PyMongo(app)
#mongo.db.users.createIndex({'name':1})
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message = u"You are now logged in"

movie_list = ['Lord of the rings', "The Hobbit", "Movie"]
user_movie_list = ['Movie1', 'Movie2']

@app.route('/')
@app.route('/index')
def index():
    if 'username' in session:
        return render_template("/index.html",
                               title='Home',
                               name=session['username'])
    else:
        return render_template("/register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        user_typed = users.find_one({'name': request.form['username']})
        print(user_typed)

        error = ""

        if user_typed is None:
            return render_template("login.html",
                                   error='User does not exist')
        elif hashlib.sha224((request.form['pass']).encode('utf-8')).hexdigest() == user_typed['pass']:
            session['username'] = request.form['username']
            session['logged_in'] = True
            user_object = User(user_typed['name'])
            login_user(user_object)
            return redirect(url_for('recommender'))
        return render_template("login.html",
                               error='Bad password')

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
    logout_user()
    session.pop('username', None)
    session['logged_in'] = False
    if request.method == 'POST':
        users = mongo.db.users
        user_exists = mongo.db.users.find_one({'name': request.form['username']})

        if user_exists is None:
            hashed_password = hashlib.sha224((request.form['pass']).encode('utf-8')).hexdigest()
            users.insert({'name': request.form['username'], 'pass': hashed_password, 'movies':[]})
            session['username'] = request.form['username']
            flash('registration succesful')
            return redirect('/index')
        return render_template('/register.html',
                               error  = "This user already exists")

    return render_template('/register.html',
                           title='REGISTER')


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
        movies = [x['movie'] for x in users.find_one({"name": session['username']})['movies']]
    #user_movie_list = []
    if request.method == 'POST':
        if session['username']:
            mov = request.form['movie']
            rating = request.form['rating']
            if mov not in movies:
                users.find_and_modify(query={"name":session['username']},
                                    update={"$push": {"movies" : {'movie':mov, 'rating:':rating}}})
            else:
                #print(users.find({"name": session['username'],'movies.movie':{'$exists':True}}))
                #users.find_and_modify(query={"name": session['username'],'movies.movie':{'$exists':True}},
                                      #update={"$set": {movie: rating}})
                #users.update({"name":session['username'], { '$set': {"movies[movie]" : rating} })
                ##users.update({'name': session['username'], "movies.movie" : mov}, { '$set': {"rating" : rating} })
                users.find_and_modify(query={"name": session['username'], 'movies.movie': mov},
                    update={"$set": {"movies.movie.mov.rating": rating}})
                print("MORE INFO")
                print(users.find_one({"name": session['username'], 'movies.movie': mov}))
            if user_mv:
                movies = [x['movie'] for x in users.find_one({"name": session['username']})['movies']]
                #print("MORE INFO")
                #print(movies)
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
                                    update={"$push": {"movies" : {'movie':movie, 'rating:':rating}}})
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
@login_manager.user_loader
def load_user(id):
    return User(id)