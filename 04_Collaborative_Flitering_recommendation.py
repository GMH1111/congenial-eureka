# -*-coding=utf-8 -*-
from texttable import Texttable
import math


# 从文件夹中读读取数据
def readFile(filename):
    # files = open(filename, "r", encoding="utf-8")
    # 如果读取不成功试一下
    files = open(filename, "r", encoding="iso-8859-15")
    data = []  # 列表
    for line in files.readlines():
        item = line.strip().split("::")
        data.append(item)
    return data


class CollaborativeFlitering(object):
    def __init__(self, movies, ratings, k=5, n=10):  # 五个邻居推荐十部电影
        self.movies = movies
        self.ratings = ratings
        # 邻居个数
        self.k = k
        # 推荐个数
        self.n = n
        # 用户对电影的评分
        # 数据格式{'UserID：用户ID':[(MovieID：电影ID,Rating：用户对电影的评星)]}
        self.userDict = {}
        # 对某电影评分的用户
        # 数据格式：{'MovieID：电影ID',[UserID：用户ID]}
        # {'1',[1,2,3..],...}
        self.movieDict = {}
        # 邻居的信息
        self.neighbor_dist = []
        self.neighbors = {}
        self.neighbor_user_id = []
        # 推荐列表
        self.backup_recommend = []
        self.recommendList = []
        self.cost = 0.0

    # 数据处理整合 userdict存放每一个用户看过的电影
    #             moviedict存放每一部电影被那些用户看过
    def get_data(self):
        self.userDict = {}
        self.movieDict = {}
        # 整理数据userDict
        for rating in self.ratings:  # 【1，1193，5】 user_id, movie_id, grade
            user_info = (rating[1], float(rating[2]) / 5)
            if rating[0] not in self.userDict.keys():
                self.userDict[rating[0]] = [user_info]
            else:
                self.userDict[rating[0]].append(user_info)
            # 整理数据movieDict
            if rating[1] not in self.movieDict.keys():
                self.movieDict[rating[1]] = [rating[0]]
            else:
                self.movieDict[rating[1]].append(rating[0])

    #  找邻居
    def get_neighbors(self, userId):  # USERID = 1
        user_exps = self.userDict[userId]  # userid 看过的所有电影
        # print("userexps", user_exps)
        for user_exp in user_exps:
            # print("看过", user_exp, "电影的人:", self.movieDict[user_exp[0]])
            for audience in self.movieDict[user_exp[0]]:
                # print("get_audiences", audience)
                if audience in self.neighbors:
                    # print(audience)
                    self.neighbors[audience] += 1
                else:
                    self.neighbors[audience] = 1
        self.neighbors = sorted((self.neighbors).items(), key=lambda x: x[1], reverse=True)  # 排序
        self.neighbors.pop(0)
        # print(self.neighbors)
        # self.neighbors = [(邻居id,与你共同看过的电影数量),...]

    # 计算余弦值
    """2、  余弦定理
            在空间模型中，两条线的夹角越小，它们的余弦值就越大，而它们越相似(重叠或者平行)。
            从上面看出空间模型中两条连线夹角的余弦值为：
            举一个具体的例子，假如文档X和文档Y对应向量分别是x1,x2,...,x64000 和y1,y2,...,y64000,
            那么它们夹角的余弦等于cosθ = (x1y1+x2y2+...+xnyn)/sqrt(x1^2+x2^2+...+xn^2)*sqrt(y1^2+y2^2+...+yn^2"""

    def cal_dist(self, neighborId, userId):
        x = 0.0
        y = 0.0
        z = 0.0
        for user_exp in self.userDict[userId]:
            for neighbor_exp in self.userDict[neighborId]:
                if neighbor_exp[0] == user_exp[0]:
                    x += float(neighbor_exp[1]) * float(neighbor_exp[1])
                    y += float(user_exp[1]) * float(user_exp[1])
                    z += float(neighbor_exp[1]) * float(user_exp[1])
        if z == 0.0:
            return 0
        cos = float(z / math.sqrt(x * y))
        return cos

    # 找电影
    def get_movies(self, userId):  # 找出推荐电影的列表
        for neighbor in self.neighbors:  # 取一个邻居出来
            if neighbor[0] != userId:  # 如果邻居不是他自己
                self.neighbor_dist.append([self.cal_dist(neighbor[0], userId), neighbor[0]])
                # 计算这个邻居的相似度并保存 （相似度，邻居id）
                self.neighbor_dist.sort(reverse=True)  # 按照相似度从大到小排序
                self.neighbor_dist = self.neighbor_dist[:5]  # 找出前五个相似度最高的邻居

        recommend_dict = {}
        for neighbor in self.neighbor_dist:  # 从最终的邻居列表里 取出每一个邻居  最相似邻居
            neighbor_user_id = neighbor[1]  # neighbor_user_id 最相似邻居id
            movies = self.userDict[neighbor_user_id]
            for movie in movies:
                if movie[0] not in recommend_dict:
                    recommend_dict[movie[0]] = neighbor[0]
                    self.neighbor_user_id.append(neighbor_user_id)
                else:
                    recommend_dict[movie[0]] += neighbor[0]
        recommend_dict = sorted(recommend_dict.items(), key=lambda x: x[1], reverse=True)
        for key in recommend_dict:
            self.recommendList.append([key[0], key[1]])
        self.recommendList.sort(reverse=True)
        return [(k[1], k[0]) for k in self.recommendList]


def main():
    movies = readFile("E:/GMH/python/FWs_graduate/ml-1m/movies.dat")
    ratings = readFile("E:/GMH/python/FWs_graduate/ml-1m/testdata.txt")
    obj = CollaborativeFlitering(movies, ratings)  # 创建对象 根据协同过滤算法创建的
    obj.get_data()
    # 调用对象的get_data()方法，整理出列表userdict[[用户1，（用户1看过的电影）]，[用户2,(用户2看过的电影)]，。。。。。。]
    #                                   moviedict[[电影1，(看过电影1的用户)]，[电影2，(看过电影2的用户)]，。。。。。。]）

    obj.get_neighbors("1")  # 根据上一步得到的列表 计算出目标用户的邻居们 并根据他们都看过的电影的个数由大到小排序 并返回一个邻居们列表
    recommend_movies = obj.get_movies("1")
    #  根据上一部的邻居们的列表 ，计算邻居跟目标用户的相似度，并根据相似度由大到小排列，并返回一个根据相似度排列的新的邻居列表
    #  此列表就是我们最终要找的相似度高的邻居列表
    #  并根据这个列表  找出要推荐的电影
    recommend_movies.sort(reverse=True)
    print("推荐电影：")

    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_dtype(['t', 't', 't'])
    table.set_cols_align(["l", "l", "l"])
    rows = list()
    rows.append([u"movie name", u"release", u"from userid"])
    for recommend_movie in recommend_movies[:100]:
        for movie in movies:
            if movie[0] == recommend_movie[1]:
                rows.append([movie[1], movie[2], obj.neighbor_user_id.pop(0)])
    table.add_rows(rows)
    print(table.draw())


if __name__ == '__main__':
    main()
