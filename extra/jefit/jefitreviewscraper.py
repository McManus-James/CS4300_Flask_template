from urllib.request import urlopen
import bs4 
import json
import time 


data = {}
baseLinkRoutine = "https://www.jefit.com/routines/"
routinePage = "https://www.jefit.com/routines/?name=1&tag=1&keyword=0&gender=0&sort=2&search=&page="
def main():

	#load data.json first.
	with open('data.json', encoding="utf8") as data_file:    
		exercisesParsed = json.load(data_file)
	names = [exercisesParsed[k]["name"] for k in exercisesParsed]
	global exercises; exercises = set(names)
	#finish loading
	counter = 0 
	page = 1
	dontStop = True
	while dontStop:
		html = urlopen( routinePage + str(page) )
		res = bs4.BeautifulSoup(html.read(),'html5lib')
		table = res.find(id='hor-minimalist_3').find("tbody")
		routine = table.findAll("tr")
		for r in routine:
			try:
				keepGoing, add = getInformation(r, counter)
				if not keepGoing:
					dontStop = keepGoing
					break
				counter += add
			except:
				pass
		page +=1
		time.sleep(0.5) #dont bombard the website with our scraping.

	with open('reviews.json', 'w') as outfile:
		json.dump(data, outfile)

def getInformation(row, idRoutine):
	#return true if views > 1000. false otherwise. We are sorting by views. can skip alot of bad routines.
	print(idRoutine)

	details = row.findAll("td", align="center")
	frequency = details[0].getText().strip() #json field
	routineType = details[1].getText().strip() #json field
	difficulty = details[2].getText().strip() #json field
	downloads = int( details[3].getText().strip() ) #json field
	views = int( details[4].getText().strip() ) #json field
	if views < 1000: 
		return (False, 0)
	name = 	row.findAll("span", {'class' :'xlink'})[1].find("a").getText().strip()
	url = baseLinkRoutine + row.findAll("span", {'class' :'xlink'})[1].find("a").get("href") #json field
	print(url)
	html = urlopen(url)
	res = bs4.BeautifulSoup(html.read(), 'html5lib')
	tableContainer = res.findAll("td", {"class": "MiddleColumn"})[0]
	votesSentences = tableContainer.findAll(id="hor-minimalist_2")[1].find("tbody").find("tr").findAll("td")[1].findAll("p")[-2].getText().strip()
	votesCount = [int(w) for w in votesSentences.split() if w.isnumeric()][0] #json field
	if (votesCount < 10): #less than 10 votes, stop looking, move on. only consider at least 10 votes.
		return (True, 0) 

	#else we gotta add to data..
	rating = int(tableContainer.find(id="starUser0").getText().strip()) #json field

	workouts = set()
	days = res.findAll(id = "hor-minimalist_3")
	for day in days:
		workout = day.find("table", {"class" : "InnerTable"}).findAll("tr")
		if len(workout) == 0:
			continue
		workout = workout[1:]
		for ex in workout:
			getName=ex.findAll("td", align="left")[1].getText().strip()
			if(getName in exercises):
				workouts.add(getName)
	workouts = list(workouts)
	jsonofData = {}
	jsonofData["name"] = name
	jsonofData["frequency"] = frequency
	jsonofData["routineType"] = routineType
	jsonofData["difficulty"] = difficulty
	jsonofData["downloads"] = downloads
	jsonofData["views"] = views
	jsonofData["url"]	= url
	jsonofData["votes"]	= votesCount
	jsonofData["exercises"] = workouts
	jsonofData["rating"] = rating
	data[idRoutine] = jsonofData
	return(True, 1)
	
if __name__ == "__main__":
	main()




