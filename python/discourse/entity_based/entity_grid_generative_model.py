'''

Algorithm for generative entity grid. Takes the transitions from training.
Created on 25 Nov 2014

@author: Karin
'''
import argparse
import logging
import itertools
import math 
import numpy as np
from grid import read_grid 

#def read_unigrams(file):
#    np.loadtxt(file).reshape((4,5,10))
    
#def read_bigrams(file):
#    np.loadtxt(file).reshape((4,5,10))

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    
    #Make an iterator that aggregates elements from each of the iterables.
    return itertools.izip(a, b) 


def compute_coherence(doc_set, unigrams, bigrams):

#probabilities for individual columns are normalized by column
#length (n) and the probability of the entire text is normalized
#by the number of columns (m):
    coherence = 0.0
    coherence_scores = {}
    
    # for each document
    for doc in doc_set:
        # for each sentence pair
        for Sa, Sb in pairwise(doc):
            # for each transition in the second sentence of the pair
            for v in Sb:
                # sum up the contributions of the pattern v conditioned on each pattern u in the first sentence of the pair
                prob_v_given_u = sum((float(bigrams.get((u, v), 0)))/(float(unigrams.get(u, 0))) for u in Sa)

                # compute the contribution of pattern v in Sb to the training likelihood
                coherence += math.log(1.0/len(Sa)) + math.log(prob_v_given_u)

                coherence/len()
                
    return coherence_scores

def main(args):
    """load data and compute the coherence"""
    data_set = []
    for index in range(args.n):
        path = args.prefix + str(index)
        logging.info('Processing %s', path)
        with open(path, 'r') as fi:
            data_set.append(read_grid(fi))
    unigrams = np.loadtxt(args.unigramfile)
    bigrams = np.loadtxt(args.bigramfile)
    logging.info( unigrams)
    logging.info( bigrams)
    #unigrams = read_unigrams(unigram_file)
    #bigrams = read_bigrams(bigram_file)
    print compute_coherence(data_set, unigrams, bigrams)
            

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
    
if __name__ == '__main__':
     main(parse_args())