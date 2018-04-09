from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app.irsystem.models.exercise import Exercise

project_name = "Ilan's Cool Project Template"
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



