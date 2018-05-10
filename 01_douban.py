# 导入模块
import urllib.request  # 网页代码抓取
import re  # 正则表达式
import pymysql  # 数据库
import time  # 时间
from selenium import webdriver  # 动态网页抓取
import random  # 随机数


# 插入数据
# insert_data(用户名，推荐等级，评论内容，电影编号，评分，（不重要，后面另说）)
def insert_data(username, comment_type, comment, movie_id, movie_name, grade):
    # 链接数据库 参数你慢慢记吧。。。
    # 链接数据库 connect方法 传入参数有 host：本机  port：端口  database:数据库名  user：登录名 password：登录密码
    # 前提是你要在数据库中先建立好库
    movies_db = pymysql.connect(host='localhost', port=3306, database='movies', user='root', password='gmhGMH123',
                                charset='utf8')
    # 设置游标（不重要 记住就行 执行必备的流程）
    cursor = movies_db.cursor()
    # 插入语句
    # sql语句 将sql语句写在一个字符串内 直接整体传给cusror.execute(str)方法 ，让该方法自己执行sql
    # insert 语句 插入新数据
    # 用法：insert into 表名(列1，列2，....) values （值1，值2，......）
    sql_insert = "INSERT INTO douban(username,star,comment,movie_id,movie_name,grade) VALUES ('%s','%s','%s','%s','%s','%f')" % (
        username, comment_type, comment, movie_id, movie_name, grade)
    # 使用try except语句捕获异常
    # 如果那组数据有问题 不予处理 不予报错 继续执行 保证程序稳定
    try:
        # 执行sql语句
        cursor.execute(sql_insert)
        movies_db.commit()
    except:  # ps:except不推荐这样直接用
        movies_db.rollback()
    # 关闭数据库连接
    movies_db.close()


# 选取电影地址
# 原理 https://movie.douban.com/subject/26945085/?tag=%E7%83%AD%E9%97%A8&from=gaia 这是电影的网站，
# 可以看到区别在于中间的电影编号，所以我们的目标是在热门电影的页面中抓取所有热门电影的编号，问题在于
# 现在的部分网站，使用ajax，js等技术动态刷新页面，普通方式无法抓取我们需要的编号。
def catch_movie_url(url):
    # 所以我们引入selenium模块中的webdriver方法 新建一个网页并等待一段时间之后再进行抓取，作用是保证所有的界面都刷新完毕
    # 才进行抓取
    # 主流浏览器是火狐和chorme此处我们选取chorme做为浏览器 下载chormedriver.exe放在浏览器的安装目录才可调用
    chorme_path = "C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
    # webdriver.Chrome()方法执行的路径是chrome_path
    driver = webdriver.Chrome(executable_path=chorme_path)
    # get方法抓取网页源代码
    # 此处会打开一个网页
    driver.get(url)
    # 系统等待十秒，等待网页加载完全
    time.sleep(10)
    # 正则表达式 re.findall()方法将正则结果放入一个列表movie_ids
    movie_ids = re.findall(r'data-id="(.*)">', driver.page_source)
    # 获取电影名及评分
    movie_names = re.findall(r'alt="(.*)" data-x', driver.page_source)
    movie_grades = re.findall(r'<strong>(\d.\d)</strong>', driver.page_source)
    movie_names.pop()
    # 返回movie_ids列表等待使用
    return movie_ids, movie_names, movie_grades
    # 方法结束


# 抓取网页内容
# 目标：从指定电影网页中抓取网页源代码
# 此时网页是静态的 故使用简单的urllib包中的requset方法直接获取
def catch_content(movie_url):
    page = urllib.request.urlopen(movie_url)
    # page是网页抓取的结果，只有调用了read（）方法才能读出源代码
    # 源代码格式并不是标准html语言，故需要decode方法解码防止乱码 因为是中文网站故我们选择utf-8字符集转码
    content = page.read().decode('utf-8')
    # 正则表达式 作用：网页源码不会识别换行符，会以\n直接输出，所以我们将文本中的\n转化为转义\n是代码更美观
    # re.sub("需要的改变的内容"，"替换的内容"，"网页源码内容")
    settle_content = re.sub(r"\n", "\n", content)
    # 返回处理过之后的源码 可读性更强 方便下一步操作
    return settle_content
    # 此方法结束


