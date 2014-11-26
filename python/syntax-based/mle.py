import itertools
import math
import sys
import logging
from collections import defaultdict
from scipy.optimize import minimize_scalar
import argparse
import numpy as np

try:
    from progressbar import ProgressBar
    PROGRESSBAR = True
except:
    PROGRESSBAR = False

try:
    from doctext import iterdoctext
except:
    print "You need to add 'preprocessing' to your PYTHONPATH"
    sys.exit(0)


def bar(iterable):
    # if progressbar is installed we use it
    return ProgressBar()(iterable) if PROGRESSBAR else iterable

def pairwise(iterable):
    "iterate over pairs in the sequence: pairwise((s0, s2, ..., sn)) -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


def minusloglikelihood(c, T, unigrams, bigrams):
    """returns the negative of the log likelihood of the data"""
    logging.info('Computing minus log likelihood with c=%f', c)
    ll = 0.0

    # for each document
    for D in bar(T):
        # for each sentence pair
        for Sa, Sb in pairwise(D):
            # for each pattern in the second sentence of the pair
            for v in Sb:
                # sum up the contributions of the pattern v conditioned on each pattern u in the first sentence of the pair
                prob_v_given_u = sum((float(bigrams.get((u, v), 0)))/(float(unigrams.get(u, 0)) + c * len(unigrams)) for u in Sa)
                # compute the contribution of pattern v in Sb to the training likelihood
                ll += math.log(1.0/len(Sa)) + math.log(prob_v_given_u)
    logging.info('average likelihood: %f', -ll/len(T))
    return -ll/len(T)


def minimize(T, unigrams, bigrams):
    """optimise the likelihood of T"""
    return minimize_scalar(minusloglikelihood, bounds=(0.0, 1.0), args=(T, unigrams, bigrams), method='bounded')


def read_data(istream):
    """
    Read documents (one document per file) in plain text format.

    File format 
    -----------
    Each line corresponds to a sentence and it contains the set of syntactic patterns associated with that sentence. Example:

        WHNP*wp SQ*vbz 
        PP*in NP-TMP*nnp NP*np VP*md 

    """

    doc = []
    
    for line in istream:
        patterns = line.split()
        sentence = []
        for pattern in patterns:
            sentence.append(pattern)
        doc.append(sentence)
            
    return doc


def count(T):
    """count unigram and bigram patterns in training data T"""
    # counts
    unigrams = defaultdict(int)
    bigrams = defaultdict(int)

    # counting
    for D in bar(T):
        for Sa in D:
            for u in Sa:
                unigrams[u] += 1
        for Sa, Sb in pairwise(D):
            for u, v in itertools.product(Sa, Sb):
                bigrams[(u, v)] += 1

    return unigrams, bigrams
                

def parse_args():
    """parse command line arguments"""

    parser = argparse.ArgumentParser(description='Hyperparameter tuning via MLE',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')

    args = parser.parse_args()

    logging.basicConfig(
            level=(logging.DEBUG if args.verbose else logging.INFO), 
            format='%(levelname)s %(message)s')

    return args


def main(args):
    """load data and optimise the likelihood"""
    logging.info('Reading documents in ...')
    T = [lines for lines, attrs in iterdoctext(sys.stdin)]
    logging.info('%d documents, on average %.2f sentences per document', len(T), np.mean([len(D)for D in T]))
    logging.info('Counting...')    
    unigrams, bigrams = count(T)
    logging.info('%d unigrams, %d bigrams', len(unigrams), len(bigrams))
    logging.info('Minimising negative log likelihood')
    print minimize(T, unigrams, bigrams)


if __name__ == '__main__':

    main(parse_args())

