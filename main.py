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
import numpy as np
import pylab as pl

# Get start time to time program
startTime = time.time()

# Dictionary of initial random article titles and path lengths
randomArticles = {}

# Dictionary of visited articles URL titles and path lengths 
#  that resolve to Philosophy page to minimize HTML requests
visitedArticles = {}

# List of articles visited in current search; to be voided after
#  completion of each search, and current random article title
currentPath = []

# Boolean to turn on or off visual output
vo = False


def getArticleTitle(respTxt):
	'''The getArticleTitle function takes a string argument respTxt 
	that holds the HTML text of a wikipedia webpage. It iteratively
	searches through characters of respTxt to find the <title> tag
	and extracts the title as a string, storing this string as a key
	in the randomArticles dictionary with an initial value of 0'''

	# i begins at index space 101 because the first 101 characters
	#  of respTxt are always the same. The title text begins at this
	#  index.
	i = 101

	for character in respTxt[i:]:
		if respTxt[i:i+8] == '</title>':
			# end of title tag, the previous 35 characters are 
			#  ' - Wikipedia, the free encyclopedia' and we don't 
			#  want to store them.
			randomTitle = respTxt[101:i-35]
			randomArticles[randomTitle] = 0
			break
		i = i + 1

	# i+76 will be the index at which to begin our hyperlink search
	#  due to consistency of beginning of HTML 
	return randomTitle, (i+76)


def getURLTitle(respTxt):
	'''getURLTitle takes the html text of a wiki article as its argument
	argument and returns the extension (EXT as in en.wikipedia.org/wiki/EXT)
	of the correct wiki article to follow next'''

	i = 0
	span = 0
	table = 0
	italic = 0
	parentheses = 0
	div = 0

	while True:
		if respTxt[i:i+25] == '<div id="mw-content-text"':
			# Correct section to find article HTML
			i = i + 25

			while True:
				# Check for incorrect sections of HTML
				if respTxt[i:i+5] == '<span':
					span = span + 1
					i = i + 4
				elif respTxt[i:i+7] == '</span>':
					span = span - 1
					i = i + 6
				elif respTxt[i:i+6] == '<table':
					table = table + 1
				 	i = i + 5
				elif respTxt[i:i+8] == '</table>' and table > 0:
				 	table = table - 1
				 	i = i + 7
				elif respTxt[i:i+3] == '<i>':
					italic = italic + 1
					i = i + 2
				elif respTxt[i:i+4] == '</i>':
					italic = italic - 1
					i = i + 3
				elif respTxt[i:i+1] == '(':
					parentheses = parentheses + 1
				elif respTxt[i:i+1] == ')' and parentheses > 0:
					parentheses = parentheses - 1
				elif respTxt[i:i+4] == '<div':
					div = div + 1
					i = i + 3
				elif respTxt[i:i+6] == '</div>' and div > 0:
					div = div - 1
					i = i + 5

				if zeroCheck(span, table, italic, parentheses, div) and \
					respTxt[i:i+15] == '<a href="/wiki/':
					# This is the link we want to follow, provided it
					#  is the correct format

					i = i + 15
					j = 0

					while True:
						if respTxt[i+j] == '"':
							urlTitle = respTxt[i:i+j]
							if checkForIncorrectURLFormat(urlTitle):
								urlTitle = ''
								break
							else:
								return urlTitle
						j = j + 1

				i = i + 1
				if i > len(respTxt):
					return ''

		i = i + 1
		if i > len(respTxt):
			return ''


def zeroCheck(s, t, i, p, d):
	'''Helper function to check if all the HTML tag counts
	are zero '''
	return (s == 0 and t == 0 and i == 0 and p == 0 and d == 0)


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

	urlTitle = getURLTitle(respTxt[idx:])
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

	elif urlTitle in visitedArticles and urlTitle != '':
		# We've visited this page before and it converges
		if vo:
			print '>>>CONVERGENT<<<'
			print 'Path Length:', len(currentPath) + visitedArticles[urlTitle] + 1
		randomArticles[randomTitle] = len(currentPath) + visitedArticles[urlTitle] + 1
		addVisitedPath(visitedArticles[urlTitle])
		currentPath = []
		return False

	elif len(currentPath) < mpl and urlTitle not in currentPath and urlTitle != '':
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


def calculateStats():
	'''calculateStats generates the count of articles that do not 
	reach the Philosophy page and the count of articles that do,
	as well as a dictionary that contains the data to generate a 
	histogram'''

	global randomArticles

	divergesCount = 0
	convergesCount = 0
	histogram = {}

	for page in randomArticles:
		if randomArticles[page] == -1:
			divergesCount = divergesCount + 1
		else:
			convergesCount = convergesCount + 1
			if randomArticles[page] in histogram:
				histogram[randomArticles[page]] = histogram[randomArticles[page]] + 1
			else:
				histogram[randomArticles[page]] = 1

	return divergesCount, convergesCount, histogram


