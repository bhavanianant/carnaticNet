import requests
from bs4 import BeautifulSoup
import re
import collections
from time import sleep


pallavi = "\s[pP]allavi"        #meaning: "chorus"
caranams = "\s[cC]ara[nN]am"    #meaning: "verse"
partOfSong = pallavi            #Choruses/refrains were analyzed in this demo

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
	composerPage = requests.get(composerSites[composer], verify=False)
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
		songPage = requests.get(composition, verify=False)
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
        sleep(5)

for composer in lyrics.iterkeys():
	print composer
	print lyrics[composer].most_common(10)
