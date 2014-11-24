import itertools
import math
import sys
import logging
from collections import defaultdict
from scipy.optimize import minimize_scalar
import argparse


def pairwise(iterable):
    "iterate over pairs in the sequence: pairwise((s0, s2, ..., sn)) -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


def minusloglikelihood(c, T, unigrams, bigrams):
    """returns the negative of the log likelihood of the data"""
    ll = 0.0
    # for each document
    for D in T:
        # for each sentence pair
        for Sa, Sb in pairwise(D):
            # for each pattern in the second sentence of the pair
            for v in Sb:
                # sum up the contributions of the pattern v conditioned on each pattern u in the first sentence of the pair
                prob_v_given_u = sum((float(bigrams.get((u, v), 0)))/(float(unigrams.get(u, 0)) + c * len(unigrams)) for u in Sa)
                # compute the contribution of pattern v in Sb to the training likelihood
                ll += math.log(1.0/len(Sa)) + math.log(prob_v_given_u)
    return -ll/len(T)


def read_data(istream):

    doc = []
    #file format:
    #WHNP*wp SQ*vbz 
    #PP*in NP-TMP*nnp NP*np VP*md 
    
    for line in istream:
        patterns = line.split()
        sentence = []
        for pattern in patterns:
            sentence.append(pattern)
        doc.append(sentence)
            
    #print 'returning '+str(len(doc))+' lines'
    return doc


def minimize(T, unigrams, bigrams):
    """optimise the likelihood of T"""
    return minimize_scalar(minusloglikelihood, bounds=(0.0, 1.0), args=(T, unigrams, bigrams), method='bounded')


def count(T):
    """count unigram and bigram patterns in training data T"""
    # counts
    unigrams = defaultdict(int)
    bigrams = defaultdict(int)

    # counting
    for D in T:
        for Sa in D:
            for u in Sa:
                unigrams[u] += 1
        for Sa, Sb in pairwise(D):
            for u, v in itertools.product(Sa, Sb):
                bigrams[(u, v)] += 1

    return unigrams, bigrams
                

def main(args):
    """load data and optimise the likelihood"""
    T = []
    for index in range(args.n):
        path = args.prefix + str(index)
        logging.info('Processing %s', path)
        with open(path, 'r') as fi:
            T.append(read_data(fi))
    unigrams, bigrams = count(T)
    print minimize(T, unigrams, bigrams)


def parse_args():
    """parse command line arguments"""

    parser = argparse.ArgumentParser(description='Hyperparameter tuning via MLE',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('prefix',
            type=str,
            help='prefix of documents (to be completed with numbers)')
    parser.add_argument('n',
            type=int,
            help='number of documents')
    parser.add_argument('--verbos', '-v',
            action='store_true',
            help='increase the verbosity level')

    args = parser.parse_args()

    logging.basicConfig(
            level=(logging.DEBUG if args.verbose else logging.INFO), 
            format='%(levelname)s %(message)s')

    return args

if __name__ == '__main__':

    main(parse_args())

