from .base import db
from .base import redis
from .user import User
from .room import Room
from .request import Request
from .request import History


def init_app(app):
    db.init_app(app)
