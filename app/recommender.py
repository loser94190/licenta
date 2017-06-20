import math


class Recommender:

    def __init__(self, data, distance = 'manhattan', num=3, k=2):
        self.k = k
        self.num = num
        self.data = data
        self.distance = distance

        if self.distance == 'manhattan':
            self.function = self.manhattan

        if self.distance == 'euclidean':
            self.function = self.euclidean

        if self.distance == 'minkowski':
            self.function = self.minkowski

    def manhattan(self, rating1, rating2):
        dist = 0
        common = False
        for key in rating1:
            if key in rating2:
                dist += abs(float(rating1[key]) - float(rating2[key]))
                common = True
        if common:
            return dist
        return 1000 #no rating in common

    def minkowski(self, rating1, rating2, mink):
        dist = 0
        common = False
        for key in rating1:
            for key in rating2:
                dist += pow(float(rating1[key]) - float(rating2[key]), mink)
                common = True
        if common:
            return pow(dist, 1/mink)
        return 1000 #no rating in common

    def euclidean(self, rating1, rating2):
        dist = 0
        common = False
        for key in rating1:
            for key in rating2:
                dist += pow(float(rating1[key]) - float(rating2[key]), 2)
                common = True
        if common:
            return pow(dist, 1/2)
        return 1000 #no rating in common

    def pearson(self, rating1, rating2):
        sum_xy = 0
        sum_x = 0
        sum_y = 0
        sum_yy = 0
        sum_xx = 0
        numitor = 0
        numarator = 0
        n = 0

        for k in rating1:
            if k in rating2:
                x = float(rating1[k])
                y = float(rating2[k])
                n += 1
                sum_xy += (x * y)
                sum_x += x
                sum_y += y
                sum_xx += x ** 2
                sum_yy += y ** 2
            if n == 0:
                return 0
        numarator = (n * sum_xy) - (sum_x * sum_y)
        numitor = math.sqrt((n * sum_xx) - (sum_x ** 2)) * math.sqrt((n * sum_yy) - (sum_y ** 2))
        # print("NUMITOR", numitor)
        # print("NUMARATOR", numarator)
        return numarator / numitor


    def nearestNeighbor(self, username):
        #list that will hold the dist values
        distances = []
        print(username)
        for instance in self.data:
            #skip current user
            if instance != username:
                #self.function is the chosen dist function
                distance = self.function(self.data[username], self.data[instance])
                distances.append((instance, distance))

        #using the pearson correlation the list will be reversed
        if self.function == self.pearson:
            #sort the list so the first k elements will be the
            #first k nearest neighbors
            distances.sort(key=lambda tuple: tuple[1], reverse=True)
        else:
            distances.sort(key=lambda tuple: tuple[1], reverse=False)
        return distances

    def recommend(self, user):
        recommendations = {}

        if self.function == self.pearson:
            nearest = [touple for touple in self.nearestNeighbor(user) if touple[1] > 0]
            self.k = len(nearest)

        else:
            nearest = self.nearestNeighbor(user)

        userRatings = self.data[user]
        totalDistance = 0.0

        print("NEAREST", nearest)

        for i in range(self.k):
            totalDistance += nearest[i][1]

        for i in range(self.k):
            if self.function ==self.pearson:
                weight = nearest[i][1]/totalDistance
            else:
                weight = nearest[i][1]/totalDistance

            name = nearest[i][0]

            neighborRatings = self.data[name]

            for movie in neighborRatings:
                if not movie in userRatings:
                    if movie not in recommendations:
                        recommendations[movie] = float(neighborRatings[movie]) * weight
                        #print("REC", movie, "=", float(neighborRatings[movie]), weight)
                    else:
                        recommendations[movie] = recommendations[
                                                         movie] + neighborRatings[movie] * weight
                        #print("REC1", recommendations)

        recommendations = list(recommendations.items())
        recommendations.sort(key=lambda tuple: tuple[1], reverse=True)

        #print(recommendations)

        if [rec for rec in recommendations[:self.num] if rec[1] > 2.5]:
            print(rec for rec in recommendations[:self.num] if rec[1] > 2.5)
            return [rec for rec in recommendations[:self.num] if rec[1] > 2.5]

        else:
            print("recommendations", recommendations)
            return recommendations[:self.num]
#data = {'Andrei': {'The Hobbit': '3', 'Lord of the rings': '1', 'Guardians': '5'}, 'Ion': {'The Hobbit': '3', 'Lord of the rings': '4'}, '_Gigel': {'The Hobbit': '5', 'Random Movie': '4'}}




#r = Recommender(data)
#print(r.recommend("Ion"))

