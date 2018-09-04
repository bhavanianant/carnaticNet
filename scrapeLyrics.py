import requests
from bs4 import BeautifulSoup
import re
import collections
import pickle
import time

#proxies = {'http': 'http://proxy-bos-v.fmr.com:8000'}

pallavi = "\s[pP]allavi"
caranams = "\s[cC]ara[nN]am"
partOfSong = pallavi

composerSites = {
	"Thyagaraja":"http://www.karnatik.com/co1006.shtml",
	"ShyamaShaastri":"http://www.karnatik.com/co1005.shtml",
	"Ramadasu":"http://www.karnatik.com/co1015.shtml",
	"Annamayya":"http://www.karnatik.com/co1010.shtml"
}

lyrics = {
	"Thyagaraja":collections.Counter(),
	"ShyamaShaastri":collections.Counter(),
	"Ramadasu":collections.Counter(),
	"Annamayya":collections.Counter()
}

def isComposition(tag): #defining composition link as a link in the bulleted(numbered) list
	return (tag.name == 'a') and (tag.parent.name == 'li')

for composer in composerSites.iterkeys():
	#composerPage = requests.get(composerSites[composer], proxies=proxies)
	composerPage = ""
	while composerPage == "":
		try:
			composerPage = requests.get(composerSites[composer])
		except requests.exceptions.ConnectionError:
			time.sleep(5)


	if(composerPage.status_code != 200):
		print "Error: could not get webpage: " + composerSites[composer] + "(" + composer + ")"
		break
	composerSoup = BeautifulSoup(composerPage.content, 'html.parser')
	compositions = composerSoup.find_all(isComposition)
	if compositions == [] :
		print "Error: could not scrape compositions webpages"+ composerSites[composer] + "(" + composer + ")"
		break
	compositions = map(lambda c: "http://www.karnatik.com/" + c['href'], compositions)



	for composition in compositions:
		#songPage = requests.get(composition, proxies=proxies)
		songPage = ""
		while songPage == "":
			try:
				songPage = requests.get(composition)
			except requests.exceptions.ConnectionError:
				time.sleep(5)
		
		if(songPage.status_code != 200):
			print "Error: could not get webpage: " + composition
			continue
		songSoup = BeautifulSoup(songPage.content, 'html.parser')
		stanzaFlag = songSoup.find(string=re.compile(partOfSong))
		if(stanzaFlag == None):
			print "Error: could not find stanza flag: " + partOfSong
		else:
			line = stanzaFlag.next_sibling.contents[0].strip()
			lyrics[composer].update(re.findall(r'\w+', line))


for composer in lyrics.iterkeys():
	print composer
	print lyrics[composer].most_common(10)


# pickle the dictionary 
pickle.dump( lyrics, open( "composer_lyrics.pkl", "wb" ) )