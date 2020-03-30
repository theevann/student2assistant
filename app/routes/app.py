from flask import Blueprint
from flask import render_template, redirect, url_for
from flask_login import current_user

from app.models import Room

app_routes = Blueprint('app', __name__)


@app_routes.route('/')
def index_room():
    rooms = Room.query.all()
    return render_template("index_room.html", rooms=rooms)  # Choice of room


@app_routes.route('/<string:room_name>/')
def index_role(room_name):
    if not Room.exists(room_name):
        return redirect(url_for("app.index_room"))
    
    return render_template("index_role.html")  # Choice of role


@app_routes.route('/<string:room_name>/<string:role>')
def index_student(room_name, role):
    if not Room.exists(room_name):
        return redirect(url_for("app.index_room"))
    elif role not in ["student", "assistant"]:
        return redirect(url_for("app.index_role"))

    return render_template("{}.html".format(role))
