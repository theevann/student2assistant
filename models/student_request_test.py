from datetime import datetime, timedelta

from flask_sqlalchemy import SQLAlchemy
from pytest import fixture
from test.fixtures import db, app

from .student_request import StudentRequest


@fixture
def student_request():
    return StudentRequest(
        id=1, name='Test Student', room='Test room',
        creation_time=datetime.now(),
        last_ping_time=datetime.now()
    )


def requests_n(db, n, timedeltas=None):
    timedeltas = iter(timedeltas) if timedeltas is not None else range(n);
    requests = []

    for i in range(n):
        delta = next(timedeltas)
        request_dict = dict(
            name='Test Student {}'.format(i),
            room='Test room',
            creation_time=datetime.now() + timedelta(seconds=delta),
            last_ping_time=datetime.now() + timedelta(seconds=delta)
        )
        request = StudentRequest(**request_dict)
        db.session.add(request)
        requests.append(request)

    db.session.commit()
    return requests


def test_StudentRequest_create(student_request: StudentRequest):
    assert student_request


def test_create_in_db(db: SQLAlchemy):  # noqa

    request_dict = dict(
        id=1, name='Test Student', room='Test room',
        creation_time=datetime.now(),
        last_ping_time=datetime.now()
    )

    request = StudentRequest(**request_dict)
    db.session.add(request)
    db.session.commit()
    
    results = StudentRequest.query.all()

    assert len(results) == 1

    for k in request_dict.keys():
        assert getattr(results[0], k) == request_dict[k]


def test_rank(db: SQLAlchemy):

    request_1, request_2 = requests_n(db, 2, [0, 1])

    rank_1 = request_1.get_rank()
    rank_2 = request_2.get_rank()

    assert rank_1 == 1
    assert rank_2 == 2


def test_update_ping_time(db: SQLAlchemy):
    request_1 = requests_n(db, 1, [-100])[0]
    previous_date = request_1.last_ping_time
    request_1.update_ping()
    assert request_1.last_ping_time != previous_date

def test_remove_stale(db: SQLAlchemy):
    request_1, request_2 = requests_n(db, 2, [0, -100])
    assert len(StudentRequest.query.all()) == 2
    StudentRequest.remove_stale()
    assert StudentRequest.query.one() == request_1 


def test_remove_stale_once_every(db: SQLAlchemy):
    request_1, request_2 = requests_n(db, 2, [0, -100])
    assert len(StudentRequest.query.all()) == 2
    StudentRequest.remove_stale()
    assert len(StudentRequest.query.all()) == 2
