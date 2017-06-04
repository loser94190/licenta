
import hashlib


class User():
    def __init__(self, username):
        self.username = username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def get_id(self):
        return self.username

    @staticmethod
    def validate(pass_hash, password):
        return hashlib.sha224((password).encode('utf-8')).hexdigest() == pass_hash
