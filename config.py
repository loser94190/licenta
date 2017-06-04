from flask import Flask

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'MovieRecommender'
app.config['MONGO_URI'] = 'mongodb://MovieRecommender'
app.secret_key = 'secret_key'

from app import views