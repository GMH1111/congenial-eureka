"""
链接数据库并抓取我们需要的数据
"""
import pymysql


class Command(object):
    def __init__(self):
        self.conn_douban = pymysql.connect(host='localhost', port=3306, database='movies', user='root',
                                           password='gmhGMH123',
                                           charset='utf8')

    def command_by_grade(self):
        grade = float(input("你希望看到多少分以上的电影？\n"))
        cs1 = self.conn_douban.cursor()
        sql_select = "SELECT DISTINCT movie_id,movie_name,grade FROM douban where grade>=%.1f" % grade
        cs1.execute(sql_select)
        result = cs1.fetchall()
        cs1.close()
        self.conn_douban.close()
        print("推荐电影(%.1f分以上)：" % grade)
        print("电影编号", "\t电影名", "\t\t评分")
        for i in result:
            print(i[0], "\t" + i[1], "\t", i[2])


obj = Command()
obj.command_by_grade()
