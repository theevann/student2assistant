import subprocess
import pytest
from datetime import datetime, timedelta

from app import create_app


@pytest.fixture
def app():
    return create_app('test')


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    from app import db
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()
        db.session.commit()



# basedir = os.path.abspath(os.path.dirname(__file__))

# @pytest.fixture
# def some_db(request):
#     app.config['TESTING'] = True
#     app.config['CSRF_ENABLED'] = False
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
#     db.create_all()

#     def fin():
#         db.session.remove()
#         db.drop_all()
#     request.addfinalizer(fin)
