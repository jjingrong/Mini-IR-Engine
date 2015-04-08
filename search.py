from StdSuites.Type_Names_Suite import null
from pip._vendor.pkg_resources import null_ns_handler
__author__ = 'Jing Rong, Jia Le, Nelson'

from nltk.corpus import stopwords
import sys
import getopt
import xml.etree.ElementTree as ET
import linecache
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models, similarities



# Python script for queries
def remove_stopwords(queryxml):
    
    lmtzr = WordNetLemmatizer()
    stemmer = PorterStemmer()
    
    no_stopwords_text = []

    tree = ET.parse(queryxml)
    root = tree.getroot()
    
    # import stopwords
    for child in root:
        if child.tag == 'description':
            abstract_text = child.text
            abstract_text = abstract_text.split()
            for w in abstract_text[4:]: # Remove irrelevant part of the query's abstract (i.e. Relevant documents will describe)
                if not w in stopwords.words('english'):
                    w = lmtzr.lemmatize(w)  # Lemmatize the word
                    w = stemmer.stem(w)  # Stem the word
                    w.lower()
                    no_stopwords_text.append(w)
                    break
    
    # Do something with query
    dictionary = corpora.Dictionary.load(input_file_d)
    corpus = corpora.MmCorpus(input_file_p)
    
    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=350)   # Implements Latent Semantic Indexing
    
    query = no_stopwords_text
    vec_bow = dictionary.doc2bow(query)
    vec_lsi = lsi[vec_bow]  # Coverts query to LSI space
    
    index = similarities.MatrixSimilarity(lsi[corpus])  # Transforms corpus to LSI space
    
    sims = index[vec_lsi]   # Performs similarity query against the corpus
    sims = sorted(enumerate(sims), key=lambda item: -item[1])
    sims = [item for item in sims if item[1] > 0.01]    # Threshold of 0.01 based on heuristics
    
    return sims
        
def performQueries():
    
    sims = remove_stopwords(input_file_q)
    
    with open(output_file, "w+") as o:
        for doc_score_pair in sims:
            doc = linecache.getline('patentid.txt', doc_score_pair[0]).rstrip()
            o.write(doc + '\n')
            print str(doc) + " " + str(doc_score_pair[1])

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

performQueries()