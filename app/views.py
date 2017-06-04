from flask import render_template, flash, redirect, request, session, Flask
from app import app
#from flask.ext.pymongo import PyMongo
from flask_pymongo import PyMongo
import hashlib
from flask.ext.login import login_user, logout_user, login_required
from .forms import LoginForm
from .user import User


mongo = PyMongo(app)

@app.route('/')
@app.route('/index')
def index():
    if 'username' in session:
        return render_template("/index.html",
                               title='Home',
                               name = session['username'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        user_typed = users.find_one({'name': request.form['username']})

        if user_typed is None:
            return render_template("error.html",
                                   message='User does not exist')
        elif hashlib.sha224((request.form['pass']).encode('utf-8')).hexdigest() == user_typed['pass']:
            session['username'] = request.form['username']
            user_object = User(user_typed['_id'])
            login_user()
            return redirect('/index')
        return render_template("error.html",
                               message='Bad password')

    return render_template('/login.html',
                            title = 'LOGIN')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        user_exists = mongo.db.users.find_one({'name': request.form['username']})

        if user_exists is None:
            hashed_password = hashlib.sha224((request.form['pass']).encode('utf-8')).hexdigest()
            users.insert({'name': request.form['username'], 'pass': hashed_password})
            session['username'] = request.form['username']
            flash('registration succesful')
            return redirect('/index')
        return 'That user already exists'

    return render_template('/register.html',
                           title='REGISTER')


