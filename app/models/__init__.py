from .base import db
from .base import redis
from .user import User
from .room import Room
from .request import Request


def init_app(app):
    db.init_app(app)
