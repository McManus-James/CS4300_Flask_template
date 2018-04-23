import pickle
import numpy as np
from numpy import linalg as LA
import os
import nltk
import re
from flask import current_app as app
import Levenshtein

class Exercise:

	@classmethod
	def simple_suggested(self, query):
		dics = [app.config['equipment_vocab_to_index'], app.config['muscles_vocab_to_index'], app.config['name_vocab_to_index']]
		top_words = []
		for dic in dics:
			top_words.extend(dic.keys())
		query_tokens = nltk.word_tokenize(query.lower())
		suggested_query = []
		for token in query_tokens:
			top_suggestion = token
			max_distance = 3 #can be subbed for anything
			for word in top_words:
				if Levenshtein.distance(token, word) <= max_distance:
					top_suggestion = word
					max_distance = Levenshtein.distance(token, word)
			suggested_query.append(top_suggestion)
		return ''.join(suggested_query)

	# @classmethod
	# def advanced_suggested(self, query, muscles, equipment, routine):
	# 	dics = [app.config['equipment_vocab_to_index'], app.config['muscles_vocab_to_index'], app.config['name_vocab_to_index']]
	# 	fields = (nltk.word_tokenize(query), dics[2]), (muscles, dics[1]), (equipment, dics[0])
	# 	suggested_fields = []
	# 	for field_tokens in fields:
	# 		suggested_query = []
	# 		for token in field_tokens:
	# 			top_suggestion = token
	# 			max_distance = 3 #can be subbed for anything
	# 			for word in field[1].keys():
	# 				if Levenshtein.distance(token, word) <= max_distance:
	# 					top_suggestion = word
	# 					max_distance = Levenshtein.distance(token, word)
	# 			suggested_query.append(top_suggestion)
	# 		suggested_fields.append(suggested_query)


	@classmethod
	#Search method. Simple search takes in name parameter as query and
	#searches name, then muscles, then description, then equipment needed
	#for matches. Advanced search searches each parameter individually and
	#returns exercises which match each criteria (intersection). Routine
	#determines whether to return individual exercises or a routine
	# comment
	def get_exercises(self, name = None, muscles = None, equipment = None, routine = None):

		if muscles == None and equipment == None and routine == None:			#Place Holder for simple search check
			return self.simple_search(name)
		else:
			return self.advanced_search(name, muscles, equipment, routine)

	@classmethod
	def simple_search(self, query, desc_w=.25, equip_w=.25, musc_w=.25, name_w=.25):
		dics = [app.config['description_vocab_to_index'], app.config['equipment_vocab_to_index'], app.config['muscles_vocab_to_index'], app.config['name_vocab_to_index']]
		tf_idfs = [app.config['desc_tfidf'], app.config['equip_tfidf'], app.config['muscles_tfidf'], app.config['name_tfidf']]

		query_tokens = nltk.word_tokenize(query.lower())
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
		sorted_ind = np.argsort(weighted_sim, axis=0 )[::-1]

		result = []
		for i in range(5):
			index = app.config['vector_index_to_exercise'][int(sorted_ind[i])]
			entry = app.config['raw_data'][index]
			result.append(entry)
			pat = re.compile('\d+\.\)');
			newline = re.compile('\n')
			for r in result:
				r['description'] = re.sub(pat, '\n', r['description'])
		return result

	@classmethod
	def advanced_search(self, query, muscles = None, equipment = None, routine=False, desc_w=.1, equip_w=.3, musc_w=.4, name_w=.2):
		dics = [app.config['description_vocab_to_index'], app.config['equipment_vocab_to_index'], app.config['muscles_vocab_to_index'], app.config['name_vocab_to_index']]
		tf_idfs = [app.config['desc_tfidf'], app.config['equip_tfidf'], app.config['muscles_tfidf'], app.config['name_tfidf']]

		name_tokens = []
		name_tokens = nltk.word_tokenize(query.lower())

		muscle_tokens = []
		if muscles != None:
			for m in muscles:
				muscle_tokens.extend(nltk.word_tokenize(m.lower()))

		equipment_tokens = []
		if equipment != None:
			for e in equipment:
				equipment_tokens.extend(nltk.word_tokenize(e.lower()))


		desc_tokens = name_tokens + muscle_tokens + equipment_tokens

		query_tokens = [desc_tokens, equipment_tokens, muscle_tokens, name_tokens]
		query_vecs = []
		for i, dic in enumerate(dics):
			q_vec = np.zeros((len(dic),1))
			for t in query_tokens[i]:
				if t in dic:
					q_vec[dic[t]] += 1.0
			query_vecs.append(q_vec)

		for i in range(len(tf_idfs)):
			cpy = np.copy(tf_idfs[i])
			cpy[cpy > 0.0] = 1
			df = np.sum(cpy, axis=0)
			df.reshape(df.shape[0] , 1)
			query_vecs[i] = np.multiply(query_vecs[i].T, np.log(1299 / (1+df)))


		if all([np.count_nonzero(x) == 0 for x in query_vecs]):
			return "No_Valid_Query_Terms".split()

		sim_matrices = []
		for i in range(len(tf_idfs)):
			sim_matrices.append(np.dot(tf_idfs[i], query_vecs[i].T))

		weighted_sim = (desc_w*sim_matrices[0] + equip_w*sim_matrices[1] + musc_w*sim_matrices[2] + name_w*sim_matrices[3])
		sorted_ind = np.argsort(weighted_sim, axis=0 )[::-1]

		result = []
		for i in range(5):
			index = app.config['vector_index_to_exercise'][int(sorted_ind[i])]
			entry = app.config['raw_data'][index]
			result.append(entry)

		return result


