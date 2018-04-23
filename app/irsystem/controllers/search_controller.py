from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app.irsystem.models.exercise import Exercise

project_name = "Exercise Planner"
net_id = "James McManus: jjm439, Kristian Langholm: krl38, Faadhil Moheed: fm363, Darien Lin: dl724, Jatin Bharwani: jsb399"

@irsystem.route('/', methods=['GET'])
def search():
  query = request.args.get('search')
  if not query:
    data = []
    output_message = ''
  else:
    output_message = "Your search: " + query
    data = Exercise.get_exercises(name = query)
  return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)

datajson = json.load(open('././extra/jefit/data.json'))
data = datajson.values()
m_options = []
e_options = []
for exercise in data:
  for m in exercise['muscles']:
    m_options.append(m)
  for e in exercise['equipment']:
    e_options.append(e)

@irsystem.route('advanced', methods=['GET'])
def advanced():
  query = request.args.get('search')
  muscles = request.args.getlist('muscles')
  equipment = request.args.getlist('equipment')
  routine = request.args.get('routine')
  difficulty = request.args.get('difficulty')
  print difficulty
  if not query and not muscles and not equipment:
    data = []
    output_message = ''
  else:
    output_message = "Your search: " + query
    data = Exercise.get_exercises(name = query, muscles=muscles, equipment=equipment, routine=routine, difficulty=difficulty)
  return render_template("advanced.html", muscles=sorted(set(m_options)), equipment=sorted(set(e_options)),
    output_message=output_message, data=data)