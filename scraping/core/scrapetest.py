from urllib import urlopen
from bs4 import BeautifulSoup
from urllib2 import HTTPError
from urlparse import urlparse, urljoin, urlunparse
import urllib
import re
import mysql.connector
import datetime
from python_mysql_dbconfig import read_db_config

visitedPages = set()
run_id = -1
source_id = -1

db_config = read_db_config()
cnx = mysql.connector.MySQLConnection(**db_config)
cursor = cnx.cursor()


def insertScrapingHistory(source_code):
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


def updateScrapingHistory(run_id, status):
    sql_update_history = "update ws_scraping_history set status = %s, end_time = %s where id = %s"
    end_time = datetime.datetime.now()
    cursor.execute(sql_update_history, (status, end_time, run_id))
    cnx.commit()


def insertPageIfNotExists(url):
    global run_id
    global source_id
    sql_select_url = "select * from ws_url where url = %(url)s"
    sql_insert_url = "insert into ws_url (source_id, url, run_id) values (%(source_id)s, %(url)s, %(run_id)s)"
    cursor.execute(sql_select_url, {'url' : url})
    row = cursor.fetchall()

    if cursor.rowcount == 0:
        cursor.execute(sql_insert_url, {'source_id': source_id, 'url': url, 'run_id': run_id})
        cnx.commit()
        return cursor.lastrowid
    else:
        return row[0][0]


def insertlink(fromPageID, toPageID):
    global run_id
    sql_count_link = "select * from ws_page_link where fromPageID = %s and toPageID = %s"
    sql_insert_link = "insert into ws_page_link (fromPageID, toPageID, run_id) values (%s, %s, %s)"

    cursor.execute(sql_count_link, (fromPageID, toPageID))
    row = cursor.fetchall()
    if cursor.rowcount == 0:
        cursor.execute(sql_insert_link, (fromPageID, toPageID, run_id))
        cnx.commit()


def getLinks(url, recursionLevel):
    global visitedPages
    if recursionLevel > 2:
        return
    pageID = insertPageIfNotExists(url)

    try:
        html = urlopen(url)
    except IOError as err:
        print(err.message)
    except:
        print("Open URL: Unexpected Error")

    try:
        bsObj = BeautifulSoup(html)
        links = bsObj.findAll("a", href=re.compile("(?! mailto)$"))
        for link in links:
            if 'href' in link.attrs:
                new_url = urljoin(url, link.attrs['href'])
                t = list(urlparse(new_url))
                # Remove params, query, fragment
                t[3:6] = ['', '', '']
                new_url = urlunparse(t)
                if (urlparse(new_url).netloc.find(urlparse(url).netloc)) != -1:
                    insertlink(pageID, insertPageIfNotExists(new_url))
                    #new_id = insertPageIfNotExists(new_url)
                    #print(new_id)
                    if new_url not in visitedPages:
                        visitedPages.add(new_url)
                        getLinks(new_url, recursionLevel + 1)
    except:
        print("List link: Unexpected Error")


def run(url):
    global run_id
    print("Scraping start time: {0}".format(datetime.datetime.now()))
    run_id = insertScrapingHistory('VNE')
    getLinks(url, 0)
    updateScrapingHistory(run_id, 'Completed')
    print("Scraping end time: {0}".format(datetime.datetime.now()))


"""
url = "http://vnexpress.net"

print("Start time: {0}".format(datetime.datetime.now()))
run_id = insertScrapingHistory('VNE')
getLinks(url, 0)
updateScrapingHistory(run_id, 'Completed')
print("End time: {0}".format(datetime.datetime.now()))
#insertPageIfNotExists(url)
"""
if __name__ == "__main__":
    run("http://vnexpress.net")
    cnx.close()