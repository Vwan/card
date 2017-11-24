# 添加用户登录表单
from flask import render_template, flash, redirect, session, url_for, request, current_app
from flask_login import login_user, logout_user, login_required, current_user

from app.utils import search_card_from_src_db
from .forms import NameForm, RegistrationForm, CardForm
from app import app, db, loginmanager, markdown, pagedown, moment
from .models import User, Role, Card
from sqlalchemy.sql.expression import func
from flaskext.markdown import Markdown

from markdown import markdown

# 回调函数，如果能找到用户，这个函数必须返回用户对象，否则返回None
from . import loginmanager

tables = [
    "医学衷中参西录",
    '伤寒论',
    '金贵要略',
    # '中兽医'
]


# app.config['tables']

@loginmanager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is not None and user.confirm_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('card'))
        flash('Invalid username or password.')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))
    # return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        role = Role('user')
        user = User(form.username.data, form.password.data, role)
        db.session.add(user)
        db.session.commit()
        flash('You can now login.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/new', methods=['GET', 'POST'])
@app.route("/card", methods=['GET', 'POST'])
@login_required
def card():
    form = CardForm()
    user = current_user._get_current_object()

    # print(request)
    # print(request.args.get("{card.id}"))

    if form.validate_on_submit():
        card = Card(form.title.data, form.body.data)
        card.author = user
        print(card.author)

        db.session.add(card)
        db.session.commit()
        cards = Card.query.filter_by(author=user).order_by(Card.timestamp.desc()).limit(8)
        return redirect(url_for('card'))
    cards = Card.query.filter_by(author=user).order_by(Card.timestamp.desc()).limit(8)
    return render_template('index.html', form=form, cards=cards)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    card = Card.query.get_or_404(id)
    user = current_user._get_current_object()
    if current_user != card.author:
        abort(403)
    form = CardForm()
    if form.validate_on_submit():
        print(form.title.data, form.body.data)
        card.title = form.title.data
        card.body = form.body.data
        card.body_html = markdown(card.body, output_format='html')
        print("markdown is ")
        print(card.body_html)
        db.session.add(card)
        flash("卡片内容已经更新")
        db.session.commit()
        cards = Card.query.filter_by(author=user).order_by(Card.timestamp.desc()).limit(8)
        return redirect(url_for('card'))
    form.body.data = card.body
    form.title.data = card.title
    cards = Card.query.filter_by(author=user).order_by(Card.timestamp.desc()).limit(8)
    return render_template('edit_card.html', form=form, cards=cards)


@app.route("/search", methods=['POST'])
def search():
    data = request.json['search-str']
    condition = "details LIKE '%" + data + "%'"
    print("condition is: " + condition)
    for table_name in tables:
        search_card_from_src_db(table_name, condition, data)
    cards = Card.query.filter(Card.title.contains(data)).all()
    return redirect(url_for('show_all'))
    #return render_template('show_all.html', cards=cards)


# 新功能测试页面
@app.route('/test', methods=['GET', 'POST'])
def test():
    return render_template('test.html')


@app.route('/test_card', methods=['GET', 'POST'])
def test_card():
    cards = Card.query.order_by(Card.timestamp.desc()).all()
    return render_template('test_card.html', cards=cards)


@app.route('/show_all/page', defaults={'page': 1}, methods=['GET', 'POST'])
@app.route("/show_all/page/<int:page>/", methods=["GET", "POST"])
# @login_required
def show_all(page):
    # 不知道为何需要用到request.args
    pic_flag = 0
    user = current_user._get_current_object()
    cards = Card.query.order_by(Card.last_modified_on.desc())#.all()
    paginated = cards.paginate(page, 10)
    # cards = Card.query.filter((Card.author_id == user) | (Card.author_id == "")).all()
    # if cards:
    #     cards = Card.query.filter_by().order_by(Card.last_modified_on.desc()).all()
    #     print("++++", cards)

    if request.args.get("pic") == "显示图片":
        pic_flag = 0

    if request.args.get("shuffle") == "乱序拼接":
        # 将数据库查询结果乱序
        #         cards = Card.query.order_by(func.random()).all()
        cards = Card.query.filter_by(author=user).order_by(func.random()).limit(6)

    return render_template('show_all.html', cards=cards, paginated=paginated, pic_flag=pic_flag)

@app.route('/show_all/<title>/page', defaults={'page': 1}, methods=['GET', 'POST'])
@app.route("/show_all/<title>/page/<int:page>/", methods=["GET", "POST"])
# @login_required
def show_all_filtered(title, page):
    pic_flag = 0
    user = current_user._get_current_object()
    cards = Card.query.filter(Card.title.contains(title)).order_by(Card.last_modified_on.desc())#.all()
    paginated = cards.paginate(page, 10)
    return render_template('show_all.html', title=title, cards=cards, paginated=paginated, pic_flag=pic_flag, search_card_str=title)