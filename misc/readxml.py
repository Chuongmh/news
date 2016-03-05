import xml.dom.minidom as minidom
import time, datetime
import mysql.connector
from python_mysql_dbconfig import read_db_config
import sys

# file_name = "/home/chuong/Downloads/Log/raw/00746_m.xml"
rows = []
db_config = read_db_config()
cnx = mysql.connector.MySQLConnection(**db_config)
cursor = cnx.cursor()
g_run_name = "20160223before"


def readfile(file_name):
    doc = minidom.parse(file_name)
    sessionElem = doc.getElementsByTagName("Session")[0]
    session_id = sessionElem.getAttribute("SID")

    stimerElem = doc.getElementsByTagName("SessionTimers")[0]

    FiddlerBeginRequest = stimerElem.getAttribute("FiddlerBeginRequest").replace('T', ' ')
    FiddlerBeginRequest = unicode(FiddlerBeginRequest[:(len(FiddlerBeginRequest)-7)])
    # print FiddlerBeginRequest

    start_time = datetime.datetime.strptime(FiddlerBeginRequest, "%Y-%m-%d %H:%M:%S.%f")

    ClientDoneResponse = stimerElem.getAttribute("ClientDoneResponse").replace('T', ' ')
    ClientDoneResponse = unicode(ClientDoneResponse[:(len(ClientDoneResponse)-7)])
    # print ClientDoneResponse

    end_time = datetime.datetime.strptime(ClientDoneResponse, "%Y-%m-%d %H:%M:%S.%f")

    total_time = (end_time - start_time).total_seconds()
    rows.append((g_run_name, session_id, FiddlerBeginRequest, ClientDoneResponse, total_time))
    """
    r = (file_name, session_id, FiddlerBeginRequest, ClientDoneResponse, total_time)
    sql_insert_time = "insert into fiddler_parsed_data (file_name, id, FiddlerBeginRequest, ClientDoneResponse, " \
                      "Total_time) values (%s, %d,  %s, %s, %d)"
    try:
        cursor.execute(sql_insert_time, r)
        cnx.commit()
    except:
        print("Run: {}".format(sys.exc_info()))
    """


def run(run_name):
    sql_select_header = "select t.raw_file from fiddler_trace_header t where t.file_name = %(file_name)s"
    cursor.execute(sql_select_header, {'file_name': run_name})
    raws = cursor.fetchall()
    for raw in raws:
        readfile(raw[0])

    sql_insert_time = "insert into fiddler_parsed_data (file_name, id, FiddlerBeginRequest, ClientDoneResponse, " \
                      "Total_time) values (%s, %s,  %s, %s, %s)"
    try:
        cursor.executemany(sql_insert_time, rows)
        cnx.commit()
    except:
        print("Run: {}".format(sys.exc_info()))

print("Start time: {0}".format(datetime.datetime.now()))
run(g_run_name)
print("End time: {0}".format(datetime.datetime.now()))