__author__ = 'Jing Rong (A0114395E), Jia Le (A0116673A), Nelson (A0111014J)'

import sys
import getopt
import xml.etree.ElementTree as ET
import linecache
import nltk

from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models, similarities
from collections import defaultdict

docid_to_ipc = {}
ipc_to_doc = defaultdict(list)

# Storing the IPC-to-Document mapping on a data structure on disk
def ipc_to_mem():
    
    print("Storing IPC-to-Document Mapping on disk...")
    
    with open('IPCtoDoc.txt') as w:
        content = w.readlines() # 'content' is all the content in the file 'IPCtoDoc.txt'
    
    for each_line in content:
        tokens = nltk.word_tokenize(each_line)
        ipc = tokens[0] # First token is the IPC subclass
        ipc_to_doc[ipc] = tokens[1:]    # Storing the list of documents belonging to that subclass
        for each_doc in tokens[1:]: # For each document in the list of documents belonging to that subclass
            docid_to_ipc[each_doc] = ipc    # Store a mapping of Document Name-to-IPC subclass
            
    print("Storing Complete!")
    
# To remove the stopwords from the query xml file
def remove_stopwords(queryxml):
    
    lmtzr = WordNetLemmatizer()
    stemmer = PorterStemmer()
    
    no_stopwords_text = []

    tree = ET.parse(queryxml)   # Parsing the xml file as a tree structure
    root = tree.getroot()
    
    for child in root:
        if child.tag == 'description':  # If the tag is the description
            abstract_text = child.text
            abstract_text = abstract_text.split()   # Split the string inside 'description' by whitespace
            for w in abstract_text[4:]: # Remove irrelevant part of the query's abstract (i.e. "Relevant documents will describe...")
                if not w in stopwords.words('english'): # If the word is not a stopword
                    w = lmtzr.lemmatize(w)  # Lemmatize the word
                    w = stemmer.stem(w)  # Stem the word
                    w = w.lower()   # Case-fold the resulting word to lowercase
                    no_stopwords_text.append(w) # Add the resulting words to the list of text to query
        
        elif child.tag == 'title':  # Else if the tag is the title
            abstract_text = child.text
            abstract_text = abstract_text.split()   # Split the string inside 'description' by whitespace
            for w in abstract_text:
                if not w in stopwords.words('english'): # If the word is not a stopword
                    w = lmtzr.lemmatize(w)  # Lemmatize the word
                    w = stemmer.stem(w)  # Stem the word
                    w = w.lower()   # Case-fold the resulting word to lowercase
                    no_stopwords_text.append(w)
                    
    # Do something with query
    dictionary = corpora.Dictionary.load(input_file_d)  # Load the dictionary
    corpus = corpora.MmCorpus(input_file_p) # Load the corpus
    
    tfidf = models.TfidfModel(corpus, normalize=True)   # Convert vector to TF-IDF weighted scheme
    corpus_tfidf = tfidf[corpus]    # Applying TF-IDF to the corpus
    
    # Attempted to utilize Latent Dirichlet Allocation model, but results were worse-off as compared to Latent Semantic Indexing (LSI)
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
    doc_bow = dictionary.doc2bow(query_for_lsi) # Transforms the query (without stopwords, with lemmatization and stemming) into a bag-of-words
    doc_lsi = lsi[doc_bow]  # Converts bag-of-words query into an LSI space
    
    print("Finding top 1% of similar documents based on input query...")
    lsi_index = similarities.MatrixSimilarity(lsi[corpus_tfidf])   # Index the corpus (TF-IDF weighted) into an LSI space
    
    sims_lsi = lsi_index[doc_lsi]   # Performs similarity query against the indexed LSI space
    sims_lsi = sorted(enumerate(sims_lsi), key=lambda item: -item[1])
    sims_lsi = sims_lsi[:25]    # Get the first 25 top scoring documents based on LSI scoring
    
    return sims_lsi
    
def performQueries():
    
    sims = remove_stopwords(input_file_q)   # Retrieve first 25 most relevant documents (About top 1% of relevant documents against corpus)
    retrieve_final(sims)   # Retrieve the total final list, with the top 25 documents AND the subclass retrieved

def retrieve_final(top_sims):
    ipc_list = []
    
    for eachDocument in top_sims:   # For each document in the top 25 documents
        docname = linecache.getline('patentid.txt', eachDocument[0]).rstrip()   # Get the actual patent document name
        if docname in docid_to_ipc: # If the document has an IPC subclass
            ipc_list.append(docid_to_ipc[docname])    # Add the IPC subclass to the list of IPCs
    
    # Retrieve the most common IPC subclass amongst the IPC list
    top_ipc = max(set(ipc_list), key=ipc_list.count)
    print("Most relevant IPC subclass: " + str(top_ipc))
    print("Finding list of documents from most common IPC subclass...")
    docs_in_relevant_ipc = ipc_to_doc[top_ipc]  # Retrieve the list of relevant documents from the most common IPC subclass
    original_query_docs = [linecache.getline('patentid.txt', i[0]).rstrip() for i in top_sims]  # Retrieve the names of the original 25 documents retrieved
    
    relevant_ipc_doc_set = set(docs_in_relevant_ipc)    # Ensure no repeated documents for the list of documents in most common IPC subclass
    original_query_doc_set = set(original_query_docs)   # Ensure no repeated documents for the original list of 25 documents
    
    print("Getting finalized list...")
    setfinal = relevant_ipc_doc_set | original_query_doc_set    # Get the merged union set of both lists
    
    # To write output of final list
    all_results = ""
    with open(output_file, "w+") as o:
        for each_doc in setfinal:
            all_results += (each_doc + ' ')
        
        all_results = all_results.rstrip()  # To remove trailing whitespace
        o.write(str(all_results))   # To actually write to file
            
    print("Finalized List Complete! Output written to output.txt!")
    
def usage():
    print "usage: " + sys.argv[0] + "-d output-dictionary -p output-posting -q input-queries -o output-results"

################################################################################################################
# MAIN #

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

# Main functions to run
ipc_to_mem()
performQueries()