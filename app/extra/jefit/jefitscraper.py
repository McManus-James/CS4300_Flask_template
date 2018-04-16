from urllib.request import urlopen
import bs4 
import json
import time 


data = {}
imageBaseLink = "https://www.jefit.com/images/exercises/"
baseLinkExercise = "https://www.jefit.com/exercises/"

def main():
	counter = 0
	for i in range(1, 131):
		html = urlopen('https://www.jefit.com/exercises/bodypart.php?id=11&exercises=All&All=0&Bands=0&Bench=0&Dumbbell=0&EZBar=0&Kettlebell=0&MachineStrength=0&MachineCardio=0&Barbell=0&BodyOnly=0&ExerciseBall=0&FoamRoll=0&PullBar=0&WeightPlate=0&Other=0&Strength=0&Stretching=0&Powerlifting=0&OlympicWeightLifting=0&Beginner=0&Intermediate=0&Expert=0&page=' + str(i))
		res = bs4.BeautifulSoup(html.read(),'html5lib')
		table = res.find(id='hor-minimalist_3')
		exercise = table.findAll("td", align="center")
		for e in exercise:
			href = baseLinkExercise + e.find("a").get('href')
			getInformation(href, counter)
			counter +=1
	time.sleep(0.5) #dont bombard the website with our scraping.

	with open('data.json', 'w') as outfile:
		json.dump(data, outfile)

def getInformation(url, idExercise):
		print(idExercise)
		html = urlopen(url)
		res = bs4.BeautifulSoup(html.read(), 'html5lib')
		tableContainer = res.findAll("td",{"class": "MiddleColumn"})
		allHorMinimalist2 = tableContainer[0].findAll(id="hor-minimalist_2")
		exerciseName = (allHorMinimalist2[0].find("thead").find("tr").getText()).strip()
		numImages = len(allHorMinimalist2[0].find("tbody").findAll("td")[0].findAll("img")) + len(allHorMinimalist2[0].find("tbody").findAll("td")[1].findAll("img"))
		imageLink = []
		try:
			for i in allHorMinimalist2[0].find("tbody").findAll("td")[0].findAll("img"):
				link = imageBaseLink + "/".join(i['src'].split("/")[-2:])
				imageLink.append(link)
			for i in allHorMinimalist2[0].find("tbody").findAll("td")[1].findAll("img"):
				link = imageBaseLink + "/".join(i['src'].split("/")[-2:])
				imageLink.append(link)
		except:
			#get as many images as possible 
			pass
		if numImages < 3:
			musclesContainer = allHorMinimalist2[0].find("tbody").find("tr").findAll("p")
			descriptionContainer = allHorMinimalist2[1].find("td").getText() #the same id unfortunately..
		else: 
			musclesContainer = allHorMinimalist2[1].find("tbody").find("tr").findAll("p")
			descriptionContainer = allHorMinimalist2[2].find("td").getText() #the same id unfortunately..
		musclegroups = []
		equipment = []	
		exerciseType = ""
		for p in musclesContainer:
			paraText = p.getText()
			if "Muscle" in paraText:
				_, muscles = paraText.split(":")
				trimmed = [x.strip() for x in muscles.split(",")]
				musclegroups += trimmed
			elif "Equipment" in paraText:
				_, equipmentNeed = paraText.split(":")
				trimmed = [x.strip() for x in equipmentNeed.split(",") ]
				removeBodyOnly = [x for x in trimmed if x != "Body Only"]
				equipment += removeBodyOnly
			elif "Type" in paraText:
				_, exerciseType = paraText.split(":")
				exerciseType = exerciseType.strip()
		
		
		if "Steps :" in descriptionContainer:
			part1,part2 = descriptionContainer.split("Steps :")
			descriptionContainer = part1 + part2
		description = "".join(descriptionContainer.split("\n"))
		musclegroups = set(musclegroups)
		musclegroups = list(musclegroups)
		jsonOfData = {}
		jsonOfData["name"] = exerciseName
		jsonOfData["muscles"] = musclegroups
		jsonOfData["exerciseType"] = exerciseType
		jsonOfData["equipment"] = equipment
		jsonOfData["description"] = description
		jsonOfData["image"] = imageLink

		data[idExercise] = jsonOfData
		
if __name__ == "__main__":
	main()




