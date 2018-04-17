import requests
import re
import math
import pymysql.cursors

class BookCrawler:
    def __init__(self):
        self.url = "http://www.youlu.net/classify/"
        self.buf = None
        self.booklist = [] # 有分类的列表
        self.booklist2 = [] # 无分类的列表
        self.bookNum = []
        self.urlList = []
        self.bookurls = None
        # self.user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36"
        # self.headers = {'User-Agent': self.user_agent}

    def crawlbuf(self):
        patterna = re.compile(r'div id="classifyDefaultRight">.*?</ul>', re.S)
        # 图书分类列表（分块匹配）
        patternall = re.compile(r'<li>.*?</li>', re.S)

        buf1 = requests.get(self.url).content.decode()
        all = str(re.findall(patterna, buf1))
        self.buf = re.findall(patternall, all)


    def getBooknum_List_Url(self):
        # 图书总数
        patternBookNum = re.compile(r'<span class="bookCount">\((.*?)\)</span>', re.S)
        # 图书匹配
        patternbook = re.compile(r'<a href="/classify/.*?">(.*?)</a>')
        # 链接匹配
        patternUrl = re.compile(r'<a href="(.*?)">')

        for i in self.buf:
            url1 = []
            book = re.findall(patternbook, i)
            # 带有图书种类（在第一条）的list
            self.booklist.append([book[0], book[1:]])
            # 不带图书种类的list
            self.booklist2.append(book[1:])
            bNum = re.findall(patternBookNum, i)
            self.bookNum.append(bNum)
            bUrl1 = re.findall(patternUrl, i)
            for i in bUrl1:
                bUrl = 'http://www.youlu.net' + i
                url1.append(bUrl)
            self.urlList.append(url1[1:])

        # print(self.urlList)
        # print(self.booklist2)
        # print(self.bookNum)


    def getBookList(self):
        # 获取列表的图书网址
        list1 = []
        # bookNum2 = []
        # # 把图书数量列表处理成平面列表
        # for m in self.bookNum:
        #     bookNum2+=m

        for i in range(len(self.booklist2)):
            list2 = list(zip(self.booklist2[i], self.urlList[i],self.bookNum[i]))
            list1 += list2

        self.bookurls = list1


    def getBookCatorgory(self):
        pass

    def getAllBook(self):
        for i in self.bookurls[0:]:
            page = 1
            while(page<int(math.ceil(int(i[2])/20.0))):
                html = i[1].replace('1.html',(str(page)+'.html'))
                print(self.getBook(html,i[0]))
                # self.insetDB(self.getBook(html,i[0]))
                page+=1

            # print(i[0],i[1],i[2])


    def getBook(self,pageHtml,catorg):
        books = None
        list1 = []
        list2 = []
        binfo = None
        buf = requests.get(pageHtml).content.decode()
        patternBook = re.compile(r'<div class="bName".*?"_blank">(.*?)</a>.*?<div class="bMore">(.*?)</div>',re.S)
        books = re.findall(patternBook,buf)
        for b in books:
            list1.append(list(b))
        for bb in list1:
            try:
                bname = bb[0].replace('（内容一致，印次、封面或原价不同，统一售价，随机发货）','')
                binfo = bb[1].replace('\n','')
                bauthor = binfo.split('/')[0]
                bpublish = binfo.split('/')[1]
                byear = binfo.split('/')[2]
                bpages = binfo.split('/')[3]
                try:
                    bweight = binfo.split('/')[4]
                except IndexError:
                    bweight = ''
                list2.append([bname,bauthor,bpublish,byear,bpages,bweight,catorg])
            except Exception as e:
                print(pageHtml)
                print(e)
                continue
        # print(list2)
        return list2


    def insetDB(self,booklist):
        for i in booklist:
            conn = pymysql.connect(
                host='localhost',
                port=3306,
                user='root',
                passwd='',
                db='books',
                charset='utf8'
            )
            try:
                with conn.cursor() as cursor:
                    sql = "insert into books (书名,作者,出版社,出版日期,页数,重量,类目) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                    cursor.execute(sql,(i[0],i[1],i[2],i[3],i[4],i[5],i[6]))
                    conn.commit()
            except Exception as e:
                print(e)
                continue
            finally:
                conn.close()



a = BookCrawler()
a.crawlbuf()
a.getBooknum_List_Url()
a.getBookList()
a.getAllBook()

# a.getBook('http://www.youlu.net/classify/2-0101-4037-8.html','')

















