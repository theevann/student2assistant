import json
import functools
from time import sleep
from easydict import EasyDict as edict

from flask import Blueprint, Response
from flask import request, jsonify, stream_with_context
from flask_login import login_required, current_user

from app.models import User, Room, Request
from app.models import db, redis


stream_api = Blueprint('stream', __name__)

@stream_api.route('/status', methods=["GET"])
@login_required
def get_status():
    return jsonify({
        "status": current_user.status
    })


@stream_api.route('/status', methods=["POST"])
@login_required
def set_status():
    data = edict(request.get_json())
    current_user.set_status(data.status)
    if data.status == "free":
        Request.check_match_in_room(current_user.room)
    return jsonify({
        "status": current_user.status
    })


@stream_api.route('/queue', methods=["GET"])
def get_queue_status():
    data = edict(request.args)
    room = Room.get_by_name(data.room)
    if not room:
        return jsonify({ "error": "Room {} does not exist".format(data.room) })
    
    return jsonify({
        "room": room.name,
        "assistant_connected": User.query.filter_by(room=room, role="assistant", connected=True).count(),
        "assistant_available": User.query.filter_by(room=room, role="assistant", connected=True, status="free").count(),
        "queue": Request.queue_size(room, "assistant")
    })


def pubsub_connector(func):
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        try:
            pubsub = redis.pubsub(ignore_subscribe_messages=True)
            current_user.set_connected(True)
            yield from func(pubsub, *args, **kwargs)
        finally:
            # print("Connection lost to {}".format(current_user.name))
            current_user.set_connected(False)
            current_user.set_status("busy")  # TODO: if recconection -- change of status might be not visible in frontend 
            pubsub.close()

            sleep(15)
            db.session.refresh(current_user)
            if not current_user.connected:
                # print("Deleting ", current_user.name)
                current_user.delete()

    return wrapper_decorator


@stream_api.route('/updates')
@login_required
def stream():
    if current_user.role == "student":
        response = Response(stream_with_context(stream_updates_for_student()), mimetype="text/event-stream")
    elif current_user.role == "assistant":
        response = Response(stream_with_context(stream_updates_for_assistant()), mimetype="text/event-stream")
    response.headers["X-Accel-Buffering"] = "no"
    return response


@pubsub_connector
def stream_updates_for_student(pubsub):
    room = current_user.room.name

    pubsub.psubscribe('{room}.assistant.*'.format(room=room))
    pubsub.subscribe('{room}.queue.match'.format(room=room))
    pubsub.subscribe('{room}.queue.delete'.format(room=room))

    while True:
        red_message = pubsub.get_message()
        if red_message is None:
            yield "data: {}\n\n"
            sleep(0.1)
            continue

        red_message = edict(red_message)
        channel = red_message.channel.decode('utf-8')

        if channel == "{}.assistant.new".format(room):
            yield "event:new_assistant\ndata:\n\n"

        elif channel == "{}.assistant.delete".format(room):
            yield "event:delete_assistant\ndata:\n\n"

        elif channel == "{}.assistant.update".format(room):
            yield "event:update_assistant\ndata:\n\n"

        elif channel == "{}.queue.delete".format(room):
            data = json.dumps(json.loads(red_message.data))
            yield "event:rank_update\ndata:{}\n\n".format(data)

        elif channel == "{}.queue.match".format(room):
            data = edict(json.loads(red_message.data))

            if data.caller_id != current_user.id:
                dump_data = json.dumps({ "request_rank" : 0 })
                yield "event:rank_update\ndata:{}\n\n".format(dump_data)

            else:
                dump_data = json.dumps({
                    "assistant_peer_id": data.callee_peer_id,
                    "assistant_zoom_id": data.callee_zoom_id,
                })
                lines = ["event:match_request"]
                lines += [
                    "data:{value}".format(value=line) for line in dump_data.splitlines()
                ]

                to_send = "\n".join(lines) + "\n\n"
                yield to_send


@pubsub_connector
def stream_updates_for_assistant(pubsub):
    room = current_user.room.name

    pubsub.psubscribe('{}.assistant.*'.format(room))
    pubsub.psubscribe('{}.queue.*'.format(room))


    dump_data = json.dumps({
        "assistants": list(map(lambda assistant: assistant.dict(), User.query.filter_by(role="assistant", room=current_user.room).all())),
        "requests": [],
    })
    lines = [
        "event:initial_state",
        "data:{value}".format(value=dump_data)
    ]
    yield "\n".join(lines) + "\n\n"
    # print(dump_data)


    while True:
        red_message = pubsub.get_message()
        if red_message is None:
            yield "data: {}\n\n"
            sleep(0.1)
            continue

        red_message = edict(red_message)

        channel = red_message.channel.decode('utf-8')
        data = red_message.data.decode('utf-8')

        if channel == "{}.assistant.new".format(room):
            lines = [
                "event:new_assistant",
                "data:{value}".format(value=data)
            ]
        elif channel == "{}.assistant.delete".format(room):
            lines = [
                "event:delete_assistant",
                "data:{value}".format(value=data)
            ]
        elif channel == "{}.assistant.update".format(room):
            lines = [
                "event:update_assistant",
                "data:{value}".format(value=data)
            ]
        elif channel == "{}.queue.new".format(room):
            lines = [
                "event:new_request",
                "data:{value}".format(value=data)
            ]
        elif channel == "{}.queue.match".format(room):
            lines = [
                "event:match_request",
                "data:{value}".format(value=data)
            ]
        elif channel == "{}.queue.delete".format(room):
            lines = [
                "event:delete_request",
                "data:{value}".format(value=data)
            ]

        yield "\n".join(lines) + "\n\n"



