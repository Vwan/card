from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_moment import Moment
# from config import config
from flask_pagedown import PageDown
from flask_pagedown.fields import PageDownField
# 为markdown的显示支持
import markdown
from flaskext.markdown import Markdown
from datetime import datetime
import sqlite3 as sql
import pandas as pd
import pandas.io.sql as pd_sql
import os

root_dir = basedir = os.path.dirname(__file__)

app = Flask(__name__)

app.config.from_object('config')  # 使Flask读取使用Flaks-WTF
bootstrap = Bootstrap(app)  # 实例化

# flask_login的初始化
loginmanager = LoginManager()
loginmanager.init_app(app)
loginmanager.session_protection = 'strong'
loginmanager.login_view = 'login'

db = SQLAlchemy(app)  # 初始数据库
pagedown = PageDown(app)
Markdown(app)
moment = Moment(app)
from app import views, models
#db.drop_all()
db.create_all()

xlsfile = "shanghanlun_wang.xlsx"
db_name = "./app.db"
# table_name = "shl"

conn = sql.connect(db_name)
# conn.row_factory = dict_factory
cur = conn.cursor()
with pd.ExcelFile(os.path.join(root_dir, xlsfile)) as file:
    sheets = file.sheet_names
    for sheet in sheets:
        print(sheet)
        cur.executescript('drop table if exists ' + sheet)
        data = pd.read_excel(file, sheet, header=0, index_col=None, na_values=['NA'])
        pd_sql.to_sql(data, sheet, conn)

conn.commit()
conn.close()
