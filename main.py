'''
main.py 
Casey Burns
6/30/2016
 - This program searches wikipedia pages for the first clickable
    word in the body of each page. It follows this hyperlink until 
    either diverging or reaching the Philosophy page. 
 - To run:
    $ python main.py [max path length] [iterations] [-vo]
    (the three arguments are optional)'''


import requests as reqs
import time
import sys
import common

# Get start time to time program
startTime = time.time()

# Dictionary of initial random article titles and path lengths
randomArticles = {}

# Dictionary of visited articles URL titles and path lengths 
#  that resolve to Philosophy page or diverge to minimize requests
visitedArticles = {}

# List of articles visited in current search; to be voided after
#  completion of each search, and current random article title
currentPath = []

# Boolean to turn on or off visual output
vo = False


def searchForHyperlink(respTxt, idx, mpl, randomTitle):
	'''The searchForHyperlink function is a recursive function that 
	takes a string argument respTxt, an integer argument idx, the max
	path length mpl, and the random article title that we are trying to 
	find the path for. It calls getURLTitle to retrieve the next URL,
	HTML requests this URL, and recursively calls itself if need be. Upon
	completion, it decides if the path converges to Philosophy or not.'''

	global randomArticles
	global visitedArticles
	global currentPath
	global vo

	# URL for non-random wiki pages
	wikiURL = 'https://en.wikipedia.org/wiki/'

	urlTitle = common.getURLTitle(respTxt[idx:])
	if vo:
		print 'Followed URL:', wikiURL + urlTitle

	if urlTitle.lower() == 'philosophy':
		# This path has converged to philosophy and is also a new path. Add the path 
		#  lenghts to visitedArticles and randomArticles
		if vo:
			print '>>>CONVERGENT<<<'
			print 'Path Length:', len(currentPath) + 1
		randomArticles[randomTitle] = len(currentPath) + 1
		addFullVisitedPath()
		currentPath = []
		return False

	elif urlTitle in visitedArticles and urlTitle != '' and visitedArticles[urlTitle] != -1:
		# We've visited this page before and it converges
		if vo:
			print '>>>CONVERGENT<<<'
			print 'Path Length:', len(currentPath) + visitedArticles[urlTitle] + 1
		randomArticles[randomTitle] = len(currentPath) + visitedArticles[urlTitle] + 1
		addVisitedPath(visitedArticles[urlTitle])
		currentPath = []
		return False

	elif len(currentPath) < mpl and urlTitle not in currentPath and urlTitle != '' and urlTitle not in visitedArticles:
		# Call searchForHyperlink function again with new URL
		#  Starting index idx will be at least 204 due to beginning of HTML file
		currentPath.append(urlTitle)
		response = reqs.get(wikiURL + urlTitle)
		diverges = searchForHyperlink(response.text, 204, mpl, randomTitle)
		return diverges
	else:
		# Path diverges
		if vo:
			print '>>>DIVERGENT<<<'
		addDivergentPath()
		currentPath = []
		return True




def addFullVisitedPath():
	'''addFullVisitedPath saves the length of the current path;
	pages in the path have not been visited before.'''

	global currentPath
	global visitedArticles

	for i in range(len(currentPath)):
		visitedArticles[currentPath[0]] = len(currentPath) 
		currentPath.pop(0)

	return


def addVisitedPath(addLength):
	'''addVisitedPath saves the length of the current path; 
	pages in the path have been visited before.'''

	global currentPath
	global visitedArticles
	
	for i in range(len(currentPath)):
		visitedArticles[currentPath[0]] = len(currentPath) + addLength + 1
		currentPath.pop(0)

	return

def addDivergentPath():
	'''addDivergentPath adds the url titles of divergent articles
	to visitedArticles as keys with values of -1'''

	global currentPath
	global visitedArticles

	for title in currentPath:
		visitedArticles[title] = -1

	return




if __name__ == '__main__':

	# Input syntax:
	#  $ python main.py [maxPathLength] [iterations] [-vo]
	maxPathLength, iterations, vo = common.parseCommandLineArgs(sys.argv)

	# Input stored path lengths from storedPathLengths.txt

	# URL for random wiki page
	randomWikiURL = 'https://en.wikipedia.org/wiki/Special:Random'

	for i in range(iterations):

		# Request random URL HTML
		response = reqs.get(randomWikiURL)

		# Get title of random article
		randomTitle, currentIdx = common.getArticleTitle(response.text)
		randomArticles[randomTitle] = 0

		if vo:
			print 'Random Article:', randomTitle

		# Search response text for next URL
		diverges = searchForHyperlink(response.text, currentIdx, maxPathLength, randomTitle)
		if diverges:
			randomArticles[randomTitle] = -1

	dc, cc, histo = common.calculateStats(randomArticles)


	runtime = time.time() - startTime
	common.printStats(dc, cc, histo, iterations, maxPathLength, runtime)


	
