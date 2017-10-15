import re
import requests
import pymysql.cursors

class DBM:
    def __init__(self):
        self.starturl = "https://movie.douban.com/top250"
        self.exurl = "?start="
        self.List = []
    def gethtml(self,url):
        html = requests.get(url).content.decode('utf-8')
        return html

    def getList(self):
        for i in range(10):
            url = self.starturl+self.exurl+str(i*25)
            buf = self.gethtml(url)
            self.findMovie(buf)


    # .*?<span class="inq">(.*?)</span>  找评论的时候有的上一条没有评论这个标签，导致匹配到了下一条的评论，暂时无法解决。
    # 可以分开来匹配。
    def findMovie(self,string):
        pattern = re.compile(r'<div class="hd">.*?<span class="title">(.*?)</span>.*?<span class="other">(.*?)</span>.*?<p class="">(.*?)</p>.*?<span class="rating_num".*?>(.*?)</span>',re.S)
        content = re.findall(pattern,string)
        for m in content:
            replacenbsp = re.compile(r'&nbsp;', re.S)
            replacenbbr = re.compile(r'<br>', re.S)
            text1 = re.sub(replacenbsp, " ", m[1])
            text2 = re.sub(replacenbbr, "", m[2])
            text3 = re.sub(replacenbsp, " ", text2)
            self.List.append([m[0].strip(), text1.strip(), text3.strip(), m[3]])

    def insertDB(self):

        for i in self.List:
            # 每次都要连接数据库才行
            conn = pymysql.connect(
                host='127.0.0.1',
                port=3306,
                user='root',
                passwd='',
                db='dbmovie250',
                charset='utf8'
            )
            try:
                with conn.cursor() as cursor:
                    sql = "insert into movie (moviename,other,men,rate) VALUES (%s,%s,%s,%s)"
                    cursor.execute(sql,(i[0],i[1],i[2],i[3]))
                    conn.commit()
            finally:
                conn.close()

    def start(self):
        self.getList()
        self.insertDB()

        # r'<div class="hd">.*?<span class="title">(.*?)</span>.*?<span class="other">(.*?)</span></a>.*?<div class="bd>.*?<p class="">(.*?)</p>.*?<span class="rating_num".*?>(.*?)</span>.*?<span class="inq">(.*?)</span>'
    # L = []
    # buf = requests.get(url).content.decode()
    # pattern1 = re.compile(r'<div class="hd">.*?<span class="title">(.*?)</span>.*?<span class="other">(.*?)</span>.*?<p class="">(.*?)</p>.*?<span class="rating_num".*?>(.*?)</span>.*?<span class="inq">(.*?)</span>',re.S)
    # moviename = re.findall(pattern1,buf)
    #
    #
    # for m in moviename:
    #     replacenbsp = re.compile(r'&nbsp;',re.S)
    #     replacenbbr = re.compile(r'<br>',re.S)
    #     text1 = re.sub(replacenbsp," ",m[1])
    #     text2 = re.sub(replacenbbr,"",m[2])
    #     text3 = re.sub(replacenbsp," ",text2)
    #     L.append([m[0].strip(),text1.strip(),text3.strip(),m[3],m[4]])
    #     # 电影名字，又名，导演 时间和类型，评分，简介
    # print(L)

s = DBM()
s.start()