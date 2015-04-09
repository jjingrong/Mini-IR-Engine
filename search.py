__author__ = 'Jing Rong, Jia Le, Nelson'

from nltk.corpus import stopwords
import sys
import getopt
import xml.etree.ElementTree as ET
import linecache
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models, similarities
from collections import defaultdict

docid_to_ipc = {}
ipc_to_doc = defaultdict(list)

# Recording a document's IPC

def record_IPC():
    
    print("Recording IPC to local memory")
    
    with open('IPCtoDoc.txt') as w:
        content = w.readlines() # Content is all the content in the file 'IPCtoDoc.txt'
    
    for each_line in content:
        tokens = nltk.word_tokenize(each_line)
        print(tokens[0])
        ipc = tokens[0] # First token is the IPC subclass
        ipc_to_doc[ipc] = tokens[1:]
        for each_doc in tokens[1:]:
            docid_to_ipc[each_doc] = ipc
            
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
        
        elif child.tag == 'title':
            abstract_text = child.text
            abstract_text = abstract_text.split()
            for w in abstract_text:
                if not w in stopwords.words('english'):
                    w = lmtzr.lemmatize(w)  # Lemmatize the word
                    w = stemmer.stem(w)  # Stem the word
                    w.lower()
                    no_stopwords_text.append(w)
                    
    # Do something with query
    dictionary = corpora.Dictionary.load(input_file_d)  # Load the dictionary
    corpus = corpora.MmCorpus(input_file_p) # Load the corpus
    
    tfidf = models.TfidfModel(corpus, normalize=True)   # Convert vector to TF-IDF weighted scheme
    corpus_tfidf = tfidf[corpus]    # Applying TF-IDF to the corpus
    
    """# Getting results via Latent Dirichlet Allocation (LDA)
    lda = models.LdaModel(corpus=corpus_tfidf, id2word=dictionary, num_topics=100)   # Setting up Latent Dirichlet Allocation (LDA) model
    
    query_for_lda = no_stopwords_text
    doc_bow = dictionary.doc2bow(query_for_lda)
    doc_lda = lda[doc_bow]  # Coverts query to LDA space
    
    lda_index = similarities.MatrixSimilarity(lda[corpus])  # Index the corpus into an LDA space
    
    sims_lda = lda_index[doc_lda]   # Performs similarity query against the indexed LDA space
    sims_lda = sorted(enumerate(sims_lda), key=lambda item: -item[1])
    sims_lda = [item for item in sims_lda if item[1] > 0.1]    # Threshold of 0.01 based on heuristics 
    
    sims_lda = set(sims_lda)    # Convert similarity query for LDA space into a set """
    
    # Getting results via Latent Semantic Indexing (LSI)
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=350)   # Setting up Latent Semantic Indexing (LSI) model
    
    query_for_lsi = no_stopwords_text
    doc_bow = dictionary.doc2bow(query_for_lsi)
    doc_lsi = lsi[doc_bow]  # Converts query to LSI space
    
    lsi_index = similarities.MatrixSimilarity(lsi[corpus_tfidf])   # Index the corpus into an LSI space
    
    sims_lsi = lsi_index[doc_lsi]   # Performs similarity query against the indexed LSI space
    sims_lsi = sorted(enumerate(sims_lsi), key=lambda item: -item[1])
    sims_lsi = sims_lsi[:25]    # Get the first 25 top scoring documents based on LSI scoring
    
    return sims_lsi
    
def performQueries():
    
    sims = remove_stopwords(input_file_q)   # Retrieve first 25 most relevant documents
    final_sims = retrieve_final(sims)

def retrieve_final(top_sims):
    ipcArr = []
    #most_relevant_ipc = max(set(top_sims), key=top_sims.count)
    for eachDocument in top_sims:
        docname = linecache.getline('patentid.txt', eachDocument[0]).rstrip()
        if docname in docid_to_ipc:
            ipcArr.append(docid_to_ipc[docname])
    # get most common ipc amongst top 25 results
    topIPC = max(set(ipcArr), key=ipcArr.count)
    print("top ipc: " + str(topIPC))
    allRelevantDocumentsInIPC = ipc_to_doc[topIPC]
    top25Docs = [linecache.getline('patentid.txt', i[0]).rstrip() for i in top_sims]
    set1 = set(allRelevantDocumentsInIPC)
    set2 = set(top25Docs)
    setfinal = set1 | set2
    
    with open(output_file, "w+") as o:
        for each_doc in setfinal:
            o.write(str(each_doc) + '\n')
    
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
    
record_IPC()
performQueries()