from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from pytest import fixture
from test.fixtures import db, app

from .assistant import Assistant


@fixture
def assistant():
    return get_assistant("free")


@fixture
def cm_free_assistant(db: SQLAlchemy):
    assistant = get_assistant("free")
    db.session.add(assistant)
    db.session.commit()
    return assistant


@fixture
def cm_busy_assistant(db: SQLAlchemy):
    assistant = get_assistant("busy")
    db.session.add(assistant)
    db.session.commit()
    return assistant


def get_assistant(status):
    return Assistant(
        name='Test Assistant',
        room='Test room', status=status,
        last_ping_time=datetime.now()
    )


def test_Assistant_create(assistant: Assistant):
    assert assistant


def test_select_assistant(db: SQLAlchemy, cm_free_assistant, cm_busy_assistant):
    assert Assistant.select_free_assistant() == cm_free_assistant
    assert cm_free_assistant.status == "busy" 


def test_select_with_no_assistant(db: SQLAlchemy):
    assert Assistant.select_free_assistant() == None


def test_select_with_only_busy_assistant(db: SQLAlchemy, cm_busy_assistant):
    db.session.add(cm_busy_assistant)
    db.session.commit()
    assert Assistant.select_free_assistant() == None