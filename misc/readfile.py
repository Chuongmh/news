from os import walk
from xml.dom import minidom
import os, datetime
import sys
from urllib import urlopen
from bs4 import BeautifulSoup
import mysql.connector
from python_mysql_dbconfig import read_db_config


logpath = '/home/chuong/Downloads/Log/before/'
html_file = logpath + '_index.htm'
file_name = "20160223before"

try:
    html = urlopen(html_file)
except:
    print("URL Open: " + sys.exc_info())
print("Start time: {0}".format(datetime.datetime.now()))
try:
    bsObj = BeautifulSoup(html, "html.parser")
except:
    print("BeautifulSoup: " + sys.exc_info())

rs = []
rows = bsObj.find_all("tr")
for row in rows:
    if row.contents[4].string.find("hr-qas.nsrp.com.vn") != -1:
        # file_name, raw_file, id, Result, protocol, host, url
        rs.append((file_name, logpath + row.contents[0].contents[4].attrs['href'].replace("\\", "/"),
                row.contents[1].string, row.contents[2].string, row.contents[3].string, row.contents[4].string,
                row.contents[5].string))

sql_insert_article = "insert into fiddler_trace_header (file_name, raw_file, id, Result, protocol, host, url) " \
                     "values (%s, %s, %s, %s, %s, %s, %s)"

db_config = read_db_config()
cnx = mysql.connector.MySQLConnection(**db_config)
cursor = cnx.cursor()

for r in rs:
    z = (unicode(r[0]), unicode(r[1]), unicode(r[2]), unicode(r[3]), unicode(r[4]), unicode(r[5]), unicode(r[6]))

    try:
        cursor.execute(sql_insert_article, z)
    except:
        print r[0], r[1],r[2],r[3],r[4],r[5],r[6]
        print("Insert: {}".format(sys.exc_info()))

cnx.commit()
cursor.close()
cnx.close()
print("End time: {0}".format(datetime.datetime.now()))