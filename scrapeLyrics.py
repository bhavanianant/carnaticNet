import requests
from bs4 import BeautifulSoup
import re
import collections

proxies = {'http': 'http://proxy-bos-v.fmr.com:8000'}

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
	composerPage = requests.get(composerSites[composer], proxies=proxies)
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
		# composition = compositions[0]
		# print composition
		songPage = requests.get(composition, proxies=proxies)
		# print songPage
		if(songPage.status_code != 200):
			print "Error: could not get webpage: " + composition
			continue
		songSoup = BeautifulSoup(songPage.content, 'html.parser')
		# print songSoup.prettify()
		stanzaFlag = songSoup.find(string=re.compile(partOfSong))
		# print stanzaFlag
		if(stanzaFlag == None):
			print "Error: could not find stanza flag: " + partOfSong
		else:
			# type(stanzaFlag)
			line = stanzaFlag.next_sibling.contents[0].strip()
			# print type(line)
			lyrics[composer].update(re.findall(r'\w+', line))
		# line = songSoup.find(string=re.compile(pallavi)).next_sibling.contents[0].strip()
		# lyrics[composer].update(re.find_all(r'\w+', line.lower()))


print "Thyagaraja: " 
print lyrics["Thyagaraja"].most_common(10)
print "ShyamaShaastri: " 
print lyrics["ShyamaShaastri"].most_common(10)
print "Ramadasu: "
print lyrics["Ramadasu"].most_common(10)
print "Annamayya: "
print lyrics["Annamayya"].most_common(10)
