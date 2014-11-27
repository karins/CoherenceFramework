import sys
import argparse
import logging
import math
import numpy as np
from collections import defaultdict
from discourse.util import register_token, read_documents, encode_documents, encode_test_documents, ibm_pairwise


def parse_args():
    """parse command line arguments"""

    parser = argparse.ArgumentParser(description='IBM model 1 decoder for syntax-based coherence',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('model',
            type=str,
            help='path to model estimated by ibm1.py')
    parser.add_argument('input', nargs='?', 
            type=argparse.FileType('r'), default=sys.stdin,
            help='test corpus in doctext format')
    parser.add_argument('output', nargs='?', 
            type=argparse.FileType('w'), default=sys.stdout,
            help='document log probabilities')
    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')

    args = parser.parse_args()

    logging.basicConfig(
            level=(logging.DEBUG if args.verbose else logging.INFO), 
            format='%(levelname)s %(message)s')

    return args


def load_model(path, null_symbol='<null>'):
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
    with open(path) as fi:
        header = next(fi)
        vocab = defaultdict()
        register_token(null_symbol, vocab)  # makes sure <null> gets id 0
        entries = []
        for line in fi:
            line = line.strip()
            if not line:
                continue
            e, f, t = line.split('\t') # t = t(f|e) where e=trigger and f=pattern
            entries.append((register_token(f, vocab), register_token(e, vocab), t))
        V = len(vocab)
        T = np.zeros((V, V), float)
        for f, e, t in entries:
            T[f,e] = t
    return T, vocab


def loglikelihood(corpus, T):
    """
    Computes -log(likelihood(T))

    This version is slightly different from the one in ibm1.py
    because it has to deal with unknown patterns.
    """
    L = np.zeros(len(corpus))
    for i, D in enumerate(corpus):
        # for each sentence pair
        for _E, F in ibm_pairwise(D):
            # for each pattern in the second sentence of the pair
            E = np.array([e for e in _E if e >= 0])
            for f in F:
                # sum up the contributions of the pattern v conditioned on each pattern u in the first sentence of the pair
                L[i] += -np.infty if f < 0 else math.log(T[f,E].sum())
    return L

def main(args):

    # reads in the model
    logging.info('Loading model: %s', args.model)
    T, vocab = load_model(args.model, '<null>')
    logging.info('%d patterns and %d entries', len(vocab), T.size)

    # detect whether document boundary tokens were used in the model
    boundaries = '<doc>' in vocab
    # reads in the test documents
    logging.info('Reading test documents in (boundaries=%s) ...', boundaries)
    documents = read_documents(args.input, boundaries)  
    logging.info('%d test documents read', len(documents))
   
    # encode test documents using the model's vocabulary
    test = encode_test_documents(documents, vocab)

    # computes the log likelihood of each document
    L = loglikelihood(test, T)

    # dumps scores
    print >> args.output, '#doc\t#logprob\t#sentences\t#s_normalised\t#patterns\t#p_normalised'
    for i, ll in enumerate(L):
        num_sentences = len(test[i])
        num_patterns = sum(len(row) for row in test[i])
        print >> args.output, '{0}\t{1}\t{2}\t{3}\t{4}\t{5}'.format(i, ll, num_sentences, 
                ll/num_sentences, num_patterns, ll/num_patterns)
    print >> sys.stderr, '#sum\t#mean'
    print >> sys.stderr, '{0}\t{1}'.format(L.sum(), np.mean(L))
  
    # TODO: print viterbi alignments
    


if __name__ == '__main__':
    main(parse_args())
