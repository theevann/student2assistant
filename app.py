from easydict import EasyDict as edict
from flask import Flask, jsonify, render_template, request

# nohup gunicorn -w4 -k gevent -b localhost:8001 app-new:app >out.log 2>err.log &

class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='%%',
        variable_end_string='%%',
    ))


app = CustomFlask(__name__)


assistants = {}
student_requests = []


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/student')
def index_student():
    return render_template("student.html")


@app.route('/assistant')
def index_assistant():
    return render_template("assistant.html")


@app.route('/set-assistant-status', methods=["POST"])
def set_assistant_status():
    req = edict(request.get_json())
    assistants[req.name].status = req.status
    return "OK"


@app.route('/get-assistant-status', methods=["GET"])
def get_assistant_status():
    name = request.args.get('name')
    return jsonify({ "status": assistants[name].status})


@app.route('/register-assistant', methods=["POST"])
def register_assistant():
    req = edict(request.get_json())
    assistants[req.name] = req
    return "OK"


@app.route('/request-call', methods=["POST"])
def request_call():
    req = edict(request.get_json())
    index = next((idx for idx, req_ in enumerate(student_requests) if req_.name == req.name), -1)
    if index == -1:
        student_requests.append(req)
    return "OK"


@app.route('/cancel-request', methods=["GET"])
def cancel_request():
    name = request.args.get('name')
    req = next((req for req in student_requests if req.name == name), None)
    if req is not None:
        student_requests.remove(req)
    return "OK"


@app.route('/get-request-status', methods=["GET"])
def get_request_status():
    print(student_requests)
    name = request.args.get('name')
    index = next((idx for idx, req in enumerate(student_requests) if req.name == name), -1)
    response = {"index": index}

    # Potential Problem : Student closes page => need to remove his/her request
    if index == 0:
        assistant = get_available_assistant()
        if assistant is not None:
            response["assistant_id"] = assistant.id
            assistant.status = "busy"
            student_requests.pop(0)

    return jsonify(response)


def get_available_assistant():
    return next((ta for ta in assistants.values() if ta.status == "free"), None)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)


# TODO:
# Remove requests that are not asked for...
# Make sounds / Show that you're being called
# Check microphone working
# Chat with code formatting
