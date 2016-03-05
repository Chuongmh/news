import threading
import Queue
from urllib import urlopen
from bs4 import BeautifulSoup
import sys
import mysql.connector
from python_mysql_dbconfig import read_db_config
import datetime

g_URLsDict = dict()
g_NewsDict = []
g_Error = []
db_config = read_db_config()
cnx = mysql.connector.MySQLConnection(**db_config)
cursor = cnx.cursor()


class Crawler(threading.Thread):
    global g_URLsDict
    global g_NewsDict
    global g_Error
    varLock = threading.Lock()

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while 1:
            print(self.getName() + " started")
            page_id = self.queue.get()
            url = g_URLsDict[page_id]
            # Start parsing
            try:
                html = urlopen(url)
            except:
                print("URLOpen Error: {0}".format(sys.exc_info()))

            try:
                bsObj = BeautifulSoup(html, "html.parser")
                # article[0] = page_id
                title = bsObj.h1.text
                short_intro = bsObj.find("div", class_="short_intro txt_666").text.strip()
                news_detail = ""
                detail = bsObj.find("div", class_="fck_detail width_common")
                bsDetail = BeautifulSoup(str(detail))
                for each_div in bsDetail.find_all("p", class_="Normal"):
                    news_detail = news_detail + each_div.text

                for each_div in bsObj.find_all("div", class_="block_timer left txt_666"):
                    if each_div.text is None:
                        pass
                    else:
                        published_date = each_div.text.strip()
                published_by = bsObj.strong.text
                Crawler.varLock.acquire()
                g_NewsDict.append((page_id, title, short_intro, news_detail, published_date, published_by))
                Crawler.varLock.release()
            except AttributeError as e:
                Crawler.varLock.acquire()
                g_Error.append(("AttributeError", e.message))
                Crawler.varLock.release()
            except:
                print("BS Error: {0}".format(sys.exc_info()))

            self.queue.task_done()


def insertArticle(article):
    sql_insert_article = "insert into ws_news (page_id, title, short_intro, news_detail, published_date, " \
                         "published_by) values (%s, %s, %s, %s, %s, %s)"
    try:
        cursor.executemany(sql_insert_article, article)
        cnx.commit()
    except:
        print("Exception: {0}".format(sys.exc_info()))


def run():
    stime = datetime.datetime.now()
    sql_get_url = "select u.id, u.url from ws_url u, ws_scraping_history sh, ws_sources s " \
                  "where u.run_id = sh.id " \
                  "and s.id = sh.source_id " \
                  "and s.source_code = 'VNE' " \
                  "and sh.latest_flag is null " \
                  "and sh.status = 'Completed'"

    queue = Queue.Queue()
    cursor.execute(sql_get_url)
    rows = cursor.fetchall()
    for row in rows:
        g_URLsDict[row[0]] = row[1]
        queue.put(row[0])
    print("g_URLsDict: ", len(g_URLsDict))

    for i in range(8):
        t = Crawler(queue)
        t.setDaemon(True)
        t.start()

    print("Joining...")
    queue.join()
    print("Joining Done")
    print("g_NewsDict: ", len(g_NewsDict))

    insertArticle(g_NewsDict)

    etime = datetime.datetime.now()
    tdelta = etime - stime
    print("Running Time: {}".format(tdelta))

run()