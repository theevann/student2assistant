from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from .base import db


class History(db.Model):
    table = "history"

    id = Column(Integer, primary_key=True)
    caller = Column(String(64), nullable=False)
    callee = Column(String(64), nullable=False)
    room_id = Column(Integer, ForeignKey('room.id'), nullable=False)
    request = Column(String(64), nullable=False)
    creation_time = Column(DateTime, default=datetime.now)

    room = relationship("Room")

    @classmethod
    def add(cls, request, room, caller, callee):
        hist = History(
            request=request,
            room=room,
            caller=caller.name,
            callee=callee.name,
        )
        db.session.add(hist)
        db.session.commit()
