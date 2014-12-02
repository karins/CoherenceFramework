"""
Annie Louis's formulation of syntax-based coherence
---------------------------------------------------

A. Louis assumes **complete** data by assuming that every pattern in a sentence triggers patterns in the following sentence (uniformly).
Then the problem of learning a model p(pattern|trigger) becomes trivial.
The MLE solution is simply
    p(pattern|trigger) = count(pattern, trigger) / count(trigger)                         (1)

This comes with some seriour problems. For instance, insertion is not modelled, which means that for pairs never observed at training we will get 0 probability.
To deal with such pairs A. Louis introduced a smoothing constant (absolute discounting):

    p(pattern|trigger) = (count(pattern, trigger) + c) / (count(trigger) + c|V|)          (2)

The problem now is that we have no obvious way to optimise c.

At first (without thinking enough about the problem) I tried to optimise the data's likelihood.
But this is silly as it will simply retrieve the MLE solution (1). That is, scipy will lower c as close to 0 as possible.

Perhaps a way around would be to introduce the possibility of null alignments in her formulation (still assuming complete data).
A much better way around is not to assume the data is complete and use EM (basically, IBM model 1), see `ibm1.py`.

@author: wilkeraziz
"""

import itertools
import math
import sys
import logging
from collections import defaultdict
from scipy.optimize import minimize_scalar
import argparse
import numpy as np
from discourse.util import bar, pairwise, ibm_pairwise, read_documents, encode_documents


def count(T, V, insertion=False):
    """
    Count unigram and bigram patterns in training data

    Arguments
    ---------
    T: training data encoded as numpy arrays of ids
    V: size of the vocabulary (which might include a null symbol)
    insertion: whether or not insertion is considered (in which case the null symbol takes id 0 in the vocabulary)

    Returns
    -------
    unigram counts: a numpy array of size V
    bigram counts: a V by V numpy array
    """
    # counts
    U = np.zeros(V)
    B = np.zeros((V, V))

    getpairs = ibm_pairwise if insertion else pairwise

    # counting
    for D in bar(T):
        if insertion:  # if we have null tokens we count one occurrence for each sentence in the document (that can head a pair of sentences)
            U[0] += len(D) - 1
        for Sa in D:
            for u in Sa:
                U[u] += 1
        for Sa, Sb in getpairs(D):
            for u, v in itertools.product(Sa, Sb):
                B[u,v] += 1

    return U, B


def loglikelihood(T, U, B, c=0, insertion=False):
    """
    Returns the log likelihood of the data

    Arguments
    ---------
    T: training data encoded by `encode_documents`
    U: unigram counts as produced by `count`
    B: bigram counts as produced by `count`
    c: smoothing constant (in absolute discounting smoothing)
    insertion: whether or not insertion is considered

    """
    ll = 0.0
    
    getpairs = ibm_pairwise if insertion else pairwise

    for D in T:
        # for each sentence pair
        for Sa, Sb in getpairs(D):  # if insertion=True, then getpairs=ibm_pairwise, consequently, Sa[0] is the null word
            # for each pattern in the second sentence of the pair
            for v in Sb:
                # sum up the contributions of the pattern v conditioned on each pattern u in the first sentence of the pair
                ll += np.log(1.0/len(Sa)) + np.log(np.sum([float(B[u,v] + c)/(U[u] + c * len(U)) for u in Sa]))

    return ll


def minimize(T, U, B, insertion):
    """optimise the likelihood of T"""
    
    def f(c, T, U, B, insertion):
        logging.info('Computing minus log likelihood with c=%f', c)
        ll = loglikelihood(T, U, B, c, insertion)
        logging.info('average likelihood: %f', -ll/len(T))
        return -ll/len(T)

    return minimize_scalar(f, bounds=(0.0, 1.0), args=(T, U, B, insertion), method='bounded')


def parse_args():
    """parse command line arguments"""

    parser = argparse.ArgumentParser(description='Hyperparameter tuning via MLE',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('output', 
            type=str,
            help="prefix for output files")
    parser.add_argument('--insertion', '-i',
            action='store_true',
            help='allows for insertion (obviating the need for a smoothing constant)')
    parser.add_argument('--smoothing', '-c',
            type=float, default=0.0,
            help='smoothing constant in absolute discounting')
    parser.add_argument('--boundary', '-b',
            action='store_true',
            help='add document boundary tokens')
    parser.add_argument('--mle',
            action='store_true',
            help="chooses c to maximise the data's likelihood (useless, note that this will retrieve the MLE solution, i.e. c=0)")
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

    # read in documents
    logging.info('Reading documents in ...')
    documents = read_documents(sys.stdin, args.boundary)
    logging.info('%d documents, on average %.2f sentences per document', len(documents), np.mean([len(D)for D in documents]))
   
    # decide whether or not there will be a null symbol
    null_symbol = '<null>' if args.insertion else None
    # encode documents using numpy array of ids
    T, vocab = encode_documents(documents, null_symbol)
   
    # gather unigram and bigram counts
    logging.info('Counting ...')    
    U, B = count(T, len(vocab), insertion=args.insertion)
    logging.info('%d unigrams, %d bigrams', U.size, B.size)

    # compute log likelihood
    logging.info('Computing likelihood ...')
    ll = loglikelihood(T, U, B, args.smoothing, args.insertion)
    logging.info('Negative log likelihood %f with c=%f and insertion=%s', -ll, args.smoothing, args.insertion)
    
    # dumps U and B in a nice format
    tokens = [t for t, i in sorted(vocab.iteritems(), key=lambda (t, i): i)]
    V = len(tokens)
    logging.info('Writing unigrams to: %s', '{0}.unigrams'.format(args.output))
    with open('{0}.unigrams'.format(args.output), 'w') as fu:
        print >> fu, '#pattern\t#count'
        for u, n in sorted(enumerate(U), key=lambda (u, n): n, reverse=True):
            print >> fu, '{0}\t{1}'.format(tokens[u], n)
    logging.info('Writing bigrams to: %s', '{0}.bigrams'.format(args.output))
    with open('{0}.bigrams'.format(args.output), 'w') as fb:
        print >> fb, '#trigger\t#pattern\t#count'
        for u in xrange(V):
            # we iterate over triggers so that the most likely ones come first
            for v in sorted(itertools.ifilter(lambda v: B[u,v], xrange(V)), key=lambda v: B[u,v], reverse=True):
                print >> fb, '{0}\t{1}\t{2}'.format(tokens[u], tokens[v], B[u,v])

    # legacy options: optimise likelihood
    if args.mle:
        logging.info('Minimising negative log likelihood')
        print minimize(T, U, B, args.insertion)


if __name__ == '__main__':

    main(parse_args())

