from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from datetime import datetime

from .base import db
from .request import Request

class User(UserMixin, db.Model):
    table = "user"

    id = Column(Integer, primary_key=True)
    peer_id = Column(String(64), unique=True)
    zoom_id = Column(String(64), unique=True, nullable=True)
    name = Column(String(64), nullable=False)
    room_id = Column(Integer, ForeignKey('room.id'), nullable=False)
    role = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False)
    connected = Column(Boolean, default=False)
    creation_time = Column(DateTime, default=datetime.now)
    last_connection_time = Column(DateTime, default=datetime.now)

    room = relationship("Room")

    def update(self, changes):
        for key, val in changes.items():
            setattr(self, key, val)
        return

    def get_id(self):
        return self.id

    def set_status(self, status):
        self.status = status
        db.session.commit()

    def set_connected(self, connected):
        self.connected = connected
        db.session.commit()

    def delete(self):
        Request.delete_all_from(self.id)
        db.session.delete(self)
        db.session.commit()


    @classmethod
    def get_free_user(cls, role, room):
        return User.query \
            .filter_by(status='free', role=role, room=room) \
            .order_by(func.random()) \
            .limit(1) \
            .first()
            # .with_for_update() \

    @classmethod
    def add(cls, data, room):
        user = User(
            peer_id=data["peer_id"],
            zoom_id=data["zoom_id"],
            name=data["name"],
            role=data["role"],
            status=data["status"],
            room=room
        )
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def remove_user_with_peer_id(cls, peer_id):
        User.query.filter_by(peer_id=peer_id).delete()
