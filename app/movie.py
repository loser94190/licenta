import omdb
import json, requests
from flask_pymongo import PyMongo

class Movie:
    def __init__(self,name):
        self.name = name
        self.IMDb_rating = 0
        self.baseurl = "http://omdbapi.com/?t="
        self.apikey = '43783491'
        self.poster = ''
        self.plot = ''
        self.get_info()
        self.status = True


    def get_info(self):
        movieTitle = self.name.rstrip("\n")  # get rid of newline characters
        status = False
        try:
            res = omdb.request(t=movieTitle,plot='short', tomatoes='true', timeout=5, apikey=self.apikey)
            info = json.loads(res.text)
            status = True
        except:
            self.status = False
        if status:
            self.IMDb_rating = info['Ratings'][0]['Value']
            self.poster = info['Poster']
            self.name = info['Title']
            self.plot = info['Plot']


class LocalMovie:
    def __init__(self, title, rating, poster, plot):
        self.title = title
        self.rating = rating
        self.poster = poster
        self.plot = plot

mov = Movie("The Matrix")
print(mov.name)

m = Movie('matrix')
m.get_info()



