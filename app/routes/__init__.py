from app.routes.app import app_routes
from app.routes.login import login_api
from app.routes.stream import stream_api
from app.routes.request import request_api


def init_app(app):
    app.register_blueprint(app_routes)
    app.register_blueprint(login_api)
    app.register_blueprint(stream_api)
    app.register_blueprint(request_api)
