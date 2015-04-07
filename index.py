import collections
import getopt
import math
import os
import sys

import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

import xml.etree.ElementTree as ET


__author__ = 'Jing Rong, Jia Le, Nelson'


# Python script for indexing

term_to_docfreq = {}    # Dictionary to map [term.field : document frequency]
term_to_docposting = collections.defaultdict(list) # Dictionary to map [term.field : list[document posting]]
termdocname_to_termfreq = {}  # Dictionary to map [(term.field, doc name) : term frequency]
stemmer = PorterStemmer()
terms = []
terms_to_startptr = {}
docid_to_terms = collections.defaultdict(list)  # Dictionary to map [document name : list of terms in document]
docid_to_cosnorm = {}

# To conduct XML parsing for PatSnap corpus
def corpus_xml_parsing(corpus_doc, corpus_directory): # corpus_doc is the document file (XML file)

    filename = os.path.join(corpus_directory, corpus_doc) # filename is the name of the file in the directory

    tree = ET.parse(filename)
    root = tree.getroot()

    # For each subheading in the XML file
    for child in root:

        # If the subheading is the title or the abstract
        if child.attrib['name'] == 'Title' or child.attrib['name'] == 'Abstract':
            child_tokens = set(nltk.word_tokenize(child.text))   # Tokenize the title / abstract # Put in a set to count for doc freq
            child_tokens_no_stopwords = [w for w in child_tokens if not w in stopwords.words('english')]    # Remove stopwords
            
            for token in child_tokens_no_stopwords:
                if is_ascii(token):
                    token = stemmer.stem(token)   # Stem the word
                    term = token + "." + child.attrib['name'].lower()    # No case-folding for the word
                
                    # If this token is not found in the docid_to_terms[doc_id]
                    if term not in docid_to_terms[corpus_doc]:
                        docid_to_terms[corpus_doc].append(term)
                    
                    # If term exists within the term dictionary
                    if term in term_to_docfreq:
                        term_to_docfreq[term] += 1  # Add one to the frequency
                    # Else instantiate one copy of it
                    else:
                        term_to_docfreq.setdefault(term, 1)
                        terms.append(term)
                        
                    # If the document does not exist in the postings dictionary
                    if corpus_doc not in term_to_docposting[term]:
                        term_to_docposting[term].append(corpus_doc) # Add this document to the postings list
    
                    termdocname = (term, corpus_doc)   # Store the document name as a tuple (token.field, document name)
                    if termdocname not in termdocname_to_termfreq:  # If it does not exist in the data structure
                        termdocname_to_termfreq.setdefault(termdocname, 1)  # Add to data structure
                    else:
                        termdocname_to_termfreq[termdocname] += 1   # Else add one to the frequency

    # Need to write to dictionary.txt
    
    
# Indexing the corpus into dictionary.txt
def corpus_indexing(corpus_path, dictionary_output, postings_output):
    
    global terms
    corpus_list = os.listdir(corpus_path)  # Getting the directory of the corpus

    for each_file in corpus_list:
        print "Currently indexing: " + str(each_file)
        corpus_xml_parsing(each_file, corpus_path)    # Parse each XML document
        
    # logarithmic term freq
    for key, value in termdocname_to_termfreq.iteritems():
        termdocname_to_termfreq[key] = 1 + math.log10(value)
        
    # normalise the tf
    for doc in docid_to_terms:
        termslist = docid_to_terms[doc]
        sum = 0
        for term in termslist:
            termDocId = (term, doc)
            tf_weight = 1 + math.log10(termdocname_to_termfreq[termDocId])
            sum += pow(tf_weight, 2)
        docid_to_cosnorm[doc] = 1 / math.sqrt(sum)   # Denominator of cosine
        
    # sort the terms
    terms = sorted(terms)
    
    # To write the postings.txt
    with open(postings_output, "w+") as p:
        for term in terms:
            # to keep track of the start pointer
            startptr = p.tell()
            terms_to_startptr[term] = startptr
 
            list_of_docid = term_to_docposting[term]  # list_of_docid is the list of names of the XML file in the corpus
            
            for posting in list_of_docid:
                termDocId = (term, posting)
                text = str(posting) + " " + str(termdocname_to_termfreq[termDocId] * docid_to_cosnorm[posting]) + " "
                p.write(text)   # Writes in the form <Document
            p.write('\n')
    
    # To write the dictionary.txt
    with open(dictionary_output, "w+") as d:
        for term in terms:
            # For each term in all the terms
            text = str(term) + " " + str(term_to_docfreq[term]) + " " + str(terms_to_startptr[term]) + '\n'
            d.write(text)

def is_ascii(s):
    return all(ord(c) < 128 for c in s)
    
def usage():
    print "usage: " + sys.argv[0] + " -i path-of-file-for-indexing -d output-dictionary -p output-posting"

indexingPath = output_file_p = output_file_d = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-i':
        indexingPath = a
    elif o == '-d':
        output_file_d = a
    elif o == '-p':
        output_file_p = a
    else:
        assert False, "unhandled option"
if indexingPath == None or output_file_p == None or output_file_d == None:
    usage()
    sys.exit(2)

dictionaryFileName = output_file_d
postingFileName = output_file_p
corpus_indexing(indexingPath, output_file_d, output_file_p)