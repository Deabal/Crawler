import pymysql
import requests
from lxml import etree
import time
import re


class JZMSpider:
    def __init__(self):
        self.url = "http://www.juzimi.com/totallike"
        self.header= {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"}
        self.dblist =[]
    def onePage(self,url):
        buf1 = requests.get(url, headers=self.header).content.decode()

        # 把每一段标签分开，为了处理特殊的段落（没有作者或者来源的）
        patbuf = re.compile(r'<div class="views-row views-row-\d(.*?)<div class="views-field-field-addtoalbum-value">',
                            re.S)
        buf2 = re.findall(patbuf, buf1)
        for buf in buf2:
            # 匹配句子
            patternSentence = re.compile(r'<a href=.*?class="xlistju">(.*?)</a>', re.S)

            # 匹配作者（有可能没有）
            patternAuthor = re.compile(r'.*?<div class="xqjulistwafo">.*?oriwriter-value">(.*?)</a>', re.S)

            # 匹配来源（有可能没有）
            patternWhere = re.compile(r'<span class="views-field-field-oriarticle-value">.*?>(.*?)</a>', re.S)

            # 匹配赞数
            patternlike = re.compile(r'.title="喜欢本句">(.*?)</a>', re.S)

            # 句子格式整理
            sentence = re.findall(patternSentence, buf)[0].replace('<br/>', '').replace('\r', '\n')
            try:
                author = re.findall(patternAuthor, buf)[0]
            except:
                author = None
            try:
                where = re.findall(patternWhere, buf)[0]
            except Exception as e:
                where = None
            like = re.findall(patternlike, buf)[0].strip('喜欢()')

            self.dblist.append([sentence, author, where, like])

    def allPage(self):
        for x in range(50):
            url = self.url+'?page='+str(x)
            self.onePage(url)

    def saveToDB(self):
        for i in self.dblist:
            # 每次都要连接数据库才行
            conn = pymysql.connect(
                host='127.0.0.1',
                port=3306,
                user='root',
                passwd='123456',
                db='juzimi',
                charset='utf8'
            )
            try:
                with conn.cursor() as cursor:
                    sql = "insert into jzmtotal (sentence,author,wherefrom,likes) VALUES (%s,%s,%s,%s)"
                    cursor.execute(sql, (i[0], i[1], i[2], i[3]))
                    conn.commit()
            except Exception as e:
                print(e)
            finally:
                conn.close()

if __name__ == '__main__':
    jzm = JZMSpider()
    jzm.allPage()
    jzm.saveToDB()
