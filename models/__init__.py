from models.base import db
from models.student_request import StudentRequest
from models.assistant import Assistant


def init_app(app):
    db.init_app(app)
