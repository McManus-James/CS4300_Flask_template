from flask import Blueprint
from app.irsystem.models.exercise import Exercise

# Define a Blueprint for this module (mchat)
irsystem = Blueprint('irsystem', __name__, url_prefix='/',static_folder='static',template_folder='templates')
# Import all controllers
from controllers.search_controller import *
