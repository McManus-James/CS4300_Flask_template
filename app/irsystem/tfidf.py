import json


def build_vectorizer(max_features, stop_words, max_df=0.8, min_df=10, norm='l2'):
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
    data = json.load(open('data.json'))
    for exercise in data:
        name.append(exercise['name'])
        muscles.append(exercise['muscles'])
        equipment.append(exercise['equipment'])
        description.append(exercise['description'])
    tf_idf_vec = TfidfVectorizer(input=name, stop_words= stop_words, max_df= max_df, min_df= min_df, max_features= max_features, norm= norm)
    return tf_idf_vec


