'''
Created on 5 Oct 2015

@author: Karin

Compare 2 sets of files, representing the MT and PE output of particular documents from the LIG corpus.
-Count the connectives in each.
-count the types of connectives in MT vs PE 

'''


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
import logging,os,argparse

def main(args):
    connectives = {}
    #extract from MT
    extract_connectives(args, connectives)
    #extract from PE
    #extract_connectives(args, connectives)
    #analyse
    
def extract_connectives(args, connectives):    
    files = [name for name in os.listdir(args.directory) if os.path.isfile(os.path.join(args.directory, name)) ]
    for filename in files:
        logging.info(filename)
        
        with open(os.path.join(args.directory, filename)) as fi:
            if not os.path.exists(args.output):
                os.makedirs(args.output)
            with open(os.path.join(args.output, filename ), 'w') as output:
                #output.write(filename)
                line_no = 0
                for line in fi:
                    if '#' in line:
                        items = line.split()
                        for item in items:
                            if '#' in item:
                                tokens = item.split('#')
                                if tokens[2][0] != '0':
                                    print str(line_no)+' \t '+item.rstrip(')')
                                    output.write(str(line_no)+' \t '+item.rstrip(')'))
                                    output.write(' \n')
                        line_no+=1
                        #connectives[ ] = 
                
                    
                        
                        
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