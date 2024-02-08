from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField


class PostForm(FlaskForm):
    title = StringField(label="Blog Post Title", validators=[DataRequired()])
    subtitle = StringField(label="Subtitle", validators=[DataRequired()])
    # author = StringField(label="Your Name", validators=[DataRequired()])
    img_url = StringField(label="Blog Image Url", validators=[DataRequired()])
    body = CKEditorField(label="Blog Content", validators=[DataRequired()])
    submit = SubmitField(label="Submit Post")


class CommentForm(FlaskForm):
    comment = CKEditorField(label="Comment", validators=[DataRequired()])
    submit = SubmitField(label="Post Comment")


class RegisterForm(FlaskForm):
    email = StringField(label='Email Address', validators=[DataRequired()], render_kw={"class": "form-control", "placeholder": "Enter your email..."})
    password = PasswordField(label='Password', validators=[DataRequired()], render_kw={"class": "form-control", "placeholder": "Enter your password..."})
    name = StringField(label='Name', validators=[DataRequired()], render_kw={"class": "form-control", "placeholder": "Enter your name..."})
    submit = SubmitField(label='SUBMIT', render_kw={"class": "btn btn-primary text-uppercase"})


class LoginForm(FlaskForm):
    email = StringField(label='Email Address', validators=[DataRequired()], render_kw={"class": "form-control", "placeholder": "Enter your email..."})
    password = PasswordField(label='Password', validators=[DataRequired()], render_kw={"class": "form-control", "placeholder": "Enter your password..."})
    submit = SubmitField(label='SUBMIT', render_kw={"class": "btn btn-primary text-uppercase"})


class DashForm(FlaskForm):
    email = StringField(label='Email Address', render_kw={"class": "form-control", "placeholder": "Enter your email..."})
    password = PasswordField(label='Password')
    name = StringField(label='Name', validators=[DataRequired()], render_kw={"class": "form-control", "placeholder": "Enter your name..."})
    submit = SubmitField(label='SUBMIT', render_kw={"class": "btn btn-primary text-uppercase"})
