#! /usr/bin/env python

import git
import requests
from bs4 import BeautifulSoup

#Get the Spamhaus website
data = requests.get('https://www.spamhaus.org/statistics/tlds/')

#Parse the hrml
soup = BeautifulSoup(data.text, 'html.parser')

#Find the subtitle class (the only class that has the tld data)
resultsRow = soup.find_all('span', {'class': 'subtitle'})

results = []

for resultRow in resultsRow:
    #Get the text object which is the tld
    tld = resultRow.text
    #Append that tld to an array
    results.append(tld)

print(results)

tlds = ""
f = open("/home/ubuntu/spamhaus/spamhaus/bad_tlds","w")
for ele in results:
    tlds += ele + "\n"
f.write(tlds)
f.close()

repo = git.Repo("/home/ubuntu/spamhaus/spamhaus")
#repo.git.pull()
repo.git.add("/home/ubuntu/spamhaus/spamhaus/bad_tlds")
repo.git.commit("-m", "updated bad_tlds", author="xxxxxxx@xxxxxxx.com")
repo.git.push()
