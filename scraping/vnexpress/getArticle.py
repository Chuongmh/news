from urllib import urlopen
from bs4 import BeautifulSoup
from urllib2 import HTTPError
import mysql.connector
import datetime
from python_mysql_dbconfig import read_db_config
import sys
from scraping.log import log


db_config = read_db_config()
cnx = mysql.connector.MySQLConnection(**db_config)
cursor = cnx.cursor()
source_id = -1
run_id = -1
page_ids = set([])


def insertArticle(article):
    sql_insert_article = "insert into ws_news (page_id, title, short_intro, news_detail, published_date, " \
                         "published_by) values (%s, %s, %s, %s, %s, %s)"
    data_insert_article = (article[0], article[1], article[2], article[3], article[4], article[5])

    try:
        cursor.execute(sql_insert_article, data_insert_article)
        cnx.commit()
    except:
        print("Exception: {0}".format(sys.exc_info()))


def parseArticle(page_id):
    article = ["", "", "", "", "", "", ""]
    sql_select_url = "select url from ws_url where id = %(page_id)s"
    cursor.execute(sql_select_url, {'page_id' : page_id})
    row = cursor.fetchone()
    if cursor.rowcount <= 0:
        print("Error: Invalid Page ID")
        return
    else:
        url = row[0]

    try:
        html = urlopen(url)
    except IOError as err:
        print(err.message)
    except:
        print("Unexpected Error: {0}".format(sys.exc_info()))

    try:
        bsObj = BeautifulSoup(html)
        article[0] = page_id
        article[1] = bsObj.h1.text
        article[2] = bsObj.find("div", class_="short_intro txt_666").text.strip()
        article[3] = ""
        detail = bsObj.find("div", class_="fck_detail width_common")
        bsDetail = BeautifulSoup(str(detail))

        for each_div in bsDetail.find_all("p", class_="Normal"):
            article[3] = article[3] + each_div.text

        for each_div in bsObj.find_all("div", class_="block_timer left txt_666"):
            if each_div.text is None:
                pass
            else:
                article[4] = each_div.text.strip()
        article[5] = bsObj.strong.text
        article[6] = datetime.datetime.now()
        #print article[6]

        insertArticle(article)
    except HTTPError as err:
        print("HTTPError: {0}".format(err.message))
    except AttributeError as err:
        #print("AttributeError: {}".format(err.message))
        log.log(source_id=source_id,run_id=run_id,unique_id=page_id,error_code='AttributeError',
                error_message=err.message,cnx=cnx,cursor=cursor)
    except UnboundLocalError as err:
        log.log(source_id=source_id,run_id=run_id,unique_id=page_id,error_code='UnboundLocalError',
                error_message=err.message,cnx=cnx,cursor=cursor)
    except:
        print("Unexpected Error: {0}".format(sys.exc_info()))


def parseArticles():
    global source_id
    global run_id
    sql_select_source = "select id from ws_sources where source_code = %(source_code)s"
    cursor.execute(sql_select_source, {'source_code': 'VNE'})
    row = cursor.fetchone()
    if cursor.rowcount <= 0:
        print("Unexpected Error: {0}".format(sys.exc_info()))
        return
    else:
        source_id = row[0]

    sql_select_runid = "select id from ws_scraping_history where source_id = %(sid)s and latest_flag is null"
    cursor.execute(sql_select_runid, {'sid': source_id})
    row = cursor.fetchone()
    if cursor.rowcount <= 0:
        print("Unexpected Error: {0}".format(sys.exc_info()))
        return
    else:
        run_id = row[0]

    sql_select_page = "select id from ws_url where source_id = %s and run_id = %s"
    cursor.execute(sql_select_page, (source_id, run_id))
    rows = cursor.fetchall()

    for row in rows:
        parseArticle(row[0])
        #print(row[0])



#parseArticle(3923)
print("VNE Start time: {0}".format(datetime.datetime.now()))
parseArticles()
print("VNE End time: {0}".format(datetime.datetime.now()))