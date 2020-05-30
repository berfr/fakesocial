"""
"""

from .config import config

import datetime
import functools

import sqlalchemy
from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


engine = sqlalchemy.create_engine("sqlite:///" + config["db_file"])

Base = declarative_base()


def retry_if_constraint_fails(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        count = 0
        while True:
            if count >= 5:
                raise ValueError("Ran into IntegrityError too many times")
            try:
                return func(*args, **kwargs)
            except sqlalchemy.exc.IntegrityError:
                count += 1
                logging.debug("IntegrityError")

    return wrapper


class Like(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    __table_args__ = (UniqueConstraint("post_id", "user_id"),)
    user = relationship("User")


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    text = Column(String)
    user = relationship("User")

    def info(self):
        return {
            "id": self.id,
            "created_date": self.created_date,
            "user": self.user.info(),
            "text": self.text,
        }


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    text = Column(String)
    comments = relationship("Comment")
    likes = relationship("Like")
    user = relationship("User")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def info(self):
        return {
            "id": self.id,
            "created_date": self.created_date,
            "user": self.user.info(),
            "text": self.text,
            "comment_count": len(self.comments),
            "like_count": len(self.likes),
        }

    def details(self):
        return {
            **self.info(),
            "comments": [c.info() for c in self.comments],
            "likes": [l.user.full_name for l in self.likes],
        }


class Connection(Base):
    __tablename__ = "connections"
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    user_1_id = Column(Integer, ForeignKey("users.id"))
    user_2_id = Column(Integer, ForeignKey("users.id"))
    __table_args__ = (UniqueConstraint("user_1_id", "user_2_id"),)
    user_1 = relationship("User", foreign_keys=[user_1_id])
    user_2 = relationship("User", foreign_keys=[user_2_id])


class Image(Base):
    __tablename__ = "images"
    uuid = Column(String, primary_key=True)
    image_hash = Column(String, unique=True)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    image_uuid = Column(String, ForeignKey("images.uuid"), unique=True)
    full_name = Column(String, unique=True)

    location = Column(String)
    job_title = Column(String)
    company_name = Column(String)

    connections = relationship(
        "Connection",
        primaryjoin="or_(User.id==Connection.user_1_id, User.id==Connection.user_2_id)",
    )
    posts = relationship("Post", order_by="desc(Post.created_date)")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def _image_path(self, size):
        return "{}/{}_{}.jpg".format("/images", self.image_uuid, size)

    def info(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "image_64_path": self._image_path(64),
        }

    def _connections(self):
        return [
            c.user_1 if c.user_1.id != self.id else c.user_2 for c in self.connections
        ]

    def details(self):
        return {
            **self.info(),
            "created_date": self.created_date,
            "image_256_path": self._image_path(256),
            "location": self.location,
            "job_title": self.job_title,
            "company_name": self.company_name,
            "connections": [c.full_name for c in self._connections()],
            "posts": [p.info() for p in self.posts],
        }


def get_latest_created_date():
    """Return the most recent created_date of models."""
    session = Session()
    models = [Like, Comment, Post, Connection, User]
    latest_date = None
    for model in models:
        latest_object = (
            session.query(model).order_by(sqlalchemy.desc(model.created_date)).first()
        )
        if not latest_object:
            continue
        latest_object_date = latest_object.created_date
        if not latest_date or latest_object_date > latest_date:
            latest_date = latest_object_date
    session.close()
    return latest_date


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
