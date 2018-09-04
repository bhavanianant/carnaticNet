import requests
from bs4 import BeautifulSoup
import re
import collections
import pickle
import time
import numpy as np

#proxies = {'http': 'http://proxy-bos-v.fmr.com:8000'}




def isComposition(tag): #defining composition link as a link in the bulleted(numbered) list
	return (tag.name == 'a') and (tag.parent.name == 'li')


def get_data(pallavi, caranams, partOfSong, composerSites, lyrics, composer_id, vocab_dict):
	# map song ids to composition urls 
	song_mapping = {}

	# class label vector
	Y = []

	song_id = 0

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
				# add composition to mapping dict
				song_mapping[song_id] = composition

				line = stanzaFlag.next_sibling.contents[0].strip()
				stanza_words = re.findall(r'\w+', line)

				song_X = np.zeros((len(vocab_dict.keys())))
				for w in stanza_words:
					try:
						song_X[vocab_dict[w.lower()]] +=1
					except KeyError:
						pass

				# add to the X master table
				try:
					X = np.vstack((X, song_X))
				except:
					X = song_X

				# add class label to Y master table
				Y.append(composer_id[composer])

				# keep count across all composers for stats
				lyrics[composer].update(stanza_words)

				# update song_id
				song_id +=1


	return song_mapping, X, np.array(Y), lyrics



if __name__ == "__main__":
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

	composer_id = {
		"Thyagaraja":0,
		"ShyamaShaastri":1,
		"Ramadasu":2,
		"Annamayya":3
	}


	# read in vocab_dict
	vocab_dict = pickle.load( open( "vocab_dict.pkl", "rb" ) )

	song_mapping, X, Y, lyrics = get_data(pallavi, caranams, partOfSong, composerSites, lyrics, composer_id, vocab_dict)

	# pickle the lyrics dict for stats 
	pickle.dump( lyrics, open( "composer_lyrics.pkl", "wb" ) )

	# pickle the song mapping for analysis
	pickle.dump( song_mapping, open( "song_url_mapping.pkl", "wb") )

	# pickle the np arrays for net input
	X.dump("X_" + str(len(vocab_dict.keys())) + ".dat")
	Y.dump("Y_" + str(len(vocab_dict.keys())) + ".dat")
