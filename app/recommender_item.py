class ItemRecommender:

    def __init__(self, data, user_data, number=4):
        self.user_data = user_data
        self. data = data
        self.number = number

    def intersection_size(self, movie1, movie2):
        # used for jaccard similarity
        set1 = set(movie1)
        set2 = set(movie2)
        print("SET", len(set1.intersection(set2)))
        print("THE SET:", set1.intersection(set2))
        return len(set1.intersection(set2))


    def union_size(self, movie1, movie2):
        #used for jaccard similarity
        res = set(movie1+ movie2)
        print("RES", res)
        return len(res)

    def jaccard_coef(self, movie1, movie2):
        #the count of the intersection
        intersect = self.intersection_size(movie1, movie2)
        #the count of the union
        union = self.union_size(movie1, movie2)
        return float(intersect)/float(union)

    def recommend(self):
        jaccard_coef_list = []
        for key in self.data:
            jaccard_coef_list.append((key, self.jaccard_coef(self.user_data, self.data[key])))

        jaccard_coef_list.sort(key=lambda t: t[1], reverse=True)

        return jaccard_coef_list[:self.number]






