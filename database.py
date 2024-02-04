from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from flask_login import UserMixin


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Users(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    blogposts: Mapped[str] = relationship("Blogposts", back_populates="author")
    comments: Mapped[str] = relationship("Comment", back_populates="comment_poster")


class Blogposts(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[str] = mapped_column(nullable=False)
    body: Mapped[str] = mapped_column(nullable=False)
    # author: Mapped[str] = mapped_column(nullable=False)
    img_url: Mapped[str] = mapped_column(nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped[str] = relationship("Users", back_populates="blogposts")
    comments: Mapped[str] = relationship("Comment", back_populates="original_post")


class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(nullable=False)
    comment_poster: Mapped[str] = relationship("Users", back_populates="comments")
    comment_poster_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    original_post: Mapped[str] = relationship("Blogposts", back_populates="comments")
    original_post_id: Mapped[str] = mapped_column(ForeignKey("blogposts.id"))



