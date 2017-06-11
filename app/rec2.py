data = {'2': {'The Hobbit': '3', 'Movie': '1'}, '1': {'The Hobbit': '4', 'Lord of the rings': '4'}, '5': {'The Hobbit': '5', 'Movie': '4'}}



class Recommender:

    def __init__(self, data, distance = 'manhattan', num=1, k=1):
        self.k = k
        self.num = num
        self.data = data
        self.distance = distance

        if self.distance == 'manhattan':
            self.function = self.manhattan

    def manhattan(self, rating1, rating2):
        dist = 0
        common = False
        for key in rating1:
            for key in rating2:
                dist += abs(int(rating1[key]) - int(rating2[key]))
                common = True
        if common:
            return dist
        return -1 #no rating in common

    def nearestNeighbor(self, username):
        distances = []
        for instance in self.data:
            if instance != username:
                try:
                    distance = self.function(self.data[username], self.data[instance])
                except(KeyError):
                    distance = -1
                    distances.append((instance, distance))

        distances.sort(key = lambda tuple: tuple[1], reverse = True)
        return distances

    def recommend(self, user):
        recommendations = {}

        nearest = self.nearestNeighbor(user)

        userRatings = self.data[user]
        totalDistance = 0.0

        for i in range(self.k):
            totalDistance += nearest[i][1]

        for i in range(self.k):
            weight = nearest[i][1]/totalDistance
            name = nearest[i][0]
            neighborRatings = self.data[name]

            for movie in neighborRatings:
                if not movie in userRatings:
                    if movie not in recommendations:
                        recommendations[movie] = neighborRatings[movie] * int(weight)
                        print(recommendations)
                    else:
                        recommendations[movie] = recommendations[movie] + neighborRatings[movie] * weight
                        print(recommendations)

        recommendations = list(recommendations.items())

        recommendations.sort(key=lambda tuple: tuple[1], reverse=True)

        return recommendations[:self.num]


r = Recommender(data)
print(r.recommend("2")[0][0])

