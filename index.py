import getopt
import os
import sys
import nltk
import xml.etree.ElementTree as ET

from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from gensim import corpora, models, similarities
from collections import defaultdict

__author__ = 'Jing Rong, Jia Le, Nelson'

# Python script for indexing

stemmer = PorterStemmer()
lmtzr = WordNetLemmatizer()
corpus_dict = [[]]
corpus = []
ipc_to_doc = defaultdict(list)

# To conduct XML parsing for PatSnap corpus
def corpus_xml_parsing(corpus_doc, corpus_directory): # corpus_doc is the document file (XML file)

    filename = os.path.join(corpus_directory, corpus_doc) # filename is the name of the file in the directory
    
    doc_dict = []
    tree = ET.parse(filename)
    root = tree.getroot()
    
    # For each subheading in the XML file
    for child in root:

        # If the subheading is the title or the abstract
        if child.attrib['name'] == 'Title' or child.attrib['name'] == 'Abstract':
            child_tokens = set(nltk.word_tokenize(child.text))   # Tokenize the title / abstract # Put in a set to count for doc freq
            child_tokens_no_stopwords = []
            
            for w in child_tokens:
                if not w in stopwords.words('english'): # Check if word is not a stopword
                    try:
                        isInt = int(w)  # Check if word is not a number. If it is, do nothing with it.
                    except ValueError:
                        child_tokens_no_stopwords.append(w) # Append the word into the list of tokens
                        
            for token in child_tokens_no_stopwords:
                if is_ascii(token): # If the token is ascii
                    token = lmtzr.lemmatize(token)  # Lemmatize the word
                    token = stemmer.stem(token)   # Stem the lemmatized word
                    term = token
                    doc_dict.append(term)   # Append the term inside the document's local dictionary # Can have multiple same words
        
        elif child.attrib['name'] == 'IPC Subclass':
            ipc_sc = nltk.word_tokenize(child.text)
            ipc_to_doc[ipc_sc[0]].append(corpus_doc[:-4])
            
    corpus_dict.append(doc_dict) # Add the local document dictionary to the corpus dictionary
            
# Indexing the corpus into dictionary.txt
def corpus_indexing(corpus_path, dictionary_output, postings_output):
    
    global terms
    corpus_list = os.listdir(corpus_path)  # Getting the directory of the corpus
    
    with open('patentid.txt', "w+") as pid:
        for eachFile in corpus_list:
            eachFileArr = nltk.word_tokenize(str(eachFile))
            each_file = eachFileArr[0]
            print "Currently indexing: " + str(each_file[:-4])
            corpus_xml_parsing(each_file, corpus_path)    # Parse each XML document
            pid.write(str(each_file[:-4]) + '\n')    # Write patent doc name on each line to patentid.txt
        
    dictionary = corpora.Dictionary(corpus_dict)
    dictionary.save(dictionary_output)  # Save the dictionary e.g. 'Apple': 0, 'Pear': 1 to dictionary.txt
    
    corpus = [dictionary.doc2bow(doc) for doc in corpus_dict]
    corpora.MmCorpus.serialize(postings_output, corpus) # Store to disk as postings.txt
    
    print "Indexing Complete! (:"
    
    # To write IPC Subclass to Document with said subclass
    with open('IPCtoDoc.txt', "w+") as i:
        for each_ipc in ipc_to_doc:
            i.write(str(each_ipc) + ' ')
            for each_doc in ipc_to_doc[each_ipc]:
                i.write(str(each_doc) + ' ')
            i.write('\n')
    
    print "IPC Mapping Document Complete! (:"

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