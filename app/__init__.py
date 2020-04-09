import socket
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

    # Remove all requests and users on reboot
    with app.app_context():
        models.User.query.delete()
        models.Request.query.delete()
        models.db.session.commit()

    return app


env = "prod" if socket.gethostname() == "importance-sampling" else "dev"
app = create_app(env)
migrate = Migrate(app, models.db)





# boris.conforty@epfl.ch
