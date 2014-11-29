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
from grid import read_grid , r2i

#convert to dictionary from numpy [ 146.    7.    8.    4.]
#r2i = {'S': 3, 'O': 2, 'X': 1, '-': 0}
def read_unigrams(raw_unigrams):
    unigrams = {}
    for idx in range(len(raw_unigrams)):
        unigrams[get_role(idx)] = raw_unigrams[idx]
    logging.info(unigrams)
    return unigrams

'''  grid indexing to create following format:
    -- -X -O -S
    X- XX XO XS
    O- OX OO OS
    S- SX SP SS
 '''
def read_bigrams(raw_bigrams):
    bigrams = {}
    
    for idx in range(len(raw_bigrams)):
        row = raw_bigrams[idx,:]
        
        for idx2 in range(len(row)): 
            bigrams[get_role(idx)+get_role(idx2)] = row[idx2]
    logging.info(bigrams)
    return bigrams

def get_role(value_to_match):
    for key, value in r2i.items():
        if value == value_to_match:
            return key

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
    coherence_scores = []
    
    # for each document
    for doc in doc_set:
        for entity_roles in doc.transpose():
            for ri, rj in pairwise(entity_roles):
                
                # sum up the probability of entity role ri conditioned on entity role rj in the first sentence of the pair
                logging.debug( 'entity: \''+get_role(ri) +get_role(rj)+'\' -> '+str(bigrams.get(get_role(ri)+get_role(rj))))
                logging.debug( 'unigram: \''+get_role(ri)+'\' -> '+ str(unigrams.get( get_role(int(ri))) ))
                #prob = float(bigrams.get(str(int(ri)) +str(int(rj)), 0))/float(unigrams.get(str(int(ri)), 0))
                prob = bigrams.get(get_role(ri)+get_role(rj), 0)/unigrams.get( get_role(int(ri)),0) 
                logging.debug( 'prob '+str(prob)) 
                coherence += math.log(prob)
        m = doc.shape[0]
        n =doc.shape[1]
        coherence_scores.append( ( 1 /(m * n)) *  coherence)
        
         
    return coherence_scores

def main(args):
    """load data and compute the coherence"""
    data_set = []
    for index in range(args.n):
        path = args.prefix + str(index)
        logging.info('Processing %s', path)
        with open(path, 'r') as fi:
            data_set.append(read_grid(fi))
    coded_unigrams = np.loadtxt(args.unigramfile)
    coded_bigrams = np.loadtxt(args.bigramfile)
    logging.info(coded_unigrams)
    logging.info(coded_bigrams)
    unigrams = read_unigrams(coded_unigrams)
    bigrams = read_bigrams(coded_bigrams)
    
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