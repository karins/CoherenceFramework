"""
This module can be used to score a document using A. Louis's model

@author: wilkeraziz
"""

import sys
import argparse
import logging
import numpy as np
import traceback
from itertools import izip
from collections import defaultdict
from multiprocessing import Pool
from functools import partial
from discourse.util import register_token, read_documents, encode_documents, encode_test_documents, ibm_pairwise, pairwise, smart_open
from discourse import command


def load_model(u_path, b_path, null='<null>', unk='<unk>'):
    """
    Loads a model stored in a file.

    Arguments
    ---------
    path: path to file containing the T table (as produced by ibm.py)
    null_symbol: symbol that should get id 0
    
    Returns
    -------
    T: numpy array such that T[f,e] = t(f|e)
    vocab: defaultdict mapping a pattern (str) into an id (int)
    """
    vocab = defaultdict()
    register_token(null, vocab)  # makes sure <null> gets id 0
    register_token(unk, vocab)  # makes sure <null> gets id 0
    u_entries = []
    b_entries = []
    
    # read unigrams in
    with open(u_path) as fi:
        header = next(fi)
        for line in fi:
            line = line.strip()
            if not line:
                continue
            w, count = line.split('\t') 
            u_entries.append((register_token(w, vocab), float(count)))
    
    # read bigrams in
    with open(b_path) as fi:
        header = next(fi)
        for line in fi:
            line = line.strip()
            if not line:
                continue
            w1, w2, count = line.split('\t') 
            b_entries.append((register_token(w1, vocab), register_token(w2, vocab), float(count)))
    
    V = len(vocab)
    U = np.zeros(V, int)
    B = np.zeros((V, V), int)
    for w, c in u_entries:
        U[w] = c
    for w1, w2, c in b_entries:
        B[w1,w2] = c
    return U, B, vocab


def loglikelihood(corpus, U, B, c, insertion=False):
    """
    Computes -log(likelihood(T))

    This version is slightly different from the one in ibm1.py
    because it has to deal with unknown patterns.
    """
    L = np.zeros(len(corpus))
     
    getpairs = ibm_pairwise if insertion else pairwise

    for i, D in enumerate(corpus):
        # for each sentence pair
        for Sa, Sb in getpairs(D):  # if insertion=True, then getpairs=ibm_pairwise, consequently, Sa[0] is the null word
            # for each pattern in the second sentence of the pair
            for v in Sb:
                # sum up the contributions of the pattern v conditioned on each pattern u in the first sentence of the pair
                L[i] = np.log(1.0/len(Sa)) + np.log(np.sum([(B[u,v] + c)/(U[u] + c * len(U)) for u in Sa]))
    return L


def wrapped_loglikelihood(corpus, U, B, c, insertion):
    try:
        return loglikelihood(corpus, U, B, c, insertion)
    except:
        raise Exception(''.join(traceback.format_exception(*sys.exc_info())))


def decode(unigrams, bigrams, c, istream, ostream, estream=sys.stderr):

    # reads in the model
    logging.info('Loading model: %s and %s', unigrams, bigrams)
    U, B, vocab = load_model(unigrams, bigrams)
    logging.info('%d unigrams and %d bigrams', U.shape[0], B.shape[0])

    # detect whether document boundary tokens were used in the model
    boundaries = '<doc>' in vocab
    # detect whether insertion was swtiched
    insertion = B[0,:].sum() > 0
    # reads in the test documents
    logging.info('Reading test documents in (boundaries=%s) ...', boundaries)
    documents = read_documents(istream, boundaries)  
    logging.info('%d test documents read', len(documents))
   
    # encode test documents using the model's vocabulary
    test = encode_test_documents(documents, vocab)

    # computes the log likelihood of each document
    L = loglikelihood(test, U, B, c, insertion)

    # dumps scores
    print >> ostream, '#doc\t#logprob\t#sentences\t#s_normalised\t#patterns\t#p_normalised'
    for i, ll in enumerate(L):
        num_sentences = len(test[i])
        num_patterns = sum(len(row) for row in test[i])
        print >> ostream, '{0}\t{1}\t{2}\t{3}\t{4}\t{5}'.format(i, ll, num_sentences, 
                ll/num_sentences, num_patterns, ll/num_patterns)
    print >> estream, '#sum\t#mean'
    print >> estream, '{0}\t{1}'.format(L.sum(), np.mean(L))
  

def decode_many(unigrams, bigrams, c, ipaths, opaths, jobs, estream=sys.stderr):

    # reads in the model
    logging.info('Loading model: %s and %s', unigrams, bigrams)
    U, B, vocab = load_model(unigrams, bigrams)
    logging.info('%d unigrams and %d bigrams', U.shape[0], B.shape[0])

    # detect whether document boundary tokens were used in the model
    boundaries = '<doc>' in vocab
    # detect whether insertion was swtiched
    insertion = B[0,:].sum() > 0

    # reads in the test documents
    logging.info('Reading test documents in (boundaries=%s) ...', boundaries)

    tests = [None] * len(ipaths)
    for i, ipath in enumerate(ipaths):
        documents = read_documents(smart_open(ipath), boundaries)  
        logging.info('%s: %d test documents read', ipath, len(documents))
        # encode test documents using the model's vocabulary
        tests[i] = encode_test_documents(documents, vocab)

    # computes the log likelihood of each document in each test file
    pool = Pool(jobs)
    all_L = pool.map(partial(wrapped_loglikelihood, U=U, B=B, c=c, insertion=insertion), tests)

    print >> estream, '#file\t#sum\t#mean'
    for ipath, opath, test, L in izip(ipaths, opaths, tests, all_L):
        with smart_open(opath, 'w') as ostream:
            # dumps scores
            print >> ostream, '#doc\t#logprob\t#sentences\t#s_normalised\t#patterns\t#p_normalised'
            for i, ll in enumerate(L):
                num_sentences = len(test[i])
                num_patterns = sum(len(row) for row in test[i])
                print >> ostream, '{0}\t{1}\t{2}\t{3}\t{4}\t{5}'.format(i, ll, num_sentences, 
                        ll/num_sentences, num_patterns, ll/num_patterns)
            print >> estream, '{0}\t{1}\t{2}'.format(opath, L.sum(), np.mean(L))


def main(args):
    logging.basicConfig(
            level=(logging.DEBUG if args.verbose else logging.INFO), 
            format='%(levelname)s %(message)s')
    decode(args.unigrams, args.bigrams, args.smoothing, args.input, args.output)
    

@command('alouis_decoder', 'syntax-based')
def argparser(parser=None, func=main):
    """parse command line arguments"""

    if parser is None:
        parser = argparse.ArgumentParser(prog='alouis_decoder')
    parser.description = "A. Louis decoder for syntax-based coherence"
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    
    parser.add_argument('unigrams',
            type=str,
            help='unigram counts')
    parser.add_argument('bigrams',
            type=str,
            help='bigram counts')
    parser.add_argument('input', nargs='?', 
            type=argparse.FileType('r'), default=sys.stdin,
            help='test corpus in doctext format')
    parser.add_argument('output', nargs='?', 
            type=argparse.FileType('w'), default=sys.stdout,
            help='document log probabilities')
    parser.add_argument('--smoothing', '-c',
            type=float, default=0.001,
            help='smoothing constant')
    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')

    if func is not None:
        parser.set_defaults(func=func)

    return parser


if __name__ == '__main__':
    main(argparser().parse_args())

