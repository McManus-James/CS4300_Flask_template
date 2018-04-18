import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer


datajson = json.load(open('jefit/data.json'))

data = []
vector_index_to_exercise = {} #takes the index of the vector for an exercise in the tfidf matrix and returns the exercise
i = 0
for key, value in datajson.iteritems():
    data.append(value)
    vector_index_to_exercise[i] = key
    i += 1

vector_index_to_exercise_file = open("pickles/vector_index_to_exercise",'wb')
pickle.dump(vector_index_to_exercise, vector_index_to_exercise_file)
vector_index_to_exercise_file.close()

def build_vectorizer(max_features, stop_words, max_df=1.0, min_df=1, norm='l2'):
    """Returns a TfidfVectorizer object
    
    Params: {max_features: Integer,
             max_df: Float,
             min_df: Float,
             norm: String,
             stop_words: String}
    Returns: TfidfVectorizer
    """
    # YOUR CODE HERE
    name = []
    muscles = []
    equipment = []
    description = []
    #etype = []
    for exercise in data:
        name.append(exercise['name'])
        muscles.append(" ".join(exercise['muscles']))
        equipment.append(" ".join(exercise['equipment']))
        description.append(exercise['description'])
        #etype.append(exercise['exerciseType'])

    tf_idf_vec_name = TfidfVectorizer(input=name, max_df= max_df, min_df= min_df, max_features= max_features, norm= norm)
    tf_idf_vec_muscles = TfidfVectorizer(input=name, max_df= max_df, min_df= min_df, max_features= max_features, norm= norm)
    tf_idf_vec_equipment = TfidfVectorizer(input=name, max_df= max_df, min_df= min_df, max_features= max_features, norm= norm)
    tf_idf_vec_description = TfidfVectorizer(input=name, max_df= max_df, min_df= min_df, max_features= max_features, norm= norm)
    #tf_idf_vec_type = TfidfVectorizer(input=etype, stop_words= stop_words, max_df= max_df, min_df= min_df, max_features= max_features, norm= norm)
    return (tf_idf_vec_name, tf_idf_vec_muscles, tf_idf_vec_equipment, tf_idf_vec_description)

tfidf_vecs = build_vectorizer(5000, "english")
name_by_vocab = tfidf_vecs[0].fit_transform([exercise['name'] for exercise in data]).toarray()
muscle_by_vocab = tfidf_vecs[1].fit_transform([" ".join(exercise['muscles']) for exercise in data]).toarray() 
equipment_by_vocab = tfidf_vecs[2].fit_transform([" ".join(exercise['equipment']) for exercise in data]).toarray() 
desc_by_vocab = tfidf_vecs[3].fit_transform([exercise['description'] for exercise in data]).toarray()
#type_by_vocab = tfidf_vecs[4].fit_transform([" ".join(exercise['exerciseType']) for exercise in data]).toarray()


name_tfidf = open("pickles/name_tfidf",'wb')
muscles_tfidf = open("pickles/muscles_tfidf",'wb')
equipment_tfidf = open("pickles/equipment_tfidf",'wb')
desc_tfidf = open("pickles/description_tfidf",'wb')

pickle.dump(name_by_vocab, name_tfidf)
name_tfidf.close()
pickle.dump(muscle_by_vocab, muscles_tfidf)
muscles_tfidf.close()
pickle.dump(equipment_by_vocab, equipment_tfidf)
equipment_tfidf.close()
pickle.dump(desc_by_vocab, desc_tfidf)
desc_tfidf.close()

name_vocab_to_index = {v:i for i, v in enumerate(tfidf_vecs[0].get_feature_names())} #takes a word and gives the index of it in the name tfidf matrix
muscles_vocab_to_index = {v:i for i, v in enumerate(tfidf_vecs[1].get_feature_names())} #takes a word and gives the index of it in the muscles tfidf matrix
print(muscles_vocab_to_index.keys())
equipment_vocab_to_index = {v:i for i, v in enumerate(tfidf_vecs[2].get_feature_names())} #takes a word and gives the index of it in the equipment tfidf matrix
desc_vocab_to_index = {v:i for i, v in enumerate(tfidf_vecs[3].get_feature_names())} #takes a word and gives the index of it in the description tfidf matrix

name_vocab_to_index_file = open("pickles/name_vocab_to_index",'wb')
muscles_vocab_to_index_file = open("pickles/muscles_vocab_to_index",'wb')
equipment_vocab_to_index_file = open("pickles/equipment_vocab_to_index",'wb')
desc_vocab_to_index_file = open("pickles/description_vocab_to_index",'wb')

pickle.dump(name_vocab_to_index, name_vocab_to_index_file)
name_vocab_to_index_file.close()
pickle.dump(muscles_vocab_to_index, muscles_vocab_to_index_file)
muscles_vocab_to_index_file.close()
pickle.dump(equipment_vocab_to_index, equipment_vocab_to_index_file)
equipment_vocab_to_index_file.close()
pickle.dump(desc_vocab_to_index, desc_vocab_to_index_file)
desc_vocab_to_index_file.close()



