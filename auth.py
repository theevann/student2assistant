from werkzeug.security import generate_password_hash, check_password_hash
from flask_httpauth import HTTPBasicAuth

TAS = {
    "ta": generate_password_hash("generic-ta-password")
}

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if username in TAS:
        return check_password_hash(TAS[username], password)
    return False

