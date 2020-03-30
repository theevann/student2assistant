from flask import Blueprint
from flask import request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from easydict import EasyDict as edict

from app.models import User, Room
from app.auth import load_user


login_api = Blueprint('login', __name__)


@login_api.route('/login', methods=["GET"])
def get_login():
    return jsonify({
        "is_authenticated": current_user.is_authenticated,
        "room": current_user.room.name if current_user.is_authenticated else None,
        "role": current_user.role if current_user.is_authenticated else None,
        "user_id": current_user.id if current_user.is_authenticated else None
    })


@login_api.route('/login', methods=["POST"])
def do_login():
    data = edict(request.get_json())
    room = Room.get_by_name(data.room)
    error = ""

    # if current_user.is_authenticated:
    #     logout_user()

    if room is None:
        error = "Room {} does not exist".format(data.room)
    elif data.role == "assistant" and not room.check_password(data.password):
        error = "Password is incorrect"
    elif current_user.is_authenticated and \
        current_user.room.name == data.room and \
        current_user.role == data.role:
        current_user.update({
            "zoom_id": data.zoom_id,
            "peer_id": data.peer_id,
            "name": data.name,
        })
    else:
        # User.remove_user_with_peer_id(data.peer_id)
        user = User.add(data, room)
        login_user(user)

    return jsonify({
        "is_authenticated": current_user.is_authenticated,
        "role": current_user.role if current_user.is_authenticated else None,
        "room": current_user.room.name if current_user.is_authenticated else None,
        "user_id": current_user.id if current_user.is_authenticated else None,
        "error": error
    })


@login_api.route('/logout', methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({
        "is_authenticated": current_user.is_authenticated,
    })
