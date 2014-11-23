import itertools
import math
import sys
from collections import defaultdict
from scipy.optimize import minimize_scalar


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


def minusloglikelihood(c, T, bigrams, unigrams):
    ll = 0.0
    # for each document
    for D in T:
        # for each sentence pair
        for Sa, Sb in pairwise(D):
            # for each pattern in the second sentence of the pair
            for v in Sb:
                # sum up the contributions of the pattern v conditioned on each pattern u in the first sentence of the pair
                prob_v_given_u = sum((float(bigrams.get((u, v), 0)))/(float(unigrams.get(u, 0)) + c * len(unigrams)) for u in Sa)
                #prob_v_given_u = sum((bigrams[u,v] + c)/(unigrams[u] + c * len(unigrams)) for u in Sa)
                # compute the contribution of pattern v in Sb to the training likelihood
                ll += math.log(1.0/len(Sa)) + math.log(prob_v_given_u)
    #return -ll
    return -ll/len(T)

def read_data(file):

    doc = []
    #file format:
    #WHNP*wp SQ*vbz 
    #PP*in NP-TMP*nnp NP*np VP*md 
    
    for line in file:
        
        tuples =line.split()
        sentence = []
        for tuple in tuples:            
            sentence.append(tuple)
        doc.append(sentence)
            
    #print 'returning '+str(len(doc))+' lines'
    return doc

def minimize(T, bigrams, unigrams):
    return minimize_scalar(minusloglikelihood, bounds=(0.0, 1.0), args=(T, bigrams, unigrams), method='bounded')

T = []
#for all docs to given index
for index in range(int(sys.argv[2])):
    T.append(read_data(open(sys.argv[1]+str(index), 'r')))
# document 1
d1_s1 = ['(S (NP VP))', '(NP (D N))', '(VP (V))']
d1_s2 = ['(S (NP VP))', '(NP (D NP))', '(NP (J N))', '(VP (V))']
d1_s3 = ['(S (NP VP))', '(NP (D NP))', '(NP (J N))', '(VP (V))']
d1_s4 = ['(S (NP))', '(NP (D NP))', '(NP (J N))']
d1_s5 = ['(S (NP))', '(NP (D N))']
D1 = [d1_s1, d1_s2, d1_s3, d1_s4, d1_s5] 
# document 2
d2_s1 = ['(S (NP VP))', '(NP (D N))', '(VP (V PNP))', '(PNP (P NP))']
d2_s2 = ['(S (VP))', '(VP (V))']
d2_s3 = ['(S (NP VP))', '(NP (D N))', '(VP (VP NP))', '(VP (V))', '(NP (N))']
D2 = [d2_s1, d2_s2, d2_s3] 
 
# training data
#T = [D1, D2]

#unigrams =  get_unigrams(open(sys.argv[3]))
#bigrams =  get_bigrams(open(sys.argv[4]))
unigrams = defaultdict(float)
bigrams = defaultdict(float)

for D in T:
    for Sa in D:
        for u in Sa:
            unigrams[u] += 1
    for Sa, Sb in pairwise(D):
        for u, v in itertools.product(Sa, Sb):
            bigrams[(u, v)] += 1
            
            

print minimize(T, bigrams, unigrams)
