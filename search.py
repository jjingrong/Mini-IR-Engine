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
    dictionary = corpora.Dictionary.load(input_file_d)  # Load the dictionary
    corpus = corpora.MmCorpus(input_file_p) # Load the corpus
    
    tfidf = models.TfidfModel(corpus, normalize=True)   # Convert vector to TF-IDF weighted scheme
    corpus_tfidf = tfidf[corpus]    # Applying TF-IDF to the corpus
    
    ''' # Getting results via Latent Dirichlet Allocation (LDA)
    lda = models.LdaModel(corpus=corpus, id2word=dictionary, num_topics=200)   # Setting up Latent Dirichlet Allocation (LDA) model
    corpus_lda = lda[corpus]  # Applying the LDA model on the corpus (corpus is TF-IDF weighted)
    
    query_for_lda = no_stopwords_text
    doc_bow = dictionary.doc2bow(query_for_lda)
    doc_lda = lda[doc_bow]  # Coverts query to LDA space
    
    lda_index = similarities.MatrixSimilarity(corpus_lda)  # Index the corpus into an LDA space
    
    sims_lda = lda_index[doc_lda]   # Performs similarity query against the indexed LDA space
    sims_lda = sorted(enumerate(sims_lda), key=lambda item: -item[1])
    sims_lda = [item[0] for item in sims_lda if item[1] > 0.01]    # Threshold of 0.01 based on heuristics '''
    
    # Getting results via Latent Semantic Indexing (LSI)
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=300)   # Setting up Latent Semantic Indexing (LSI) model
    corpus_lsi = lsi[corpus_tfidf]  # Applying the LSI model on the corpus (corpus is TF-IDF weighted) and transform it to a LSI space
    
    query_for_lsi = no_stopwords_text
    doc_bow = dictionary.doc2bow(query_for_lsi)
    doc_lsi = lsi[doc_bow]  # Converts query to LSI space
    
    lsi_index = similarities.MatrixSimilarity(corpus_lsi)   # Index the corpus into an LSI space
    
    sims_lsi = lsi_index[doc_lsi]   # Performs similarity query against the indexed LSI space
    sims_lsi = sorted(enumerate(sims_lsi), key=lambda item: -item[1])
    sims_lsi = [item for item in sims_lsi if item[1] > 0.01]    # Threshold of 0.01 based on heuristics
    
    # sims_lda = set(sims_lda)    # Convert similarity query for LDA space into a set
    # sims_lsi = set(sims_lsi)    # Convert similarity query for LSI space into a set 
    
    return sims_lsi
        
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