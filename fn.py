from flask import Flask, render_template, g
import mysql.connector
from python_mysql_dbconfig import read_db_config

app = Flask(__name__)
app.config.from_object(__name__)


@app.before_request
def before_request():
    db_config = read_db_config()
    g.cnx = mysql.connector.MySQLConnection(**db_config)


@app.route('/')
def show_entries():
    sql_select_entries = "select title, short_intro, url.url, page_id, source_name, published_date from " \
                         "ws_news n, ws_url url, ws_scraping_history sh, ws_sources s " \
                         "where n.page_id = url.id " \
                         "and url.source_id = s.id " \
                         "and url.run_id = sh.id " \
                         "and sh.latest_flag is NULL order by page_id desc"

    cursor = g.cnx.cursor()
    cursor.execute(sql_select_entries)
    entries = [dict(title=row[0], short_intro=row[1], url=row[2], source_name=row[4]) for row in cursor.fetchall()]
    return render_template('show_entries.html', entries=entries)


@app.route('/<subcat>')
def show_subcat(subcat):
    sql_select_entries = "select title, short_intro, url.url, page_id, source_name, published_date from " \
                         "ws_news n, ws_url url, ws_scraping_history sh, ws_sources s " \
                         "where n.page_id = url.id " \
                         "and url.source_id = s.id " \
                         "and url.run_id = sh.id " \
                         "and url.url like %(subcat)s " \
                         "order by page_id desc"
    cursor = g.cnx.cursor()
    cursor.execute(sql_select_entries, {'subcat': '%' + subcat + '%'})
    entries = [dict(title=row[0], short_intro=row[1], url=row[2], source_name=row[4]) for row in cursor.fetchall()]
    #return cursor.statement
    return render_template('show_entries.html', entries=entries)


if __name__ == "__main__":
    app.run(debug=True)