# Gevent needed for sockets
from gevent import monkey
monkey.patch_all()

# Imports
import os
import pickle
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

# Load pickle files
f = open('extra/pickles/description_tfidf','rb')
desc_tfidf = pickle.load(f)
app.config['desc_tfidf'] = desc_tfidf

f = open('extra/pickles/equipment_tfidf','rb')
equip_tfidf = pickle.load(f)
app.config['equip_tfidf'] = equip_tfidf

f = open('extra/pickles/muscles_tfidf','rb')
muscles_tfidf = pickle.load(f)
app.config['muscles_tfidf'] = muscles_tfidf

f = open('extra/pickles/name_tfidf','rb')
name_tfidf = pickle.load(f)
app.config['name_tfidf'] = name_tfidf

f = open('extra/pickles/description_vocab_to_index','rb')
description_vocab_to_index = pickle.load(f)
app.config['description_vocab_to_index'] = description_vocab_to_index

f = open('extra/pickles/equipment_vocab_to_index','rb')
equipment_vocab_to_index = pickle.load(f)
app.config['equipment_vocab_to_index'] = equipment_vocab_to_index

f = open('extra/pickles/muscles_vocab_to_index','rb')
muscles_vocab_to_index = pickle.load(f)
app.config['muscles_vocab_to_index'] = muscles_vocab_to_index

f = open('extra/pickles/name_vocab_to_index','rb')
name_vocab_to_index = pickle.load(f)
app.config['name_vocab_to_index'] = name_vocab_to_index

f = open('extra/pickles/vector_index_to_exercise','rb')
vector_index_to_exercise = pickle.load(f)
app.config['vector_index_to_exercise'] = vector_index_to_exercise

f = open('extra/jefit/data.json','rb')
raw_data = json.load(f)
app.config['raw_data'] = raw_data

# HTTP error handling
@app.errorhandler(404)
def not_found(error):
  return render_template("404.html"), 404

@app.route('/advanced', methods=['GET'])
def advanced():
  return render_template("advanced.html")
