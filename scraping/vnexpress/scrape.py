import threading
import Queue
from urllib import urlopen
from urlparse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
import hashlib
import sys
import re
import datetime
from mysql.connector import MySQLConnection
from python_mysql_dbconfig import read_db_config

run_id = -1
source_id = -1
g_URLsDict = dict()
g_link_limit = 200

db_config = read_db_config()
cnx = MySQLConnection(**db_config)
cursor = cnx.cursor()


class Crawler(threading.Thread):
    global g_URLsDict
    varLock = threading.Lock()
    count = 0

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        # self.url = self.queue.get()
        # self.links = []

    def getLinks(self, url):
        try:
            html = urlopen(url)
        except IOError as err:
            print("getLinks openurl: {}".format(err.message))
            return

        try:
            bsObj = BeautifulSoup(html, "html.parser")
            links = bsObj.findAll("a", href=re.compile("(?! mailto)$"))
            tmp = []
            for link in links:
                if 'href' in link.attrs:
                    new_url = urljoin(url, link.attrs['href'])
                    t = list(urlparse(new_url))
                    t[3:6] = ['', '', '']
                    new_url = urlunparse(t)
                    if (urlparse(new_url).netloc.find(urlparse(url).netloc)) != -1:
                        tmp.append(new_url)
            return tmp
        except:
            print("getLinks BeautifulSoup: {}".format(sys.exc_info()))

    def run(self):
        while 1:
            print self.getName() + " started"
            url = self.queue.get()
            # print url
            links = self.getLinks(url)
            # print links
            # """
            for link in links:
                fp = hashlib.sha1(link).hexdigest()
                Crawler.varLock.acquire()
                if fp in g_URLsDict:
                    Crawler.varLock.release()
                else:
                    Crawler.count += 1
                    g_URLsDict[fp] = link
                    Crawler.varLock.release()
                    if Crawler.count < g_link_limit:
                        self.queue.put(link)
            self.queue.task_done()


def insert_scraping_history(source_code):
    global source_id
    sql_select_source = "select * from ws_sources where source_code = %(source_code)s"
    sql_update_latest = "update ws_scraping_history set latest_flag = 'Y' where latest_flag is null " \
                        "and source_id = %(source_id)s"
    sql_insert_history = "insert into ws_scraping_history (source_id, start_time, end_time, status) values " \
                         "(%(source_id)s, %(start_time)s, %(end_time)s, %(status)s)"

    # Get Source ID
    cursor.execute(sql_select_source, {'source_code': source_code})
    row = cursor.fetchall()

    if cursor.rowcount > 0:
        source_id = row[0][0]
    else:
        source_id = -1

    cursor.execute(sql_update_latest, {"source_id": source_id})
    cnx.commit()

    start_time = datetime.datetime.now()
    data_insert_history = {
        'source_id': source_id,
        'start_time': start_time,
        'end_time': None,
        'status': 'In Process'
    }
    cursor.execute(sql_insert_history, data_insert_history)
    cnx.commit()
    return cursor.lastrowid


def update_scraping_history(run_id, status):
    print("Updating Scraping History")
    sql_update_history = "update ws_scraping_history set status = %s, end_time = %s where id = %s"
    end_time = datetime.datetime.now()
    cursor.execute(sql_update_history, (status, end_time, run_id))
    cnx.commit()


def insert_pages(urls):
    sql_insert_url = "insert into tmp_ws_url (source_id, run_id, url) values (%s, %s, %s)"
    try:
        cursor.executemany(sql_insert_url, urls)
        cnx.commit()
    except:
        print("Insert Page: {}".format(sys.exc_info()))


def load_to_table(p_run_id):
    print("Loading to Actual Table")
    try:
        cursor.callproc('insert_pages', [p_run_id])
        cnx.commit()
    except:
        print("Load to table: {}".format(sys.exc_info()))


def run():
    global run_id
    global source_id
    urls = []
    stime = datetime.datetime.now()
    source = ["http://vnexpress.net"]
    run_id = insert_scraping_history('VNE')
    print(run_id)
    queue = Queue.Queue()

    for i in range(8):
        t = Crawler(queue)
        t.setDaemon(True)
        t.start()

    for s in source:
        queue.put(s)

    print("Joining...")
    queue.join()
    print("Joining Done")
    print(len(g_URLsDict))
    for value in g_URLsDict:
        urls.append((source_id, run_id, g_URLsDict[value]))
    print(len(urls))
    insert_pages(urls)
    update_scraping_history(run_id, 'Completed')
    load_to_table(run_id)
    print("End time: {0}".format(datetime.datetime.now()))
    etime = datetime.datetime.now()
    tdelta = etime - stime
    print("Running Time: {}".format(tdelta))

run()