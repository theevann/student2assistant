from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from werkzeug.security import check_password_hash, generate_password_hash

from .base import db


class Room(db.Model):
    table = "room"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
    description = Column(String(200), default="")
    creation_time = Column(DateTime, default=datetime.now)
    password_hash = Column(String(128), nullable=False)

    def update(self, changes):
        for key, val in changes.items():
            setattr(self, key, val)
        return

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def add(cls, name, password, description):
        room = Room(
            name=name,
            description=description,
            password_hash=generate_password_hash(password)
        )
        db.session.add(room)
        db.session.commit()
        return room
    
    @classmethod
    def get_by_name(cls, name):
        return Room.query.filter_by(name=name).first()

    @classmethod
    def exists(cls, name):
        return Room.get_by_name(name) is not None
