from urllib.request import urlopen
import bs4 
import json
import time 

data = {}
counter = 0

for i in range(1, 131):
	html = urlopen('https://www.jefit.com/exercises/bodypart.php?id=11&exercises=All&All=0&Bands=0&Bench=0&Dumbbell=0&EZBar=0&Kettlebell=0&MachineStrength=0&MachineCardio=0&Barbell=0&BodyOnly=0&ExerciseBall=0&FoamRoll=0&PullBar=0&WeightPlate=0&Other=0&Strength=0&Stretching=0&Powerlifting=0&OlympicWeightLifting=0&Beginner=0&Intermediate=0&Expert=0&page=' + str(i))
	res = bs4.BeautifulSoup(html.read(),'html5lib')
	table = res.find(id='hor-minimalist_3')
	exercise = table.findAll("td", align="left")
	for e in exercise:
		theExercise = e.find("h3").getText()
		allParagraphs = e.findAll("p")
		theMuscle = allParagraphs[0].getText()
		theType = allParagraphs[1].getText()
		theEquipment = allParagraphs[2].getText()
		jsonOfData = {}
		jsonOfData["exercise"] = theExercise
		jsonOfData["muscle"] = theMuscle
		jsonOfData["type"] = theType
		jsonOfData["equipment"] = theEquipment
		data[counter] = jsonOfData
		counter +=1
	time.sleep(0.5) #dont bombard the website with our scraping.

with open('data.json', 'w') as outfile:
    json.dump(data, outfile)

