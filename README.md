# Student2Assistant

**Main goal**: Queue/dispatch students to teaching assistants.

## Features:
- Queue students until an assistant is online and available
- Chat in the browser
- Call in the browser
- Share screen in the browser
- "Zoom integration" : launch call on zoom rather than in the browser

**Warning**:  
This repo was not initially made for sharing purpose - a couple of files will have to be adapted.  
The install-instructions of this repo have not been tested.

# Installing the server
- Install requirements (with python3-pip: `python3 -m pip install -r requirements.txt`)
- Install redis-server (ubuntu: `sudo apt-get install redis-server`)
- Create and seed db: `python3 db.py seed`

# Starting server
- Start redis-server
- Start flask server with `python3 run.py` or use gunicorn with `gunicorn -k gevent -w 4 -b localhost:8000 run:app`
