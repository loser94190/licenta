from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager

app = Flask(__name__)

lm = LoginManager()
lm.init_app(app)

app.config.from_object('config')

app.config['MONGO_DBNAME'] = 'MovieRecommender'
app.config['MONGO_URI'] = 'mongodb://localhost/MovieRecommender'

from app import views