"""

Algorithm for generative entity grid. Takes the transitions from training.
Created on 25 Nov 2014

@author: Karin Sim
"""
import sys
import argparse
import logging
import itertools
import traceback
import numpy as np
from discourse.util import pairwise, smart_open
from grid import read_grids, r2i, i2r
from discourse import command
from multiprocessing import Pool
from functools import partial


def read_unigrams(istream, str2int):
    U = np.zeros(len(str2int), int)
    for line in istream:
        if line.startswith('#'):
            continue
        line = line.strip()
        if not line:
            continue
        role, count = line.split('\t')
        U[str2int[role]] = int(count)
    return U


def read_bigrams(istream, str2int):
    B = np.zeros((len(str2int), len(str2int)), int)
    for line in istream:
        if line.startswith('#'):
            continue
        line = line.strip()
        if not line:
            continue
        r1, r2, count = line.split('\t')
        B[str2int[r1], str2int[r2]] = int(count)
    return B


def grid_loglikelihood(grid, U, B, salience=0):
    # sum_i sum_j log p(rj|ri)
    # where p(rj|ri) = c(ri,rj)/c(ri)
    logprob = np.sum([
        np.sum(
            [np.log( np.divide(float(B[ri,rj]), U[ri])) for ri, rj in pairwise(entity_roles)])
        for entity_roles in grid.transpose()])
    # probabilities for individual columns are normalized by column
    # length (n) and the probability of the entire text is normalized
    # by the number of columns (m):
    return logprob / grid.size


def loglikelihood(corpus, U, B, salience):
    return np.array([grid_loglikelihood(grid, U, B, salience) for grid in corpus])
    

def wrapped_loglikelihood(corpus, U, B, salience):
    try:
        return loglikelihood(corpus, U, B, salience)
    except:
        raise Exception(''.join(traceback.format_exception(*sys.exc_info())))


def decode_many(unigrams, bigrams, salience, ipaths, opaths, jobs, estream=sys.stderr):

    # reads in the model
    logging.info('Reading unigrams from: %s', unigrams)
    U = read_unigrams(smart_open(unigrams), r2i)
    logging.info('Read in %d unigrams', U.size)

    logging.info('Reading bigrams from: %s', bigrams)
    B = read_bigrams(smart_open(bigrams), r2i)
    logging.info('Read in %d bigrams', B.size)
    
    
    tests = [None] * len(ipaths)
    for i, ipath in enumerate(ipaths):
        documents = read_grids(smart_open(ipath), r2i)
        logging.info('%s: %d test documents read', ipath, len(documents))
        tests[i] = documents 

    # computes the log likelihood of each document in each test file
    pool = Pool(jobs)
    all_L = pool.map(partial(wrapped_loglikelihood, U=U, B=B, salience=salience), tests)

    print >> estream, '#file\t#sum\t#mean'
    for ipath, opath, test, L in itertools.izip(ipaths, opaths, tests, all_L):
        with smart_open(opath, 'w') as ostream:
            # dumps scores
            print >> ostream, '#doc\t#logprob\t#sentences\t#entities'
            for i, ll in enumerate(L):
                num_sentences = test[i].shape[0]
                num_entities = test[i].shape[1]
                print >> ostream, '{0}\t{1}\t{2}\t{3}'.format(i, ll, num_sentences, num_entities)
            print >> estream, '{0}\t{1}\t{2}'.format(opath, L.sum(), np.mean(L))


def main(args):
    """load data and compute the coherence"""
    logging.basicConfig(
            level=(logging.DEBUG if args.verbose else logging.INFO), 
            format='%(levelname)s %(message)s')
    U = read_unigrams(args.unigrams, r2i)
    logging.info('Read in %d unigrams', U.size)
    B = read_bigrams(args.bigrams, r2i)
    logging.info('Read in %d bigrams', B.size)
    test = read_grids(args.input, r2i)
    logging.info('Scoring %d documents', len(test)) 
    print >> args.output, '#docid\t#loglikelihood'
    for i, grid in enumerate(test):
        ll = grid_loglikelihood(grid, U, B, args.salience)
        print >> args.output, '{0}\t{1}'.format(i, ll)
            

@command('grid_decoder', 'entity-based')
def argparser(parser=None, func=main):
    """parse command line arguments"""
    
    if parser is None:
        parser = argparse.ArgumentParser(prog='grid_decoder')

    parser.description = 'Generative implementation of Entity grid '
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    
    parser.add_argument('unigrams', 
            type=argparse.FileType('r'),
            help="path for unigram file")
    parser.add_argument('bigrams', 
            type=argparse.FileType('r'),
            help="path for bigram file")
    parser.add_argument('input', nargs='?', 
            type=argparse.FileType('r'), default=sys.stdin,
            help='input corpus in doctext format')
    parser.add_argument('output', nargs='?', 
            type=argparse.FileType('w'), default=sys.stdout,
            help='output probabilities')
    parser.add_argument('--salience', default=0,
            type=int,
            help='salience variable for entities')
    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')
   
    if func is not None:
        parser.set_defaults(func=func)
     
    return parser
    
if __name__ == '__main__':
     main(argparser().parse_args())
