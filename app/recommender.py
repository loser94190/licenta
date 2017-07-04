import math


class Recommender:

    def __init__(self, data, distance='euclidean', num=5, k=2):
        self.k = k
        self.num = num
        self.data = data
        self.distance = distance

        if self.distance == 'manhattan':
            self.function = self.manhattan

        if self.distance == 'euclidean':
            self.function = self.euclidean

        if self.distance == 'pearson':
            self.function = self.pearson

        if self.distance == 'cos':
            self.function = self.cos_similarity

        if self.distance == 'jac':
            self.function = self.jaccard_coef




    def intersection_size(self, user1, user2):
        # used for jaccard similarity
        n = 0
        for k in user1:
            if k in user2:
                n += 1
        return n

    def union_size(self, user1, user2):
        #used for jaccard similarity
        return len(dict(user1, **user2))

    def square_rooted_list(self, x):
        #Used to determine the numerator
        #for cosine similarity
        return round(math.sqrt(sum([float(a) * float(a) for a in x])), 4)


    def cos_similarity(self, user_ratings_1, user_ratings_2):

        numarator = 0
        numitor = self.square_rooted_list([user_ratings_1[k] for k in user_ratings_1]) * \
                  self.square_rooted_list([user_ratings_2[k] for k in user_ratings_2])

        for k in user_ratings_1:
            if k in user_ratings_2:
                numarator += float(user_ratings_1[k]) * float(user_ratings_2[k])

        if numitor == 0:
            return 0

        return round(numarator / float(numitor), 4)


    def jaccard_coef(self, user1, user2):
        #the count of the intersectiom
        intersect = self.intersection_size(user1, user2)
        #the count of the union
        union = self.union_size(user1, user2)
        return float(intersect)/float(union)

    def jaccard_dist(self, user1, user2):
        intersect = self.intersection_size(user1, user2)
        union = self.union_size(user1, user2)
        return float(union - intersect)/float(union)


    def manhattan(self, user1, user2):
        dist = 0
        common = False
        for k in user1:
            if k in user2:
                dist += abs(float(user1[k]) - float(user2[k]))
                common = True
        if common:
            return dist
        return 100 #no rating in common

    def minkowski(self, rating1, rating2, mink):
        dist = 0
        common = False
        for key in rating1:
            if key in rating2:
                dist += pow(float(rating1[key]) - float(rating2[key]), mink)
                common = True
        if common:
            return pow(dist, 1/mink)
        return 1000 #no rating in common

    def euclidean(self, user1, user2):
        dist = 0
        common = False
        for key in user1:
            if key in user2:
                print("KEY", key)
                dist += pow(float(user1[key]) - float(user2[key]), 2)
                common = True
        print("DIST",dist)
        if common:
            return pow(dist, 1/2)
        return 1000 #no rating in common

    def pearson(self, user1, user2):
        sum_xy, sum_x, sum_y, sum_yy, sum_xx = 0, 0, 0, 0, 0
        n = 0
        for k in user1:
            if k in user2:
                x = float(user1[k])
                y = float(user2[k])
                n += 1
                sum_xy += (x * y)
                sum_x += x
                sum_y += y
                sum_xx += x ** 2
                sum_yy += y ** 2

        numarator = (n * sum_xy) - (sum_x * sum_y)
        numitor = math.sqrt((n * sum_xx) - (sum_x ** 2)) * math.sqrt((n * sum_yy) - (sum_y ** 2))

        print("NUMARATOR= ", numarator, "NUMITOR= ", numitor)
        if n == 0 or numitor == 0:
            return 0

        return numarator / numitor


    def k_nearest(self, username):
        #list that will hold the dist values
        distances = []
        print(username)
        for instance in self.data:
            #utilizatorul curent nu se ia in considerare
            if instance != username:
                #self.function reprezinta functia de distanta
                distance = self.function(self.data[username], self.data[instance])
                distances.append((instance, distance))

        #doar pt aceste funtii se sorteaza descrescator
        if self.function == self.pearson or self.function == self.jaccard_coef or self.function == self.cos_similarity:
            #sort the list so the first k elements will be the
            #first k nearest neighbors
            distances.sort(key=lambda tuple: tuple[1], reverse=True)
        else:
            distances.sort(key=lambda tuple: tuple[1], reverse=False)
        return distances


    def recommend(self, username):
        current_ratings = self.data[username]
        dist_sum = 0.0
        result_set = {}
        pondere = 1/self.k

        if self.function == self.pearson:
            if len([tuple for tuple in self.k_nearest(username) if tuple[1] > 0]) > 0:
                knn = [tuple for tuple in self.k_nearest(username) if tuple[1] > 0]
                self.k = len(knn)
            else:
                knn = self.k_nearest(username)


        else:
            knn = self.k_nearest(username)

        print("KNN", knn)
        for i in range(self.k):
            dist_sum += knn[i][1]

        for i in range(self.k):
            if dist_sum:
                if self.function == self.pearson or self.function == self.jaccard_coef or self.function == self.cos_similarity:
                    pondere = knn[i][1]/dist_sum
                else:
                    pondere = 1/self.k
            name = knn[i][0]

            other_ratings = self.data[name]

            for movie in other_ratings:
                if movie not in current_ratings:
                    if movie not in result_set:
                        #print("MOVIE: ", movie, "RATING: ", other_ratings[movie], "dist: ", knn[i][1], "Pondere", pondere)
                        result_set[movie] = float(other_ratings[movie]) * pondere
                    else:
                        #print("MOVIE exists:", movie)
                        result_set[movie] += float(other_ratings[movie]) * pondere
        result_set = list(result_set.items())
        result_set.sort(key=lambda t: t[1], reverse=True)
        print("RES", result_set)

        if self.function == self.pearson or self.function == self.jaccard_coef or self.function == self.cos_similarity:
            if [movie for movie in result_set[:self.num] if movie[1] > 2.5]:
                return [movie for movie in result_set[:self.num] if movie[1] > 2.5]
            else:
                return result_set[:self.num]

        else:
            print("Recommended movies: ", result_set)
            return result_set[:self.num]

data = {'Andrei': {'The Hobbit': '3', 'Lord of the rings': '1', 'Guardians': '5'}, 'Ion': {'The Hobbit': '4', 'Lord of the rings': '4'}, '_Gigel': {'The Hobbit': '5', 'Random Movie': '4'}}



r = Recommender(data)
print(r.recommend("Ion"))

