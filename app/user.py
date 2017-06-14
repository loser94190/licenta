
import hashlib

from flask.ext.login import UserMixin


class User(UserMixin):
    def __init__(self,user_id):
        self.id = user_id
        self.username = user_id
        self.ratings = {}

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def set_rating(self, movie, rating):
        self.ratings[movie] = rating


    @staticmethod
    def validate(pass_hash, password):
        return hashlib.sha224((password).encode('utf-8')).hexdigest() == pass_hash

class PrintedUser():
    def __init__(self, name, poster, favorite):
        self.name = name
        self.poster = poster
        self.favorite = favorite