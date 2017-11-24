from werkzeug.security import generate_password_hash, check_password_hash
# User模型继承UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
# from . import login_manager
from markdown import markdown
from flaskext.markdown import Markdown
from datetime import datetime


class Role(db.Model):
    # __table_args__ = {'extend_existing': True}
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    def __init__(self, name):
        self.name = name

    # users = db.relationship('User', backref='role', lazy='dynamic')

    # __repr__ 方法告诉 Python 如何打印这个类的对象,用它来调试。
    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model, UserMixin):
    # __table_args__ = {'extend_existing': True}
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))#, unique=True, index=True)
    password_hash = db.Column(db.String(128))

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role = db.relationship('Role', backref=db.backref('user_set', lazy='dynamic'))
    cards = db.relationship('Card', backref='author', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def confirm_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, username, password, role):
        self.username = username
        self.password = password

    def is_authenticated(self):
        return True

    def is_active():
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '%s' % self.username


# 创建卡片数据库对象模型
class Card(db.Model):
    # __table_args__ = {'extend_existing': True}
    __tablename__ = 'cards'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.String(350))
    last_modified_on = db.Column(db.DateTime, index=True)
    # 创建时得到Markdown的HTML代码缓存到数据库这个列中。
    body_html = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.last_modified_on = datetime.utcnow()
        # 创建时得到Markdown的HTML代码缓存到数据库这个列中。
        self.body_html = markdown(self.body, output_format='html')
        # self.body_html = body

class SHL(db.Model):
    # __table_args__ = {'extend_existing': True}
    __tablename__ = 'shl'
    id = db.Column(db.Integer, primary_key=True)
    bian_jing = db.Column(db.String(60))
    type = db.Column(db.String(350))
    content = db.Column(db.DateTime, index=True)
    fangji = db.Column(db.Text)
    fangji_details = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, id, bian_jing, type, content, fangji, fangji_details):
        self.id = id
        self.bian_jing = bian_jing
        self.type = type
        self.content = content
        self.fangji = fangji
        self.fangji_details = fangji_details
