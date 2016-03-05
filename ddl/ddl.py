import mysql.connector
from mysql.connector import errorcode
from python_mysql_dbconfig import read_db_config


DB_NAME = "test"

TABLES = {}

TABLES["ws_url"] = (
    "CREATE TABLE ws_url ("
    "   id bigint(7) not null auto_increment,"
    "   source_id bigint(7),"
    "   url varchar(200),"
    "   run_id bigint,"
    "   created timestamp DEFAULT current_timestamp,"
    "   PRIMARY KEY (id)) ENGINE=InnoDB")

TABLES["tmp_ws_url"] = (
    "CREATE TABLE tmp_ws_url ("
    "   id bigint(7) not null auto_increment,"
    "   source_id bigint(7),"
    "   url varchar(200),"
    "   run_id bigint,"
    "   created timestamp DEFAULT current_timestamp,"
    "   PRIMARY KEY (id)) ENGINE=InnoDB")

TABLES["ws_page_link"] = (
    "CREATE TABLE ws_page_link ("
    "   id bigint(7) not null auto_increment,"
    "   fromPageID bigint(7),"
    "   toPageID bigint(7),"
    "   run_id bigint(7),"
    "   creation_date timestamp DEFAULT current_timestamp,"
    "   PRIMARY KEY (id)) ENGINE=InnoDB")

TABLES["ws_sources"] = (
    "CREATE TABLE ws_sources ("
    "   id bigint(7) not null auto_increment,"
    "   source_code varchar(20),"
    "   source_name varchar(200),"
    "   is_latest varchar(1),"
    "   creation_date timestamp DEFAULT current_timestamp,"
    "   PRIMARY KEY (id)) ENGINE=InnoDB")

TABLES["ws_scraping_history"] = (
    "CREATE TABLE ws_scraping_history ("
    "   id bigint(7) not null auto_increment,"
    "   source_id bigint(7),"
    "   start_time timestamp,"
    "   end_time timestamp,"
    "   status varchar(10),"
    "   latest_flag varchar(2),"
    "   PRIMARY KEY (id)) ENGINE=InnoDB")

TABLES["ws_news"] = (
    "CREATE TABLE ws_news ("
    "   id bigint(7) not null auto_increment,"
    "   page_id bigint(7),"
    "   title nvarchar(400),"
    "   short_intro nvarchar(1000),"
    "   news_detail nvarchar(40000),"
    "   published_date nvarchar(40),"
    "   published_by nvarchar(100),"
    "   creation_date timestamp DEFAULT current_timestamp,"
    "   PRIMARY KEY (id)) ENGINE=InnoDB")

TABLES["ws_log"] = (
    "CREATE TABLE ws_log ("
    "   id bigint(7) not null auto_increment,"
    "   source_id bigint(7),"
    "   run_id bigint(7),"
    "   unique_id bigint(7),"
    "   error_code varchar(20),"
    "   error_message varchar(200),"
    "   creation_date datetime,"
    "   PRIMARY KEY (id)) ENGINE=InnoDB")

db_config = read_db_config()
cnx = mysql.connector.MySQLConnection(**db_config)
cursor = cnx.cursor()


def database_name():
    return DB_NAME


def create_database(cursor):
    try:
        cursor.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

try:
    cnx.database = DB_NAME
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        cnx._database = DB_NAME
    else:
        print("err")
        exit(1)

for name, ddl in TABLES.iteritems():
    try:
        print("Creating table {}: ".format(name))
        print(ddl)
        cursor.execute(ddl)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Already exists")
        else:
            print(err.message)
    else:
        print("OK")

cursor.close()
cnx.close()
