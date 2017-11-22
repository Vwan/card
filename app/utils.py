"""
filter source data db and populate card table
"""
import pandas as pd
import pandas.io.sql as pd_sql
import sqlite3 as sql


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def filter_by(cur, table, condition):
    # script = "SELECT * FROM shl WHERE " + field + " " + operator + " \"" + value + "\""
    script = "SELECT * FROM " + table + " WHERE " + condition
    return cur.execute(script).fetchall()


# filter data from source table
def search_card_from_src_db(db_name, condition, filter_str):
    conn = sql.connect(db_name)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    data1 = filter_by(cur,"shl", condition)  # "%" + filter_str + "%")
    data2 = filter_by(cur,"jgyl", condition)  # "%" + filter_str + "%")
    # insert into cards table in cards db
    body = ""
    for d in data1 + data2:
        body += str('<b>' + str(d.get("id")) + "</b> " + d.get("content") + "<br><br>")
        print("body is: ", body)

    body_html = body
    script = "insert into cards (title, body, body_html) values(?,?, ?)"
    cur.execute(script, (filter_str, body, body_html))
    conn.commit()
    conn.close()
