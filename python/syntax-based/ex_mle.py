import itertools
import math
import sys
from collections import defaultdict
from scipy.optimize import minimize_scalar


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
                

def main(n, stem):
    T = []
    for index in range(n):
        with open(stem + str(index), 'r') as fi:
            T.append(read_data(fi))
    unigrams, bigrams = count(T)
    print minimize(T, unigrams, bigrams)


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print >> sys.stderr, 'Usage: %s stem n' % (sys.argv[0])
        sys.exit(0)

    main(int(sys.argv[2]), sys.argv[1])

