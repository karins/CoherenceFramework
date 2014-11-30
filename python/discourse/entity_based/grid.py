"""

Input format (ignore the header and the first column, they are there just for illustration)

    e1 e2 e3
s1  S  -  O
s2  -  S  -
s3  S  O  X

"""
import argparse
import numpy as np
import itertools
import math
import sys
import logging
from collections import defaultdict

r2i = {'S': 3, 'O': 2, 'X': 1, '-': 0}

def read_grid(file):
    
    #doc = np.array([np.array([r2i[r] for r in line.strip().split()]) for line in file])
    doc = np.array([np.array([r2i[line[idx]] for idx in range((len(line)-1))]) for line in file])
    logging.info( doc)
    
    return doc 



def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)

def train(corpus):
    
    U = np.zeros(len(r2i), int)
    B = np.zeros((len(r2i), len(r2i)), int)
    
    # counts
    for doc in corpus:
        for entity_roles in doc.transpose():
            #print 'transposed'
            #print doc
            for r in entity_roles:
                U[r] += 1
            for ri, rj in pairwise(entity_roles):
                B[ri,rj] += 1
                 
    return U,B


    
def parse_args():
    """parse command line arguments"""
    
    parser = argparse.ArgumentParser(description='Generative implementation of Entity grid ',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('prefix', 
            type=str,
            help="prefix for input files")  
    
    parser.add_argument('n',
            type=int,
            help='number of documents')
    
    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')
    
    parser.add_argument('unigramfile', 
            type=str,
            help="path for unigram file")
    
    parser.add_argument('bigramfile', 
            type=str,
            help="path for bigram file")
    
    args = parser.parse_args()
    
    logging.basicConfig(
            level=(logging.DEBUG if args.verbose else logging.INFO), 
            format='%(levelname)s %(message)s')
    return args

def main(args):
    """load grids and extract unigrams and bigrams"""
    data_set = []
    for index in range(args.n):
        path = args.prefix + str(index)
        logging.info('Processing %s', path)
        # read all docs first into data_set
        with open(path, 'r') as fi:
            data_set.append(read_grid(fi))
            
    unigrams,bigrams = train(data_set)    
    
    logging.info( unigrams)    
    logging.info( bigrams)
    
    """save unigrams and bigrams"""
    np.savetxt(args.unigramfile, unigrams)
    np.savetxt(args.bigramfile, bigrams)
    
if __name__ == '__main__':
     main(parse_args())
