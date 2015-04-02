__author__ = 'Jing Rong, Jia Le, Nelson'

import nltk
from nltk.corpus import stopwords
import sys
import getopt
import math
import heapq
import xml.etree.ElementTree as ET

# Python script for queries

def remove_stopwords(queryxml):
    
    tree = ET.parse(queryxml)
    root = tree.getroot()
    
    # import stopwords

    for child in root:
        if child.tag == 'description':
            abstract_text = child.text
            no_stopwords_text = [w for w in abstract_text.split() if not w in stopwords.words('english')]
            no_stopwords_text = no_stopwords_text[3:]   # Remove irrelevant part of the query's abstract (i.e. Relevant documents will describe)
            break
    
    # Do something with query
    
def performQueries(allQueries, dictionaryFile, postingsFile, outputFile):

    ####################################################################################
    # File processing
    # Get array of lines of dictionary

    # Freq List is done for HW3 extensionability
    dictList = [] # Line number -> term
    freqList = [] # Line number -> document frequency of that term
    pointerList = []

    # DocID -> Doc Length
    docIDLength = {}
    with open(dictionaryFile) as fileObj:
        dictContents = fileObj.readlines()
    for eachLine in dictContents:
        tokens = eachLine.split()
        dictList.append(tokens[0])
        freqList.append(tokens[1])
        pointerList.append(tokens[2])

    # Initialise scoring system
    documentScore = {}

    fp = open(postingsFile)
    fp.seek(int(pointerList[len(pointerList) - 1]), 0)
    allPostingsStr = fp.readline()
    allPostingsTemp = allPostingsStr.split()
    totalNumberOfDocs = len(allPostingsTemp)

    ####################################################################################

    # Open queries file and do them sequentially
    # Content now stores each line
    with open(allQueries) as fileObj:
        queryContent = fileObj.readlines()

    # open output file
    toOutput =  open(outputFile, 'w')

    # For each line of query
    for eachLine in queryContent:
        #print("Time for each query: ")
        #start = timeit.default_timer()
        queryWordArray = {}
        for eachEntry in allPostingsTemp:
            splittedEntry = eachEntry.split(',')
            docIDLength[splittedEntry[0]] = float(splittedEntry[1])
            documentScore[splittedEntry[0]] = 0
        tokens = nltk.word_tokenize(eachLine)
        # Process query heuristics
        # For each query word
        for eachQueryToken in tokens:
            word = eachQueryToken
            # If the word is already in queryWordArray
            if word in queryWordArray:
                # Add one to the count in that element
                queryWordArray[word] = queryWordArray[word] + 1
            else:
                # Start a new count
                queryWordArray[word] = 1
        # Iterate through queryWordArray and replace term frequency with weighted version
        for eachQueryWord in queryWordArray:
            queryWordArray[eachQueryWord] = 1 + math.log10(queryWordArray[eachQueryWord])
        # Look through the dictionary for queryWord
        totalTemp = 0.0

        # Stores word -> weight
        queryWordWeight = {}
        for eachWord in queryWordArray:
            if eachWord in dictList:
                indexOfWord = dictList.index(eachWord)
                wordDF = freqList[indexOfWord]
                wordIDF = math.log10(totalNumberOfDocs/float(wordDF))
                wordWeight = wordIDF * queryWordArray[eachWord]
                queryWordWeight[eachWord] = wordWeight
                totalTemp = totalTemp + math.pow(wordWeight, 2)

        # queryterm -> normalized value
        queryDocLength = math.sqrt(totalTemp)
        queryNormalisedWordValues = {}
        for eachWord in queryWordArray:
            if eachWord in dictList:
                if queryDocLength > 0:
                    queryNormalisedWordValues[eachWord] = queryWordWeight[eachWord] / queryDocLength
                else:
                    queryNormalisedWordValues[eachWord] = 0

        termToDictToNormalisedValue = {}
        for eachQueryTerm in queryWordArray:
            if eachQueryTerm in dictList:
                indexOfWord = dictList.index(eachQueryTerm)
                pointerToPostings = pointerList[indexOfWord]
                fp = open(postingsFile)
                fp.seek(int(pointerToPostings), 0)

                postingsStr = fp.readline()
                postingsTemp = postingsStr.split()

                termToDictToNormalisedValue[eachQueryTerm] = {}
                for eachEntry in postingsTemp:
                    splittedEntry = eachEntry.split(',')
                    if int(splittedEntry[1]) == 0:
                        termToDictToNormalisedValue[eachQueryTerm][splittedEntry[0]] = 0
                    else:
                        termToDictToNormalisedValue[eachQueryTerm][splittedEntry[0]] = (1 + math.log10(int(splittedEntry[1]))) / docIDLength[splittedEntry[0]]

                    # Calculate score
                    documentScore[splittedEntry[0]] = documentScore[splittedEntry[0]] + ( queryNormalisedWordValues[eachQueryTerm] * termToDictToNormalisedValue[eachQueryTerm][splittedEntry[0]])

        # Sort the document via heapq
        heap = [(value, key) for key, value in documentScore.items()]
        sortedHeapDocScore = heapq.nlargest(10, heap)
        sortedHeapDocScore = [(key, value) for value , key in sortedHeapDocScore]

        tempStringToWrite = ""
        for eachDocTuple in sortedHeapDocScore:
            if eachDocTuple[1] > 0 :
                tempStringToWrite += str(eachDocTuple[0])
                tempStringToWrite += " "

        tempStringToWrite = tempStringToWrite[:-1]
        toOutput.write(tempStringToWrite)
        if (queryContent.index(eachLine) != len(queryContent) -1 ):
            toOutput.write('\n')
        #stop = timeit.default_timer()
        # print(stop - start)

# Takes in 'String', returns array of postings(int)
def getPostingsList(term, dictList, pointerList, postingsFile):

    postings = []

    if term in dictList:
        pointerIndex = dictList.index(term)
    else:
        return postings

    fp = open(postingsFile)
    fp.seek(int(pointerList[int(pointerIndex)]), 0)
    postings = nltk.word_tokenize(fp.readline())

    print(term)
    print(postings)
    return postings

def usage():
    print "usage: " + sys.argv[0] + "-d output-dictionary -p output-posting -q input-queries -o output-results"

input_file_q = input_file_p = input_file_d = output_file = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-q':
        input_file_q = a
    elif o == '-d':
        input_file_d = a
    elif o == '-p':
        input_file_p = a
    elif o == '-o':
        output_file = a
    else:
        assert False, "unhandled option"
if input_file_q == None or input_file_d == None or input_file_p == None or output_file == None:
    usage()
    sys.exit(2)

remove_stopwords(input_file_q)
#performQueries(input_file_q, input_file_d, input_file_p, output_file)