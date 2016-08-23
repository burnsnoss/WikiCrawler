main.py is a program that searches random wikipedia pages for the 
 first clickable word in the body of each page. It follows this 
 hyperlink until:
  1. Reaching the Philosophy page (converging)
  2. Reaching the max path length limit (diverging)
  3. Reaching a page with no clickable links (diverging)
  4. Reaching a page that was previously reached in the same path
   (diverging) 

See a full description of this phenomenon here:
 https://en.wikipedia.org/wiki/Wikipedia:Getting_to_Philosophy
NOTE: as of the end of August 23, 2016, the statistics reported on 
 this page have changed. Due to an edit of the wikipedia article
 on 'consciousness', all pages that reach this page will diverge due
 to it looping with the 'awareness' page. My test runs now show a new 
 statistic of about 25% of pages converging to philosophy. 

To run:
	Navigate to the directory where main.py is located.
	In your bash shell, type:
	$ python main.py [max path length] [iterations] [-vo]
	max path length, iterations, and -vo are not required.

	[max path length] is the maximum number of pages that will be 
	 followed before we give up and call it 
	[iterations] is the number of random pages that will be 
	 generated
	[-vo] use this option to see realtime visual output, showing
	 the pages that are being navigated to.

	All three of these are optional, however they must be in the
	 order above. You may omit iterations or both iterations and
	 max path length and still include the [-vo] option for 
	 visual output, for example:

		$ python main.py 60 100 -vo
		$ python main.py 70 -vo
		$ python main.py -vo
		$ python main.py 

		These are all correct formats. 
		The default value for max path length is 50 pages and 
		 the default value for iterations is 500

Stats:
	The program takes about 2-3 minutes to run on average on my 
	 machine for 100 random pages.
	I am getting a rough value of about 35% of random pages
	 converging to the philosophy page and an average path 
	 length of about 12 pages.

In order to reduce the number of HTML requests necessary, I 
 store every page that's been visited that converges in a
 dictionary along with the length of the path from that page
 to the philosophy page. Future edits will probably involve
 a txt file with these path lengths pre-stored for quick
 loading and to save even more time.

Interesting notes:
	Common looping pages:
		Consciousness/Awareness
		Atom/Matter
		Building/Structure
		Genetics/Gene/Locus
		Logic/Argument
		Concept/Generalization

	Reaching any of the above pages results in a loop.

	Pages my algorithm won't work on:
		2009 Supreme Court opinions of Antonin Scalia
		Punjabi Language
	 
	The Antonin Scalia page is laid out unlike any other
	 page on wikipedia, where the entire first body paragraph
	 is in a table, and the Punjabi Language page won't work
	 due to an opening parenthesis without a corresponding 
	 closing parenthesis. I'd imagine there are a few more 
	 that don't work as well.

Outputs from my own runs: (August 23, 2016)


Diverged count:			66
Converged count:		34
Convergence percentage:		34.0 %
Random pages generated:		100
Maximum path length:		50
Average path length:		11
Runtime:			189.41 seconds

--------------------------------------------

Diverged count:			70
Converged count:		30
Convergence percentage:		30.0 %
Random pages generated:		100
Maximum path length:		50
Average path length:		12
Runtime:			166.954 seconds

--------------------------------------------

Diverged count:			61
Converged count:		39
Convergence percentage:		39.0 %
Random pages generated:		100
Maximum path length:		50
Average path length:		12
Runtime:			150.386 seconds

--------------------------------------------

Diverged count:			65
Converged count:		35
Convergence percentage:		35.0 %
Random pages generated:		100
Maximum path length:		50
Average path length:		12
Runtime:			155.036 seconds



