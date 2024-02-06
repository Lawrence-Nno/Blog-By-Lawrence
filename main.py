import flask
from flask import Flask, render_template, request, url_for, redirect, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from form import RegisterForm, LoginForm, PostForm, CommentForm
from database import Blogposts, Users, db, Comment
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import hashlib
import os
import psycopg2


login_manager = LoginManager()
app = Flask(__name__)
Bootstrap(app)
ckeditor = CKEditor(app)
DATABASE_URL = os.environ['DATABASE_URL']
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///posts.db")
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
app.secret_key = os.environ["key"]
db.init_app(app)
login_manager.init_app(app)


def gravatar_url(email, size=50,rating='g',default='retro',force_default=False):
    hash_value = hashlib.md5((email.lower().encode('utf-8'))).hexdigest()
    return f"https://www.gravatar.com/avatar/{hash_value}?s={size}&d={default}&r={rating}&f={force_default}"


@login_manager.user_loader
def load_user(user_id):
    return db.session.execute(db.select(Users).where(Users.id == user_id)).scalar()


def admin_decorator(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        if current_user.id == 1:
            return func(*args, **kwargs)
        else:
            return abort(403)
    # wrapper_func.__name__ = func.__name__
    return wrapper_func


current_time = datetime.now()
current_year = current_time.year


@app.route('/')
def home():
    all_posts = db.session.query(Blogposts).all()
    return render_template('index.html', posts=all_posts, year=current_year, logged_in=current_user.is_authenticated)


@app.route('/new-post', methods=["GET", "POST"])
@login_required
@admin_decorator
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        new_post = Blogposts(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            date=current_time.strftime("%B %d %Y"),
            # author="Lawrence",
            img_url=form.img_url.data,   # "url_for('static', filename='assets/img/post-bg.jpg')"
            author_id=current_user.id
        )
        db.session.add(new_post)
        db.session.commit()
        all_posts = db.session.query(Blogposts).all()
        return render_template('index.html', posts=all_posts, year=current_year, logged_in=current_user.is_authenticated)
    return render_template('make-post.html', form=form, logged_in=current_user.is_authenticated)


@app.route('/edit-post/<post_id>', methods=["GET", "POST"])
@login_required
@admin_decorator
def edit_post(post_id):
    # post_to_edit = db.session.query(BlogPost).where(BlogPost.id == post_id).scalar()
    post_to_edit = db.session.execute(db.select(Blogposts).where(Blogposts.id == post_id)).scalar()
    form = PostForm(
        title=post_to_edit.title,
        subtitle=post_to_edit.subtitle,
        body=post_to_edit.body,
        author=post_to_edit.author,
        img_url=post_to_edit.img_url
    )
    if form.validate_on_submit():
        post_to_edit.title = form.title.data
        print(f"Form data = {form.title.data}")
        print(post_to_edit.title)
        post_to_edit.subtitle = form.subtitle.data
        post_to_edit.body = form.body.data
        # post_to_edit.author = form.author.data
        post_to_edit.img_url = form.img_url.data
        db.session.add(post_to_edit)
        db.session.commit()
        return render_template('index.html', post=post_to_edit, logged_in=current_user.is_authenticated)
    return render_template('make-post.html', form=form, post_id=post_id, logged_in=current_user.is_authenticated)


@app.route('/delete/<post_id>')
@login_required
@admin_decorator
def delete(post_id):
    post_to_delete = db.session.execute(db.select(Blogposts).where(Blogposts.id == post_id)).scalar()
    db.session.delete(post_to_delete)
    db.session.commit()
    all_posts = db.session.query(Blogposts).all()
    return render_template('index.html', posts=all_posts, year=current_year, logged_in=current_user.is_authenticated)


@app.route('/about')
def about():
    return render_template('about.html', year=current_year, logged_in=current_user.is_authenticated)


@app.route('/contact', methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        print(request.form['name'])
        print(request.form['email'])
        print(request.form['phone'])
        print(request.form['message'])
        return render_template('contact.html', year=current_year, msg_sent=True, logged_in=current_user.is_authenticated)
    elif request.method == "GET":
        return render_template('contact.html', year=current_year, msg_sent=False, logged_in=current_user.is_authenticated)


# @app.route('/post')
# def post():
#     return render_template('post.html', year=current_year, logged_in=current_user.is_authenticated)


@app.route('/post/<int:num>', methods=["GET", "POST"])
def get_post(num):
    comment_form = CommentForm()
    all_posts = db.session.query(Blogposts).all()
    for blog_post in all_posts:
        if blog_post.id == num:
            requested_post = blog_post

    # all_comments = db.session.execute(db.select(Comment).where(Comment.original_post_id == requested_post.id)).scalars()
    all_comments = db.session.query(Comment).filter_by(original_post_id=requested_post.id)

    if comment_form.validate_on_submit():
        if current_user.is_authenticated:
            print(current_user.email)
            new_comment = Comment(
                text=comment_form.comment.data,
                comment_poster_id=current_user.id,
                original_post_id=num
            )
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for('get_post', num=num))
        else:
            flask.flash("Please Login before you can leave a comment")
            return redirect(url_for('login'))
    return render_template('post.html', num=num, post=requested_post, year=current_year,
                           logged_in=current_user.is_authenticated, form=comment_form, comments=all_comments,
                           gravatar_url=gravatar_url)


@app.route('/register', methods=["GET", "POST"])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        user = db.session.execute(db.select(Users).where(Users.email == register_form.email.data)).scalar()
        if user:
            flask.flash("You have already registered with that email, log in instead")
            return redirect(url_for('login'))
        hashed_pass = generate_password_hash(register_form.password.data, method="pbkdf2:sha256", salt_length=8)
        new_user = Users(
            email=register_form.email.data,
            password=hashed_pass,
            name=register_form.name.data
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html', form=register_form, logged_in=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = db.session.execute(db.select(Users).where(Users.email == login_form.email.data)).scalar()
        if user:
            if check_password_hash(user.password, login_form.password.data):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flask.flash("Wrong password, Check that you are entering the correct password")
                return redirect(url_for('login'))
        else:
            flask.flash("Sorry, That email doesn't exist in our database.")
            return redirect(url_for('login'))
    return render_template('login.html', form=login_form, logged_in=current_user.is_authenticated)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)

