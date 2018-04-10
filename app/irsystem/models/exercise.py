class Exercise:

	@classmethod
	#Search method. Simple search takes in name parameter as query and 
	#searches name, then muscles, then description, then equipment needed
	#for matches. Advanced search searches each parameter individually and
	#returns exercises which match each criteria (intersection). Routine 
	#determines whether to return individual exercises or a routine
	def get_exercises(self, name = None, muscles = None, equipment = None, routine = None):
		return name.split()