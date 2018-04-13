# Gevent needed for sockets
from gevent import monkey
monkey.patch_all()

# Imports
import os
import json
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

# Configure app
socketio = SocketIO()
app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# DB
db = SQLAlchemy(app)

# Import + Register Blueprints
from app.accounts import accounts as accounts
app.register_blueprint(accounts)
from app.irsystem import irsystem as irsystem
app.register_blueprint(irsystem)

# Initialize app w/SocketIO
socketio.init_app(app)

datajson = json.load(open('././extra/jefit/data.json'))
data = datajson.values()
muscles = []
equipment = []
for exercise in data:
  for m in exercise['muscles']:
    muscles.append(m)
  for e in exercise['equipment']:
    equipment.append(e)

# HTTP error handling
@app.errorhandler(404)
def not_found(error):
  return render_template("404.html"), 404

@app.route('/advanced', methods=['GET'])
def advanced():
  return render_template("advanced.html", muscles=sorted(set(muscles)), equipment=sorted(set(equipment)))
