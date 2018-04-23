from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app.irsystem.models.exercise import Exercise

project_name = "Exercise Planner"
net_id = "James McManus: jjm439, Kristian Langholm: krl38, Faadhil Moheed: fm363, Darien Lin: dl724, Jatin Bharwani: jsb399"

# AUTOCOMPLETE DATA
datajson = json.load(open('././extra/jefit/data.json'))
data = datajson.values()
m_options = []
e_options = []
auto_list = []
for exercise in data:
  for m in exercise['muscles']:
    m_options.append(m)
    auto_list.append(m)
  for e in exercise['equipment']:
    e_options.append(e)
    auto_list.append(e)
  
  auto_list.append(exercise['name'])

# Make set
auto_set = list(set(auto_list))

@irsystem.route('/', methods=['GET'])
def search():
  query = request.args.get('search')
  option = ''
  if not query:
    data = []
    output_message = ''
  else:
    output_message = "Your search was: " + query
    suggest = request.args.get('suggest')
    data = Exercise.get_exercises(name = query)
    if suggest != "false":
      suggested = Exercise.simple_suggested(query)
      if (suggested != query):
        output_message = "Currently searching for: " + suggested
        option = query
        data= Exercise.get_exercises(name = suggested)

  return render_template('search.html', name=project_name, netid=net_id, original_query=option, output_message=output_message, data=data, autocomplete=auto_set)

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