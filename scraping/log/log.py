import mysql.connector
import datetime

LOG_ENABLE = True


def log(source_id, run_id, unique_id, error_code, error_message, cnx, cursor):
    if LOG_ENABLE:
        sql_insert_log = "Insert into ws_log (source_id, run_id, unique_id, error_code, error_message, creation_date)" \
                         " values (%s, %s, %s, %s, %s, %s)"
        data_insert_log = (source_id, run_id, unique_id, error_code, error_message, datetime.datetime.now())
        cursor.execute(sql_insert_log, data_insert_log)
        cnx.commit()