"""
IBM 1 for syntax-based coherence
--------------------------------

* Training corpus: a set of documents
* Document: a list of sentences
* Sentence: a set of syntactic patterns

Suppose (E, F) adjacent sentences in a document.
Let f1..fm be m syntactic patterns in F
which are triggered by n patterns (e1, e2, ..., en) in E.

Then we can define an aligment a: fi -> ej, where e0 is a special position associated with a NULL symbol.

Then for a given alignment:

    t(f1..fm, a1..am | e1..en) = \prod_i t(fi,ai | e_ai)

In practice we do not have aligned data, thus to estimate t(F|E) we marginalise over all possible alignments.

1. we start with uniform parameters t(f|e)
        V = len(vocab)     # vocab size including the null symbol
        T = ones((V,V))/V  # uniform distribution
2. EM: we iterate over the training set gathering fractional counts (E-step) and updating our model (M-step)
        until convergence:
            # E-step
            c(f,e) = zeros(V,V)
            c(e) = zeros(V)
            for D in T:
                for (e0..en), (f1..fm) in pairwise(D):
                    c(f,e) = c(f,e) + t(f,e)/sum(t(f|ej) for ej in e0..en)
            # M-step 
            t(e|f) = c(e,f)/c(c)
3. convergence can be assessed in terms of the likelihood of the training set
        \sum_D \sum_(F,E) \sum_i log( \sum_j t(fi|ej) )
                
@author: wilkeraziz
"""

import sys
import logging
import itertools
import argparse
import numpy as np
from discourse.util import bar, ibm_pairwise, read_documents, encode_documents


def loglikelihood(corpus, T, progress=False):
    """computes -log(likelihood(T))"""
    L = np.zeros(len(corpus))
    for i, D in bar(enumerate(corpus), maxval=len(corpus), none=not progress, msg='log likelihood'):
        # for each sentence pair
        for E, F in ibm_pairwise(D):
            # for each pattern in the second sentence of the pair
            for f in F:
                # sum up the contributions of the pattern v conditioned on each pattern u in the first sentence of the pair
                L[i] += np.log(T[f,E].sum())
    return L


def ibm1(corpus, V, max_iterations, min_gain, progress=False):
    """
    Estimates t(f|e) where (e, f) are syntactic patterns in adjacent sentences in a document.
    
    Arguments
    ---------
    corpus: training data encoded using numpy arrays of vocab ids (integers) 
        where the id 0 represents the null symbol
    V: vocabulary size
    max_iterations: maximum number of iterations (current convergence criterion)

    Return
    ------
    T[f,e] = t(f|e) as a numpy array
    """

    T = np.ones((V, V), float) / V   # T[f,e] = t(f|e)
    LL = []
    
    LL.append(-loglikelihood(corpus, T, progress).sum())
    logging.info('Initial log likelihood %f', LL[-1])

    for i in range(max_iterations):
        logging.info('Iteration %d', i)
        C = np.zeros((V, V), float)  # C[f,e] = c(f,e)
        N = np.zeros(V, float)       # N[e] = c(e)
        # E-step
        for D in bar(corpus, none=not progress, msg='E-step'):
            # for each sentence pair
            for E, F in ibm_pairwise(D):
                Z = np.zeros(V, float)  # Z[fi] = \sum_j t(fi|ej)
                # normalising factor 
                for f in F:
                    Z[f] = T[f,E].sum()  # this notation can be tricky to read: we are summing for row f the cells in columns indexed by elements of E
                # gather (normalised) fractional counts
                for e, f in itertools.product(E, F):
                    c = T[f,e]/Z[f]
                    C[f,e] += c
                    N[e] += c
        # M-step
        for f, e in bar(itertools.product(range(V), range(V)), maxval=V*V, none=not progress, msg='M-step'):
            T[f,e] = C[f,e] / N[e] 
    
        LL.append(-loglikelihood(corpus, T, progress).sum())
        gain = - LL[-1] + LL[-2]
        logging.info(' log_likelihood=%f log_gain=%f', LL[-1], gain)
        if gain <= min_gain:
            break

    LL = np.array(LL)
    logging.info('Final negative log likelihood %f ', LL[-1])
    return T, LL

     
def parse_args():
    """parse command line arguments"""

    parser = argparse.ArgumentParser(description='IBM model 1 for syntax-based coherence',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input', nargs='?', 
            type=argparse.FileType('r'), default=sys.stdin,
            help='input corpus in doctext format')
    parser.add_argument('output', nargs='?', 
            type=argparse.FileType('w'), default=sys.stdout,
            help='output IBM1 estimates')
    parser.add_argument('--ll',
            type=str,
            help='store the progression of the likelihood')
    parser.add_argument('--max-iterations', '-m',
            type=int, default=50,
            help='maximum number of iterations')
    parser.add_argument('--min-gain', '-g',
            type=int, default=np.log(10),
            help='minimum loglikelihood gain between two iterations (in log domain)')
    parser.add_argument('--boundary', '-b',
            action='store_true',
            help='add document boundary tokens')
    parser.add_argument('--progress', '-p',
            action='store_true',
            help='display progress information')
    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')

    args = parser.parse_args()

    logging.basicConfig(
            level=(logging.DEBUG if args.verbose else logging.INFO), 
            format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

    return args


def main(args):
    # read documents 
    logging.info('Reading documents in...')
    documents = read_documents(args.input, args.boundary)
    logging.info('%d documents read', len(documents))

    # maps tokens to integer ids (0 is reserved for a special <null> symbol)
    # and encodes the training data using numpy arrays of vocab ids
    logging.info('Making vocab')
    corpus, vocab = encode_documents(documents, '<null>')
    logging.info('%d tokens read (including <null>)', len(vocab))

    # estimates parameters T[f,e] = t(f|e)
    # where (e, f) are syntactic patterns occurring in adjacent sentences in a document
    T, LL = ibm1(corpus, len(vocab), args.max_iterations, args.min_gain, args.progress)
    T = np.nan_to_num(T)
    
    # store the log-likelihood values
    if args.ll:
        with open(args.ll, 'w') as fo:
            [fo.write('{0}\n'.format(ll)) for ll in LL]

    # dumps T in a nice format
    tokens = [t for t, i in sorted(vocab.iteritems(), key=lambda (t, i): i)]
    V = len(tokens)
    # we print a header so that the meaning of each column is clear
    print >> args.output, '#trigger\t#pattern\t#p(pattern|trigger)'  # note that e=trigger and f=pattern 
    # we iterate over f in no particular order (simply that of the vocabulary ids)
    for f in xrange(V):
        # we iterate over triggers so that the most likely ones come first
        for e in sorted(itertools.ifilter(lambda e: T[f,e], xrange(V)), key=lambda e: T[f,e], reverse=True):
            print >> args.output, '{0}\t{1}\t{2}'.format(tokens[e], tokens[f], T[f,e])


if __name__ == '__main__':
    main(parse_args())


