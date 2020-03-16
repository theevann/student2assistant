from models import db
from sqlalchemy.orm import relationship
from sqlalchemy import func
from datetime import datetime, timedelta


class Assistant(db.Model):
    table = "assistants"

    id = db.Column(db.Integer, primary_key=True)
    peer_id = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(64), nullable=False)
    room = db.Column(db.String(64), nullable=False)
    last_ping_time = db.Column(db.DateTime, default=datetime.now)

    def update_ping(self):
        self.last_ping_time = datetime.now()
        db.session.commit()

    def set_status(self, status):
        self.status = status
        db.session.commit()

    @classmethod
    def get_by_peer_id(cls, peer_id):
        return Assistant.query.filter_by(peer_id=peer_id).first()

    @classmethod
    def select_free_assistant(cls):
        assistant = Assistant.query \
            .filter_by(status='free') \
            .order_by(func.random()) \
            .limit(1) \
            .with_for_update() \
            .first() \
        
        if (assistant is None):
            return None

        assistant.status = "busy"
        db.session.commit()

        return assistant
