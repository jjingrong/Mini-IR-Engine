This is the README file for A0116673A-A0111014J-A0114395E's submission

== General Notes about this assignment ==

Place your comments or requests here for Min to read.  Discuss your
architecture or experiments in general.  A paragraph or two is usually
sufficient.

---- System Architecture ----

******** TO BE REMOVED AFTER DONE: add in the stackoverflow references in the reference list below ********

In this assignment, we are using an external library called gensim that helps us in doing topic modelling. 


Main points:
1 uses python library xml.etree.ElementTree to parse XML. will have tree-like data structure, traverse it from root
2 indexed the <abstract> and <title> of the patent files
3 lemmatisation / Stemming / Stopwords
4 gensim, topic modelling library
5 For query.xml, read in both <title> and <description>. do similarity comparison using gensim
6 For query, uses TFIDF + LSI. using topic modelling. topic of 350 (forgot what is the official name). Talk about the trial and error with the number of topic
7 the intuition behind our method is top 25 is always inside our result. get the most prominent IPC subclass from the top25. the rest of the patents with this IPC subclass is included


---- Field/Zone Treatment ----
For this particular homework, we indexed the words inside the <abstract> and <title> of the patents file. 

Main Points:
1 Indexed IPC subclass in seperate file "xxx.txt (to be changed to the exact file name)"
2 use it to retrieve patents that is below top 25 
3 tried to append words to its field eg word.title, word.abstract, but changed it in the end
 
---- Runtime optimisation ----
Remove if nothing to say


---- Things that we tried but removed in the final build ----
Main Points:
1 tried LDA but didnt work, briefly explain
2 query expansion (indexed all the words in title and abstract from the top10 results), didnt work very well because probably due to the 
  extra noise produced by additional words in the patents. Will work if is able to determine the key words instead of indexing all the words in the patent files
3 All the codes are commented out and available in our souce code

---- Allocation of Work ----
1 jl = slacker

---- Misc -----
Maybe can talk about the chinese character indexing, isacsii() to prevent indexing these words (optional, remove if you think not to include)



== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

index.py: the indexing part
search.py: the query part
ESSAY.txt: the essay questions
README.txt: this file
dictionary.txt: dictionary-file
posting.txt: posting-file

== Statement of individual work ==

Please initial one of the following statements.

[ X ] I, A0116673A-A0111014J-A0114395E, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

I suggest that I should be graded as follows:

<Please fill in>

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>

1 Using 3rd party libraries such as NumPy, SciPy, NLTK and gensim
2 gensim's tutorial, https://radimrehurek.com/gensim/tutorial.html
3 

