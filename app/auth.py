from flask import redirect, url_for
from flask_login import LoginManager
from app.models import User


login_manager = LoginManager()


def init_app(app):
    login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('app.index_room'))
