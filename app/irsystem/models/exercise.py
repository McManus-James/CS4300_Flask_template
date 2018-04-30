import pickle
import numpy as np
from numpy import linalg as LA
import os
import nltk
import re
from flask import current_app as app
import Levenshtein
from scipy.sparse.linalg import svds
from sklearn.preprocessing import normalize
# import matplotl/ib.pyplot as plt

class Exercise:

	alternate_spellings = {"quadriceps":"quads quad","quadricep":"quads quad","quads":"quad","quad":"quads",
	"latissimus":"lats lat","dorsi":"lats lat","lat":"lats","lats":"lat",
	"abdominal":"abs ab","abdominals":"abs ab","ab":"abs","abs":"ab",
	"deltoid":"delts delt","deltoids":"delts delt","delt":"delts","delts":"delt",
	"gluteus":"glutes glute","glute":"glutes","glutes":"glute",
	"bicep":"biceps","biceps":"bicep","bi":"biceps bicep","bis":"biceps bicep",
	"trapezius":"traps trap","traps":"trap","trap":"traps",
	"tricep":"triceps","triceps":"tricep","tri":"triceps tricep","tris":"triceps tricep"}

	@classmethod 
	def expanded_query(self, query):
		query_tokens = nltk.word_tokenize(query.lower())
		new_query_tokens = []
		for token in query_tokens:
			new_query_tokens.append(token)
			if token in self.alternate_spellings:
				new_query_tokens.append(self.alternate_spellings[token])
		new_query = ' '.join(new_query_tokens)
		return new_query


	@classmethod
	def simple_suggested(self, query):
		dics = [app.config['equipment_vocab_to_index'], app.config['muscles_vocab_to_index'], app.config['name_vocab_to_index'], app.config['description_vocab_to_index']]
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
		return ' '.join(suggested_query)

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
	def get_exercises(self, name = None, muscles = None, equipment = None, routine = None, difficulty=0):

		if muscles == None and equipment == None and routine == None:			#Place Holder for simple search check
			return self.simple_search(name)
		else:
			return self.advanced_search(name, muscles, equipment, routine, difficulty)

	@classmethod
	def simple_search(self, query, desc_w=.20, equip_w=.10, musc_w=.30, name_w=.15, rating_w = .25):
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

		ratings = []
		for i in range(len(sim_matrices[0])):
			eID = app.config['vector_index_to_exercise'][i]
			rating = app.config['raw_data'][eID]['rating']/100
			ratings.append([rating])
		sim_matrices.append( np.array(ratings) )

		weighted_sim = (desc_w*sim_matrices[0] + equip_w*sim_matrices[1] + musc_w*sim_matrices[2] + name_w*sim_matrices[3] + rating_w * sim_matrices[4])
		sorted_ind = np.argsort(weighted_sim, axis=0 )[::-1]

		top5rankingSort = sorted([i for index in sorted_ind[:5] for i in index], key= lambda x: app.config['raw_data'][app.config['vector_index_to_exercise'][int(x)]]['rating'], reverse = True)
		
		result = []
		for i in range(5):
			index = app.config['vector_index_to_exercise'][int(top5rankingSort[i])]
			entry = app.config['raw_data'][index]
			result.append(entry)
			pat = re.compile('\d+\.\)');
			newline = re.compile('\n')
			for r in result:
				r['description'] = re.sub(pat, '\n', r['description'])
		return result

	@classmethod
	def advanced_search(self, query, muscles = None, equipment = None, routine=False, difficulty=0, desc_w=.25, equip_w=.25, musc_w=.25, name_w=.25):
		dics = [app.config['description_vocab_to_index'], app.config['equipment_vocab_to_index'], app.config['muscles_vocab_to_index'], app.config['name_vocab_to_index']]
		tf_idfs = [app.config['desc_tfidf'], app.config['equip_tfidf'], app.config['muscles_tfidf'], app.config['name_tfidf']]

		# difficulty adjustments
		if difficulty == 0:
			query += ' easy'
			query += ' light'

		if difficulty == 0:
			query += ' medium'
			query += ' moderate'

		if difficulty == 0:
			query += ' hard'
			query += ' heavy'
			query += ' power'

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

		if not routine:
			return result

		# Machine Learning (SVD) to build a workout for a day
		if routine:
			if difficulty == None:
				difficulty =0
			ratings = np.zeros((1299,1))
			for i in range(len(app.config['raw_data'])):
				index = app.config['vector_index_to_exercise'][i]
				rating = (app.config['raw_data'][index]['rating'])
				ratings[i] = int(rating)
			xTr = np.concatenate((tf_idfs[0], tf_idfs[1], tf_idfs[2], tf_idfs[3], ratings/float(182)), axis=1)

			rating = np.zeros((1,1))
			rating[0] = ((3-int(difficulty))*50)/float(182)
			xTe = np.concatenate((query_vecs[0], query_vecs[1], query_vecs[2], query_vecs[3], rating), axis=1)

			words_compressed, s, docs_compressed = svds(xTr.T, k=15)

			docs_compressed = docs_compressed.transpose()
			docs_compressed = normalize(docs_compressed, axis = 1)
			xTe = normalize(xTe, axis = 1)


			xTe_projected = xTe.dot(words_compressed)
    		sims = docs_compressed.dot(xTe_projected.T)


    		sorted_ind = np.argsort(sims, axis=0 )[::-1]
    		result = []
    		i=0
    		while i<(5 + int(difficulty)):
    			index = app.config['vector_index_to_exercise'][int(sorted_ind[i])]
    			entry = app.config['raw_data'][index]
    			if 'stretch' in entry['name'].lower() or 'relaxation' in entry['name'].lower():
    				result = [entry] + result
    			else:
    				result.append(entry)
    			i+=1

		return result
