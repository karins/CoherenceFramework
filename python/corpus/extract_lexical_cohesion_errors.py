'''
Created on 8 Oct 2015

@author: Karin
'''
import argparse, logging, os
from collections import defaultdict

def main(args):
    """ Extract nouns out of parsed file. Presumption is that if Noun is edited out of MT then it is an error, not mere lexical whim. 
    input format: (S1 (S (NP (DT The) (NN public)) (VP (MD will) (ADVP (RB soon)) (VP (AUX have) (NP (DT the) (NN opportunity) ...
    """
    MT_nouns_per_doc = defaultdict(list)
    PE_nouns_per_doc  = defaultdict(list)
    
    extract_nouns(args.directory,args.output)
    #extract_nouns(args.directory+os.sep+'pe',  PE_nouns_per_doc)
    #extract_nouns(args.directory+os.sep+'mt',  MT_nouns_per_doc)
    
    derive_errors(args.directory+os.sep+'pe')
    
def derive_errors(PE_files, MT_files, output):
#12      mass exodus NATO intervention end Serbian reign quasi-state auspices UN solution independence  
#12      mass exodus NATO intervention end reign Serbia quasi tat auspices UN solution independence  
    errors_per_doc = defaultdict(list)
    errors_missing = defaultdict(list)
    errors_sense = defaultdict(list)
    for filename in PE_files:
        PE_nouns = PE_files[filename]
        print 'compare '
        print PE_nouns 
        file = filename.replace('pe','mt')
        print 'and '+file 
        MT_nouns = MT_files[file]
        print MT_nouns 
        for line in PE_nouns:
            items = PE_nouns[line]
            #if not items for MT, add as errors
            MT_items = MT_nouns[line]
            

            
def extract_nouns(directory, output):
    
    files = [name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name)) ]
    for filename in files:
        logging.info(filename)
        nouns = defaultdict(list)
        with open(os.path.join(directory, filename)) as fi:
            if not os.path.exists(output):
                os.makedirs(output)
            with open(os.path.join(output, filename ), 'w') as fo:
                line_no = 0
                for line in fi:
                    fo.write(str(line_no)+' \t ')
                    #print line
                    items = line.split()
                    for i in range(len(items)):
                        item = items[i]
                        #(S1 (S (NP (DT The) (NN public))
                        if 'NN' in item or 'NNS' in item:
                            print items[i+1].rstrip(')')
                            if '#' not in items[i+1]:
                                nouns[filename].append(items[i+1].rstrip(')'))
                                fo.write(items[i+1].rstrip(')')+' ')
                    fo.write(' \n')
                    line_no +=1 
                print nouns
                
                            
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