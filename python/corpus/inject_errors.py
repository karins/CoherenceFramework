'''
Created on 9 Oct 2015

@author: Karin
'''
import argparse, logging, os

def main(args):
    """ Take errors from error file and insert into reference file, with relevant markup. 
    Errors may take various forms. Input may be parsed file or plain text.
PE:
1      after#9#Temporal 
5      but#43#Comparison 
5      as#58#Temporal 
6      because#2#Contingency 
7      Indeed#7#Expansion 
MT:
0      Yet#17#Comparison     
1      when#10#Temporal     
5      but#13#Comparison 
6      because#2#Contingency 
7      Indeed#5#Expansion
 
  Actual error injected into postedited sentence, which is then replaced in reference translation.. As MT too distant from REF stylistically.
    """
    
    inject_errors(args.directory+os.sep+'ref',args.directory+os.sep+'pe',args.directory+os.sep+'mt',  errors_per_doc)
    
def inject_errors():
    """ params: plain text reference file to be injected, post-edited version, machine-translated version, list of errors 
    PE: (S1 (S (S (NP (NP (DT Another) (JJ crucial) (NN step)) (PP (IN for#39#0) (NP (NP (DT the) (NNPS Balkans
    MT: (S1 (S (CC Yet#17#Comparison) (S (NP (NP (DT a) (JJ crucial) (NN step)) (PP (IN for#18#0) (NP (NP (DT the) (NNPS Balkans))
    1 find position of connective in sentence"""
    
    
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