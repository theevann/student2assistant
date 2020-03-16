from models import db
from sqlalchemy.orm import relationship
from sqlalchemy import func
from datetime import datetime, timedelta


def once_every(n_seconds):
    prev = [datetime(1, 1, 1)]

    def decorator(f):
        def decorated(*args, **kwargs):
            if (datetime.now() - prev[0]).total_seconds() > n_seconds:
                prev[0] = datetime.now()
                return f(*args, **kwargs)
        return decorated

    return decorator


class StudentRequest(db.Model):
    table = "student_requests"

    id = db.Column(db.Integer, primary_key=True)
    peer_id = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(64), nullable=False)
    room = db.Column(db.String(64), nullable=False)
    creation_time = db.Column(db.DateTime, default=datetime.now)
    last_ping_time = db.Column(db.DateTime, default=datetime.now)

    def get_rank(self):
        ranks = func.row_number().over(order_by=StudentRequest.creation_time).label('rank')
        subquery = db.session.query(StudentRequest.id, ranks).subquery()
        return db.session.query(subquery.c.rank).filter(subquery.c.id == self.id).one()[0]

    def update_ping(self):
        self.last_ping_time = datetime.now()
        db.session.commit()

    @classmethod
    def get_by_peer_id(cls, peer_id):
        return StudentRequest.query.filter_by(peer_id=peer_id).first()

    @classmethod
    @once_every(60)
    def remove_stale(cls, old=60):
        time = datetime.now() - timedelta(seconds=old)
        StudentRequest.query.filter(time > StudentRequest.last_ping_time).delete()
        db.session.commit()
