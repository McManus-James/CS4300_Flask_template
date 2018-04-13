import pickle
import numpy as np
from numpy import linalg as LA
import os
import nltk
from flask import current_app as app


class Exercise:

	@classmethod
	#Search method. Simple search takes in name parameter as query and
	#searches name, then muscles, then description, then equipment needed
	#for matches. Advanced search searches each parameter individually and
	#returns exercises which match each criteria (intersection). Routine
	#determines whether to return individual exercises or a routine
	def get_exercises(self, name = None, muscles = None, equipment = None, routine = None):

		if True:			#Place Holder for simple search check 
			return self.simple_search(name)
		else:
			return advance_search(name, muscles, equipment, routine)

	@classmethod
	def simple_search(self, query, desc_w=.25, equip_w=.25, musc_w=.25, name_w=.25):
		# print app.config['desc_tfidf'].shape
		# print app.config['equip_tfidf'].shape
		# print app.config['muscles_tfidf'].shape
		# print app.config['name_tfidf'].shape
		# print len(app.config['description_vocab_to_index'])
		# print len(app.config['equipment_vocab_to_index'])
		# print len(app.config['muscles_vocab_to_index'])
		# print len(app.config['name_vocab_to_index'])
		# print len(app.config['vector_index_to_exercise'])
		dics = [app.config['description_vocab_to_index'], app.config['equipment_vocab_to_index'], app.config['muscles_vocab_to_index'], app.config['name_vocab_to_index']]
		tf_idfs = [app.config['desc_tfidf'], app.config['equip_tfidf'], app.config['muscles_tfidf'], app.config['name_tfidf']]
		query_tokens = nltk.word_tokenize(query)
		query_vecs = []
		for dic in dics:
			q_vec = np.zeros((len(dic),1))
			for t in query_tokens:
				if t in dic: 
					q_vec[dic[t]] += 1.0
			query_vecs.append(q_vec)
		
		for i in range(len(tf_idfs)):
			cpy = np.copy(tf_idfs[i])
			cpy[cpy > 0.0] = 1
			df = np.sum(cpy, axis=0)
			df.reshape(df.shape[0] , 1)
			query_vecs[i] = np.multiply(query_vecs[i].T, np.log(1299 / (1+df)))
			# print query_vecs[i].shape

		if all([np.count_nonzero(x) == 0 for x in query_vecs]):
			return "No_Valid_Query_Terms".split()

		sim_matrices = []
		for i in range(len(tf_idfs)):
			sim_matrices.append(np.dot(tf_idfs[i], query_vecs[i].T)) 

		weighted_sim = (desc_w*sim_matrices[0] + equip_w*sim_matrices[1] + musc_w*sim_matrices[2] + name_w*sim_matrices[3])
		sorted_ind = np.argsort(weighted_sim, axis=0)[::-1]

		result = []
		for i in range(10):	
			index = app.config['vector_index_to_exercise'][int(sorted_ind[i])]
			entry = app.config['raw_data'][index]
			result.append(entry['name'])

		return result