from collections import defaultdict
import json

def main():
	with open("data.json", encoding="utf8") as data_file:
		exercises = json.load(data_file)
	with open("reviews.json", encoding = "utf8") as data_file:
		reviews = json.load(data_file)
	for k in exercises:
		newtop5 = []
		for rid in exercises[k]["top5Routines"]:
			rname = reviews[rid]['name']
			rurl = reviews[rid]['url']
			entry = {"routineName": rname, "routineURL": rurl, "routineID": rid}
			newtop5.append(entry)
		exercises[k]["top5Routines"] = newtop5


	with open('data.json', 'w') as outfile:
		json.dump(exercises, outfile)



if __name__ == "__main__":
    main()