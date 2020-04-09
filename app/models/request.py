import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from .base import db, redis
from .history import History


class Request(db.Model):
    table = "request"

    id = Column(Integer, primary_key=True)
    caller_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    room_id = Column(Integer, ForeignKey('room.id'), nullable=False)
    request = Column(String(64), nullable=False)
    creation_time = Column(DateTime, default=datetime.now)

    room = relationship("Room")
    caller = relationship("User")

    def update(self, changes):
        for key, val in changes.items():
            setattr(self, key, val)
        return

    @classmethod
    def check_match_in_room(cls, room): # Match only assistant role for now
        from app.models import User

        while True:
            requested_user = User.get_free_user(role="assistant", room=room)
            if (requested_user is None):
                return # If no assistant available - no match

            request = Request.query.join(User) \
                .filter(Request.room == room, Request.request == "assistant", User.connected == True) \
                .order_by(Request.creation_time) \
                .first()
            if (request is None):
                return  # If there is no request
            elif (not request.caller.connected):
                return  # If the one who made the request is mot connected -- TODO: Include in previous query

            data = json.dumps({
                "request_id": request.id,
                "caller_id": request.caller_id,
                "callee_peer_id": requested_user.peer_id,
                "callee_zoom_id": requested_user.zoom_id,
            })

            redis.publish("{}.queue.match".format(room.name), data)

            requested_user.set_status("busy")
            History.add("assistant", room, request.caller, requested_user)
            
            db.session.delete(request)
            db.session.commit()



    @classmethod
    def get_by_id(cls, request_id):
        return Request.query.get(request_id)

    @property
    def rank(self):
        ranks = func.row_number().over(order_by=Request.creation_time).label('rank')
        subquery = db.session.query(Request.id, ranks).filter_by(room=self.room, request=self.request).subquery()
        return db.session.query(subquery.c.rank).filter(subquery.c.id == self.id).one()[0]

    @classmethod
    def queue_size(cls, room, request):
        return Request.query.filter_by(room=room, request=request).count()

    @classmethod
    def add(cls, user, data):
        request = Request(
            request=data["request"],
            room=user.room,
            caller=user,
        )
        db.session.add(request)
        db.session.commit()

        data = json.dumps({"request_id": request.id, "caller": request.caller.name})
        redis.publish("{}.queue.new".format(user.room.name), data)

        return request

    @classmethod
    def delete_all_from(cls, caller_id):
        request_ids = db.session.query(Request.id).filter_by(caller_id=caller_id).all()
        for rid in request_ids:
            Request.delete_by_id(rid)

    @classmethod
    def delete_by_id(cls, request_id):
        request = Request.query.get(request_id)
        
        if request is None:
            return

        data = json.dumps({
            "request_rank": request.rank,
        })

        redis.publish("{}.queue.delete".format(request.room.name), data)

        db.session.delete(request)
        db.session.commit()
