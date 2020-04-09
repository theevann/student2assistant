from flask import Blueprint
from flask import request, jsonify
from flask_login import login_required, current_user
from easydict import EasyDict as edict

from app.models import Room, Request, redis
from app.auth import load_user


request_api = Blueprint('request', __name__)


@request_api.route('/request', methods=["POST"])
@login_required
def make_request():
    data = edict(request.get_json())  # data should only contain request type

    # Check that it is not the same request as an existing one (e.g same user, same room, same request)
    call_request = Request.query.filter_by(caller=current_user, room=current_user.room, request=data.request).first()
    if call_request is None:
        call_request = Request.add(current_user, data)

    response = jsonify({
        "request_id": call_request and call_request.id,
        "index": call_request and call_request.rank
    })

    Request.check_match_in_room(current_user.room)

    return response


@request_api.route('/request', methods=["DELETE"])
@login_required
def delete_request():
    data = edict(request.get_json())
    req = Request.get_by_id(data.request_id)

    if req is not None and req.caller_id == current_user.id:
        Request.delete_by_id(req.id)

    return "OK"
