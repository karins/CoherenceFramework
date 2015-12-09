'''
Created on 5 Oct 2015

@author: Karin

Compare 2 sets of files, representing the MT and PE parsed output of particular documents which have been marked up with discourse
connectives by Pitler Nenkova tagger (http://www.cis.upenn.edu/~nlp/software/discourse.html).
-Count the connectives in each.
-count the types of connectives in MT vs PE 

'''
#! /usr/bin/python
#-*-coding:utf-8-*-

"""
For the excerpt below, which has been marked up using the Pitler tagger
 http://www.cis.upenn.edu/~epitler/discourse.html - paper: http://www.cis.upenn.edu/~epitler/papers/ACLShort09.pdf):
 1. Extract all connectives, identified by connective#number#type
 2. Compare those of MT with those of PE, to establish which have changed in post-edit
(S1 (S (CC Yet#17#Comparison) (S (NP (NP (DT a) (JJ crucial) (NN step)) 
(PP (IN for#18#0) (NP (NP (DT the) (NNPS Balkans)) 
(PP (IN Since#7#0) (NP (DT the) (NN world)))))) (VP (AUX is) (VP (VBN focused) (PP (IN on) (NP (NP (NNP Iraq)) (, ,) 
(NP (NNP North) (NNP Korea)) (CC and#24#0) (NP (NP (DT a) (JJ possible) (NN crisis)) (PP (IN with) (NP (NNP Iran))) 
(PP (IN over) (NP (JJ nuclear) (NNS weapons))))))))) (, ,) (NP (NNP Kosovo)) (VP (AUX is) (ADJP (RB somewhat) (JJ unnoticed))) (. .)))"""
import logging,os,argparse, re
from collections import defaultdict
import json

def main(args):
    #connectives = {}
    #extract from MT
    extract_connectives(args.directory, args.output)#, connectives)
    #extract from PE
    #extract_connectives(args, connectives)
    #analyse
    
def  extract_connectives(directory, outputdir, outputfile):
    connectives = {}
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    with open(os.path.join(outputdir, outputfile ), 'w') as output:        
        files = [name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name)) ]
        for filename in files:
            logging.info(filename) 
            doc = map(int, re.findall("\d+",filename))[0]
            connectives[doc]= defaultdict(list)
            with open(os.path.join(directory, filename)) as fi:
                line_no = 0
                connectives[doc][line_no] = []
                for line in fi:
                    #fo.write(str(line_no)+' \t ')
                    if '#' in line:
                        items = line.split()
                        for item in items:
                            if '#' in item:
                                tokens = item.split('#')
                                print tokens
                                if tokens[0].isalnum() and tokens[2][0] != '0':
                                    print str(line_no)+' \t '+item.rstrip(')')
                                    output.write(str(doc) +' \t ' +str(line_no)+' \t '+item.rstrip(')'))
                                    output.write(' \n')
                                    connectives[doc][line_no].append(item.rstrip(')'))
                    line_no+=1
                        #connectives[ ] = 
    f = open( outputdir+os.sep+ outputfile+'_json', 'w')
    f.write( json.dumps(connectives) )
                    
                        
                        
def argparser():
    """parse command line arguments"""
    
    parser = argparse.ArgumentParser(description='Remove the leading alphanumeric from each line.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('directory', nargs='?',
                        type=str, 
                        help='input directory')
    
    parser.add_argument('--output', nargs='?',
                        type=str, 
                        help='output directory')
    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')
    
    args = parser.parse_args()
    
    logging.basicConfig(
            level=(logging.DEBUG if args.verbose else logging.INFO), 
            format='%(levelname)s %(message)s')
    return args


if __name__ == '__main__':
    main(argparser())