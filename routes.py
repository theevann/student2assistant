from easydict import EasyDict as edict
from datetime import datetime

from flask import Flask, abort, jsonify, redirect, render_template, request, url_for

from __main__ import app
from auth import auth
from models import db
from models import StudentRequest, Assistant

@app.route('/')
def index():
    return redirect(url_for("index_student"), code=302)


@app.route('/student')
def index_student():
    return render_template("student.html")


@app.route('/assistant')
@auth.login_required
def index_assistant():
    return render_template("assistant.html")


@app.route('/set-assistant-status', methods=["POST"])
@auth.login_required
def set_assistant_status():
    req = edict(request.get_json())
    assistant = Assistant.get_by_peer_id(req.id)
    if assistant is None:
        abort(404)
    assistant.set_status(req.status)
    return "OK"


@app.route('/get-assistant-status', methods=["GET"])
@auth.login_required
def get_assistant_status():
    assistant = Assistant.get_by_peer_id(request.args.get("id"))
    if assistant is None:
        abort(404)
    assistant.update_ping()
    return jsonify({"status": assistant.status})


@app.route('/register-assistant', methods=["POST"])
@auth.login_required
def register_assistant():
    req = edict(request.get_json())
    assistant = Assistant.get_by_peer_id(req.id)
    if assistant is None:
        assistant = Assistant(peer_id=req.id, name=req.name, status=req.status, room=req.room)
        db.session.add(assistant)
    else:
        assistant.name = req.name
        assistant.room = req.room
        assistant.status = req.status
    db.session.commit()
    return "OK"


@app.route('/request-call', methods=["POST"])
def request_call():
    req = edict(request.get_json())
    student = StudentRequest.get_by_peer_id(peer_id=req.id)
    if student is None:
        student = StudentRequest(peer_id=req.id, name=req.name, room=req.room)
        db.session.add(student)
        db.session.commit()
    return "OK"


@app.route('/cancel-request', methods=["GET"])  # TODO: CHANGE TO GET
def cancel_call():
    student_request = StudentRequest.get_by_peer_id(request.args.get("id"))
    student_request.delete()
    db.session.commit()
    return "OK"


@app.route('/get-request-status', methods=["GET"])
def get_request_status():
    StudentRequest.remove_stale()
    
    student_request = StudentRequest.get_by_peer_id(request.args.get("id"))
    if not student_request:
        # Maybe abort 400?
        return jsonify({"index": -1})

    student_request.update_ping()

    rank = student_request.get_rank()
    if rank > 1:
        return jsonify({"index": rank})

    assistant = Assistant.select_free_assistant()
    if assistant is None:
        return jsonify({"index": rank})

    db.session.delete(student_request)
    db.session.commit()

    return jsonify({
        "index": 0,
        "assistant_id": assistant.peer_id
    })