def checkForIncorrectURLFormat(url):
	'''checkForIncorrectURLFormat checks the urlTitle of the
	potential next article to follow. Certain wiki URLs are
	not followed.'''

	if url[:5].lower() == 'file:' or \
		url[-16:].lower() == '(disambiguation)' or \
		url[:10].lower() == 'wikipedia:' or \
		url[:9].lower() == 'category:' or \
		url[:5].lower() == 'help:' or \
		url[:8].lower() == 'special:':
		return True
	else:
		return False


def parseCommandLineArgs(args):
	'''The parseCommandLineArgs function reads the command line
	arguments and catches command line errors. It takes one argument
	consisting of the list of command line arguments and returns 
	integer values for number of iterations and maximum path
	length'''

	global vo

	if len(args) > 4:
		# Too many arguments
		print errorMessage(1)
		sys.exit()
	elif len(args) == 4:
		# User has input max path length, number of iterations and
		#  option for visual output
		if args[1].isdigit() and args[2].isdigit() and \
			args[3] == '-vo':
			vo = True
			return int(args[1]), int(args[2])
		elif not args[1].isdigit() or not args[2].isdigit():
			print errorMessage(2)
			sys.exit()
		elif args[3] != '-vo':
			print errorMessage(3)
			sys.exit()
		else:
			print errorMessage(0)
			sys.exit()
	elif len(args) == 3:
		# User has input either:
		#  max path length and iterations OR
		#  max path length and -vo
		if args[1].isdigit() and args[2].isdigit():
			return int(args[1]), int(args[2])
		elif args[1].isdigit() and args[2] == '-vo':
			vo = True
			return args[1], 500
		elif not args[1].isdigit():
			print errorMessage(2)
			sys.exit()
		elif args[2] != '-vo':
			print errorMessage(3)
			sys.exit()
		else: 
			print errorMessage(0)
			sys.exit()
	elif len(args) == 2:
		# User has input only max path length or only -vo
		if args[1].isdigit():
			return int(args[1]), 500
		elif args[1] == '-vo':
			vo = True
			return 50, 500
		else:
			print errorMessage(0)
			sys.exit()
	else:
		return 50, 500


def errorMessage(number):
	'''errorMessage is a helper function for printing error messages 
	arising from command line input errors. It takes one integer argument,
	number, that denotes which specific error message to return.'''

	msg = '-Input Format: $ python main.py [max path length] [iterations] [-vo]\n'
	msg = msg + '-Default max path length is 50\n'
	msg = msg + '-Default iterations is 500'

	if number == 0:
		return 'ERROR:\n' + msg
	elif number == 1:
		msg = '\nERROR: Too many command line arguments.\n' + msg
		return msg
	elif number == 2:
		msg = '\nERROR: max path length and iterations arguments must be integers.\n' + msg
		return msg
	elif number == 3:
		msg = '\nERROR: visual output option is -vo.\n' + msg
		return msg


def printStats(dc, cc, histo, i, mpl):
	'''printStats is a helper function that prints the statistics
	of the wiki crawl, i.e. number of pages that diverged and 
	percentages. It also generates the histogram using numpy and
	pylab.'''

	global startTime

	percentage = round((float(cc) / float(i)),2) * 100.0
	print ''
	print 'Diverged count:\t\t\t', dc
	print 'Converged count:\t\t', cc
	print 'Convergence percentage:\t\t', percentage, '%' 
	print 'Random pages generated:\t\t', i
	print 'Maximum path length:\t\t', mpl
	runtime = time.time() - startTime
	print 'Runtime:\t\t\t', round(runtime,3), 'seconds\n'

	for j in range(min(histo)-2,max(histo)+2):
		if j not in histo:
			histo[j] = 0

	# The code in the below section is taken from 
	# http://stackoverflow.com/questions/16892072/histogram-in-pylab-from-a-dictionary
	x = np.arange(len(histo))
	pl.bar(x, histo.values(), align='center', width=0.5)
	pl.xticks(x, histo.keys())
	ymax = max(histo.values()) + 1
	pl.ylim(0, ymax)
	pl.show()
	# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	# http://stackoverflow.com/questions/16892072/histogram-in-pylab-from-a-dictionary


if __name__ == '__main__':

	# Input syntax:
	#  $ python main.py [maxPathLength] [iterations] [-vo]
	maxPathLength, iterations = parseCommandLineArgs(sys.argv)

	# URL for random wiki page
	randomWikiURL = 'https://en.wikipedia.org/wiki/Special:Random'

	for i in range(iterations):

		# Request random URL HTML
		response = reqs.get(randomWikiURL)

		# Get title of random article
		randomTitle, currentIdx = getArticleTitle(response.text)

		if vo:
			print 'Random Article:', randomTitle

		# Search response text for next URL
		diverges = searchForHyperlink(response.text, currentIdx, maxPathLength, randomTitle)
		if diverges:
			randomArticles[randomTitle] = -1

	dc, cc, histo = calculateStats()

	printStats(dc, cc, histo, iterations, maxPathLength)


	
