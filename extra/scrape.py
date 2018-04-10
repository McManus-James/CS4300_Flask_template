import requests
import json
import pprint

url = "https://wger.de/api/v2/exercise/?ordering=id&status=2&language=2"
# url = "https://wger.de/api/v2/exerciseinfo/3/"

data = {"key": "value"}
headers = {'Accept': 'application/json', 'Authorization': 'Token 694bf3e087521decb25e1d7644b0c476e4d9ae81'}

# Get first page
r = requests.get(url, auth=('fmoheed', 'password'), params=data, headers=headers)
page_count = 1
with open('data/data_page_' + str(page_count) + '.text', 'w') as f:
	f.write(pprint.pformat(r.json()))
f.close()

# Loop through other pages, get other data
while r.json()['next'] != None:
	page_count += 1
	print("Page: {}".format(page_count))

	url = r.json()['next']
	r = requests.get(url, auth=('fmoheed', 'password'), params=data, headers=headers)

	with open('data/data_page_' + str(page_count) + '.txt', 'w') as f:
		f.write(pprint.pformat(r.json()))
	f.close()