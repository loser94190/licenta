class Recommender:

    def __init__(self, num, k, data, distance = 'manhattan'):
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
                dist += abs(rating1[key] - rating2[key])
                common = True
        if common:
            return dist
        return -1 #no rating in common

    def nearestNeighbor(self, username):
        distances = []

        for instance in self.data:
            if instance != username:
                distance = self.function(self.data[username], self.data[instance])
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

            for
