from collections import defaultdict
import json

def main():
	with open("data.json", encoding="utf8") as data_file:
		exercises = json.load(data_file)
	with open("reviews.json", encoding = "utf8") as data_file:
		reviews = json.load(data_file)
	exercisesToRoutines = defaultdict(set)
	for k in reviews:
		for e in reviews[k]["exercises"]:
			exercisesToRoutines[e].add(k)
	
	for e in exercises:
		exerciseName = exercises[e]['name'] #at least one routine
		if exerciseName in exercisesToRoutines:
			totalvotes = 0
			totalRating = 0
			ranking = []
			for r in exercisesToRoutines[exerciseName]:
				votes = reviews[r]["votes"]
				rating = votes * reviews[r]["rating"]
				totalvotes += votes
				totalRating += rating
				ranking.append( (r, rating) )
			weightedRating = totalRating/totalvotes
			top5 = [rid for (rid, contribution) in sorted(ranking, key=lambda x: x[1], reverse = True)[:5]]
			exercises[e]["rating"] = weightedRating
			exercises[e]["top5Routines"] = top5
		else: #no routines include this..
			exercises[e]["rating"] = 0
			exercises[e]["top5Routines"] = []

	with open('data.json', 'w') as outfile:
		json.dump(exercises, outfile)



if __name__ == "__main__":
    main()