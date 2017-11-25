"""
filter source data db and populate card table
"""
import pandas as pd
import pandas.io.sql as pd_sql
import sqlite3 as sql
from datetime import datetime


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def filter_by(cur, table, condition):
    # script = "SELECT * FROM shl WHERE " + field + " " + operator + " \"" + value + "\""
    script = "SELECT * FROM " + table + " WHERE " + condition + " order by id"
    print(script)
    return cur.execute(script).fetchall()


# filter data from source table
def search_card_from_src_db(table_name, condition, filter_str):

    db_name = "./app.db"
    conn = sql.connect(db_name)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    data = filter_by(cur, table_name, condition)  # "%" + filter_str + "%")

    # insert into cards table in cards db
    cards = []
    body = ""
    count = 1
    for d in data:
        if table_name == "医学衷中参西录":
            body = str('<pre style="white-space:pre-wrap"><b>' + d.get("details") + "<br><br></pre>")
            cards.append((filter_str + " " + str(count) + "   - " + table_name, body, body, datetime.utcnow()))
            count += 1
            body = ""
        else:
            body += str('<pre style="white-space:pre-wrap"><b>' + str(d.get("id")) + "</b> " + d.get("details") + "<br><br></pre>")
    if body != "":
        cards.append((filter_str + "   - " + table_name, body, body, datetime.utcnow()))
    for card in cards:
        try:
            script = "select count(*) from cards where title='%s'" % card[0]
            # print(script)
            count = cur.execute(script).fetchall()
            if count[0]['count(*)'] == 0:
                script = "insert into cards (title, body, body_html, last_modified_on) values(?,?, ?,?)"

                cur.execute(script, card)
            else:
                script = "update cards set body='%s', body_html='%s' last_modified_on='%s' where title='%s'" % (card[1], card[2], datetime.utcnow(), card[0])
                cur.execute(script)
        except Exception as e:
            print(e)
        finally:
            conn.commit()
    conn.close()
