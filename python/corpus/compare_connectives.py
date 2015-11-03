'''
Takes as input a list of connectives, as output by discourse tagger (Pitler and Nenkova, http://www.cis.upenn.edu/~nlp/software/discourse.html)
 and previously extracted by script (analyse_connectives.py)

Created on 6 Oct 2015

@author: Karin
'''  
import logging, argparse, os
from collections import defaultdict

def main(args):    
    """input in format:
     32      If#53#Contingency 
     Read in PE and MT files
     Compare discourse sense per line
     Log errors: if for that line, PE inserted connective where MT has none, or different sense
     """
    MT_connectives_per_doc = defaultdict(list)
    PE_connectives_per_doc  = defaultdict(list)
    
    extract_connectives(args.directory+os.sep+'pe',  PE_connectives_per_doc)
    extract_connectives(args.directory+os.sep+'mt',  MT_connectives_per_doc)
    print PE_connectives_per_doc
    print MT_connectives_per_doc
    derive_errors(PE_connectives_per_doc, MT_connectives_per_doc, args.output)
    
def derive_errors(PE_files, MT_files, output):
    errors_per_doc = defaultdict(list)
    errors_missing = defaultdict(list)
    errors_sense = defaultdict(list)
    errors_deleted = defaultdict(list)
    for filename in PE_files:
        PE_connectives = PE_files[filename]
        print 'compare '
        print PE_connectives 
        file = filename.replace('pe','mt')
        print 'and '+file 
        MT_connectives = MT_files[file]
        print MT_connectives 
        for line in PE_connectives:
            items = PE_connectives[line]
            #if not items for MT, add as errors
            MT_items = MT_connectives[line]
            if not MT_items:
                errors_missing[line] = items
            #if wrong sense, add as error
            else:
                for item in items:
                    if item not in MT_items:
                        errors_sense[line] = item
        #ones that have been deleted in the post edit
        for line in MT_connectives:
            
        
    
    if not os.path.exists(output):
        os.makedirs(output)
    with open(os.path.join(output, filename+'_errors'), 'w') as output: 
        #output.write(errors)
        print 'ERRORS:'
        print errors_missing
        print errors_sense
        errors = errors_missing.copy()
        errors.update(errors_sense)
        errors_per_doc[filename]=errors
        for k,values in errors_missing.items():
            output.write(k+' ')
            for v in values:
                output.write(v+' ')
            output.write('\n')
        for k,v in errors_sense.items():
            output.write(k+' ')
            output.write(v+' ')
            output.write('\n')
        
    print errors_per_doc
    
def extract_connectives(directory, connectives_per_doc):
    
    files = [name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name)) ]
    for filename in files:
        logging.info(filename)
        connectives = defaultdict(list)
        with open(os.path.join(directory, filename)) as fi:
            prev = ''
            for line in fi:
                items = line.split()
                #for item in items:
                line_no = items[0]
                item = items[1]
                tokens = item.split('#')
                print 'line='+line_no+' dc= '+tokens[0]+' sense='+tokens[2]
                if tokens[1] == prev:
                    print 'is shared: '#+ connectives[line_no][tokens[2]]+tokens[0]
                    temp = connectives[line_no][-1]
                    print 'was '+temp
                    print 'now='+temp+' '+tokens[0]
                    connectives[line_no][-1] = temp+' '+tokens[0]
                    #connectives[line_no][tokens[2]] = connectives[line_no][tokens[2]]+tokens[0]
                else:
                    connectives[line_no].append(tokens[2]+':'+tokens[0])
                prev = tokens[1]
                
            print connectives
            connectives_per_doc[filename] = connectives
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


#C:\SMT\corpus_work\tagger_output\connectives
if __name__ == '__main__':
    main(argparser())