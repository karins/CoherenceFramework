"""

Input format (ignore the header and the first column, they are there just for illustration)

    e1 e2 e3
s1  S  -  O
s2  -  S  -
s3  S  O  X

@author: wilkeraziz
"""
import argparse
import numpy as np
import sys
import logging
import itertools
from discourse.util import pairwise
from discourse.doctext import iterdoctext
from discourse import command
import functools

# TODO: generalise vocabulary of roles
r2i = {'S': 3, 'O': 2, 'X': 1, '-': 0}
i2r = {v: k for k, v in r2i.iteritems()}


def read_grids(istream, str2int):
    return [np.array([[str2int[role] for role in line] for line in lines], int) for lines, attrs in iterdoctext(istream)]


def train(corpus, vocab_size, salience):
    U = np.zeros(vocab_size, int)
    B = np.zeros((vocab_size, vocab_size), int)
    for grid in corpus:
        for entity_roles in grid.transpose():
            #not v pythonesque :(
            if not ( salience is None) and get_role_count(entity_roles) >= salience:
                for r in entity_roles:
                    U[r] += 1
                for ri, rj in pairwise(entity_roles):
                    B[ri,rj] += 1
    return U, B

def get_role_count(entity_roles):
    
    from collections import Counter
    roles = Counter(entity_roles)
    temp = functools.reduce(lambda x, y: x+y,  Counter(entity_roles).values())
    
    return temp - roles[0]

def main(args):
    """load grids and extract unigrams and bigrams"""

    logging.basicConfig(
            level=(logging.DEBUG if args.verbose else logging.INFO), 
            format='%(levelname)s %(message)s')

    training = read_grids(args.input, r2i)
    logging.info('Training set contains %d docs', len(training))
    unigrams, bigrams = train(training, len(r2i), args.salience) 
    logging.info('%d unigrams and %d bigrams', unigrams.size, bigrams.size)
    
    # save unigrams and bigrams
    # this is nice ;) but perhaps for now we are interested in a more human readable format
    # np.savetxt('{0}.unigrams'.format(args.output), unigrams)
    # np.savetxt('{0}.bigrams'.format(args.output), bigrams)
    with open('{0}.unigrams'.format(args.output), 'w') as fu:
        print >> fu, '#role\t#count'
        for rid, count in enumerate(unigrams):
            print >> fu, '{0}\t{1}'.format(i2r[rid], count)
    with open('{0}.bigrams'.format(args.output), 'w') as fb:
        print >> fb, '#role\t#role\t#count'
        for r1, r2 in itertools.product(xrange(len(r2i)), xrange(len(r2i))):
            print >> fb, '{0}\t{1}\t{2}'.format(i2r[r1], i2r[r2], bigrams[r1,r2])
    

@command('grid', 'entity-based')
def argparser(parser=None, func=main):
    """parse command line arguments"""

    if parser is None:
        parser = argparse.ArgumentParser(prog='grid')
    
    parser.description = 'Generative implementation of Entity grid'
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    
    parser.add_argument('input', nargs='?', 
            type=argparse.FileType('r'), default=open(sys.argv[1], 'r'),
            help='input corpus in doctext format')
    
    parser.add_argument('output', 
            type=str,
            help="prefix for model files")
    
    parser.add_argument('salience', default=0,
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
