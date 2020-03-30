import redis
from flask import Flask
from flask_migrate import Migrate

from app import models
from app import routes
from app import auth

from app.config import config_by_name


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='%%',
        variable_end_string='%%',
    ))


def create_app(env):
    app = CustomFlask(__name__)
    app.config.from_object(config_by_name[env])

    routes.init_app(app)
    models.init_app(app)
    auth.init_app(app)



    with app.app_context():
        from werkzeug.security import generate_password_hash
        from app.models import Room, db
        # db.session.add(
        #     Room(name="ee-334", password_hash=generate_password_hash("pass"))
        # )
        # db.session.add(
        #     Room(name="test", password_hash=generate_password_hash(""))
        # )
        # db.session.commit()

    return app


app = create_app("dev")
migrate = Migrate(app, models.db)

# boris.conforty@epfl.ch