# 接下来的目标 就是从上一步中的源码中提取我们需要的内容
# 专业操作名：数据清洗
# 实现方法：正则表达式
# 评论用户的用户名
def catch_name(settle_content):
    # 新建一个空列表用来存储所有评论用户的昵称
    user_list = []
    # 找出名字所在行
    user_name = re.findall(r"<a title=.* href", settle_content)
    # 从行中进一步找出昵称,并加入列表
    for username in user_name:
        username = re.search(r"\".*\"", username).group()
        username = re.sub(r"[\"]", "", username)
        user_list.append(username)
    return user_list


# 推荐程度
# 同上
def catch_stars(settle_content):
    stars_list = []
    # print(settle_content)
    stars = re.findall(r'看过</span>\n(.*)', settle_content)
    for star in stars:
        star = re.search(r'title=.*\"', star).group()
        star = re.search(r"\".*\"", star).group()
        star = re.sub(r"\"", "", star)
        if "-" not in star:
            stars_list.append(star)
        else:
            str1 = "未评分"
            stars_list.append(str1)
    return stars_list


# 评论内容
# 同上
def catch_comment(settle_content):
    comment_list = []
    comments = re.findall(r'<p class="">.*', settle_content)  # 管式数据清洗法1 强行正则表达式 找出内容所在的标签
    for comment in comments:
        comment = re.search(r">.*", comment).group()  # 管式数据清洗法2 强行正则表达式 找出内容（内容在双引号之中）
        comment = re.sub(r"[>]", "", comment)  # 管式数据清洗法3 强行正则表达式 去掉双引号剩下的就是需要的数据
        # comment = re.search(r"[\w\s\d\"\':!.,?\-()\[\]{}，。？（）【】｛｝+、*/]*", comment).group() # 不要脸版强行清洗
        comment_list.append(comment)  # 管式数据清洗法 强行append 把需要的数据放在列表中
    return comment_list


# def movie(id, name, grade):
#     movie = (id, name, grade)
#     return movie


def main():
    # 主流程/逻辑
    # 第一步 将热门电影页的网址传入方法catch_movie_url()得到ids的列表
    # def 方法名(参数)：
    #  操做
    movie_ids, movie_names, movie_grades = catch_movie_url(
        "https://movie.douban.com/explore#!type=movie&tag=%E7%83%AD%E9%97%A8&sort=recommend&page_limit=20&page_start=0")
    # for in 方法 依次提取列表里的每一条数据
    movies = []
    # movies = [(1_id,1_name,1_grade),(2_id,2_name,2_grade),.......]
    for i in range(0, 20):
        # 列表[1]
        # tuple = (第一个电影的ｉｄ，第一个电影的名字，第一个电影的频分)
        movie = (movie_ids[i], movie_names[i], movie_grades[i])
        movies.append(movie)
    for movie_info in movies:
        # tuple[index]
        id = movie_info[0]
        name = movie_info[1]
        grade = float(movie_info[2])
        # 显示进度
        print("正在处理：第%s号电影" % id)
        # 此处时为了抓取评分
        page = 1
        while page <= 2:  # 抓取前2页的评论
            nums = (page - 1) * 20
            target_url = "https://movie.douban.com/subject/" + id + "/comments?start=" + str(
                nums) + "&limit=20&sort=new_score&status=P&percent_type="
            settle_content = catch_content(target_url)
            i = 0
            while i < 20:
                # list[index]
                # list = [1,2,3]
                # print(list[0])
                username = catch_name(settle_content)[i]
                comment_type = catch_stars(settle_content)[i]
                comment = catch_comment(settle_content)[i]
                insert_data(username, comment_type, comment, id, name, grade)
                i += 1
            page += 1


if __name__ == '__main__':
    main()
