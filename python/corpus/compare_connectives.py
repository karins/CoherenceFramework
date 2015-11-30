'''
Takes as input a list of connectives, as output by discourse tagger (Pitler and Nenkova, http://www.cis.upenn.edu/~nlp/software/discourse.html)
 and previously extracted by script (analyse_connectives.py)

Created on 6 Oct 2015

@author: Karin
'''  
import logging, argparse, os, re
import json, yaml
from collections import defaultdict
from extract_lexical_cohesion_errors import error2int,removed_in_PE,inserted_in_PE

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
    
def  extract_connective_errors(input_directory_pe, input_directory_mt, output):    
    MT_connectives_per_doc = defaultdict(list)
    PE_connectives_per_doc  = defaultdict(list)
    
    extract_connectives(input_directory_pe,  PE_connectives_per_doc)
    extract_connectives(input_directory_mt,  MT_connectives_per_doc)
    derive_errors(PE_connectives_per_doc, MT_connectives_per_doc, output)
    
def derive_errors(PE_connectives_per_doc, MT_connectives_per_doc, output):
    """
    from:
    1      after#9#Temporal 
    5      but#43#Comparison 
    5      as#58#Temporal 
    6      because#2#Contingency 
    7      Indeed#7#Expansion 
    11      and#21#Expansion 
    17 Expansion:in fact Comparison:while 
    
    0      Yet#17#Comparison 
    1      when#10#Temporal 
    5      but#13#Comparison 
    6      because#2#Contingency 
    7      Indeed#5#Expansion 
    11      and#29#Expansion 
    derive:
    17 Expansion:in fact Comparison:while 
    1 Temporal:after 
    5 Temporal:as
    """ 
    
    errors_per_doc = defaultdict(list)
    #errors_missing = defaultdict(list)
    #errors_sense = defaultdict(list)
    #errors_deleted = defaultdict(list)
    """presume that the errors for PE_files will include all docs under consideration - check if that is case"""
    for doc,lines in PE_connectives_per_doc.items():
        #PE_connectives = lines
        errors_per_doc[doc]=defaultdict(list)
        print 'compare '
        print lines 
        #mt_file = filename.replace('pe','mt')
        #print 'and '+mt_file 
        MT_connectives = MT_connectives_per_doc[doc]
        print MT_connectives_per_doc[doc] 
        for line, PE_connectives in lines.items():
            """ 17 Expansion:in fact Comparison:while """
            lineno = int(line) #.strip()[0])
            #connectives = line.strip()[1:]
            print 'doc %s lineno in pe: %s' %(doc,lineno)
            print PE_connectives
            deleted_MT_connectives = []
            inserted_PE_connectives = []
            #deleted_MT_connectives =[connective for connective in MT_connectives[lineno] if connective not in line] 
#            deleted_MT_connectives =[connective for connective in MT_connectives_per_doc[doc][lineno] if connective not in line]
            for connective in MT_connectives_per_doc[doc][line]:
                
                if connective not in PE_connectives:
                    deleted_MT_connectives.append(connective)
            #inserted_PE_connectives =[connective for connective in PE_connectives if connective not in MT_connectives_per_doc[doc][lineno]]
                
            for connective in PE_connectives:
                print 'checking %s against' %connective
                print MT_connectives_per_doc[doc][line]
                if connective not in MT_connectives_per_doc[doc][line]:
                    inserted_PE_connectives.append(connective)
            print 'deleted_MT_connectives: inserted_PE_connectives'
            print deleted_MT_connectives
            print inserted_PE_connectives
            if deleted_MT_connectives or inserted_PE_connectives:
                #if lineno > 0:
                #    lineno+1
                errors_per_doc[doc][lineno]= {inserted_in_PE: inserted_PE_connectives,  removed_in_PE: deleted_MT_connectives}
                
        #ones that have been deleted in the post edit, to be added back in
        for line, MT_connectives in MT_connectives_per_doc[doc].items(): 
            #items = MT_connectives[line]
            #lineno = line.strip()[0]
            found = False
            #for pe_line , PE_connectives in PE_connectives_per_doc[doc][line]:
            if not PE_connectives_per_doc[doc][line]:
                #errors_per_doc[doc][line] =  MT_connectives
                 print 'deleted MT lines:'
                 print MT_connectives
        #errors_per_doc[doc][lineno] = [line for line in in MT_connectives_per_doc[doc]  if line not in PE_connectives_per_doc[doc][lineno] ] 
                 errors_per_doc[doc][int(line)] = {inserted_in_PE: [],removed_in_PE: MT_connectives}
    print errors_per_doc
    if not os.path.exists(output): 
        os.makedirs(output)
    #with open(os.path.join(output+'connective_errors'), 'w') as output: 
    f = open( output+'_json', 'w')
    f.write( json.dumps(errors_per_doc ) )
    #f = open( output+'_t'+threshold+'_json', 'w')
    #with open(output, 'w') as output:
        #output.write(errors)
        #print 'ERRORS:'
        #print errors_missing
        #print errors_sense
        #errors = errors_missing.copy()
        #errors.update(errors_sense)
    """       for doc,lines in errors_per_doc.items():
    #for k,values in errors.items():
        output.write(str(doc)+' \t')
        #for v in values:
        #    output.write(v+' ')
        for line, connectives in lines.items():
        for line in lines:
            output.write(line)
        output.write('\n')
        """
        
    #print errors_per_doc
    
def extract_connectives(outputfile, connectives_per_doc):
#def extract_connectives(directory, connectives_per_doc):   
    #files = [name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name)) ]
    #for filename in files:
     
     allconnectives = yaml.safe_load(open(outputfile+'_json'))
     logging.info(outputfile)
     
        #doc = map(int, re.findall("\d+",filename))[0]
#     connectives = defaultdict(list)
     for doc, lines in allconnectives.items():
        print 'DOCID=%s' %doc
        for line, connectivelist in lines.items():
            connectives = defaultdict(list)
        #with open(os.path.join(directory, filename)) as fi:
            prev = ''
            #for line in fi:
            for connective in connectivelist:
                #items = line.split()
                #for item in items:
                #line_no = items[0]
                line_no = int(line)
                #item = items[1]
                #tokens = item.split('#')
                tokens = connective.split('#')
                print 'line='+line+' dc= '+tokens[0]+' sense='+tokens[2]
                if tokens[1] == prev:
                    print 'is shared: '#+ connectives[line_no][tokens[2]]+tokens[0]
                    temp = connectives[line_no][-1]
                    print 'was '+temp
                    print 'now='+temp+' '+tokens[0]
                    connectives[line_no][-1] = temp+' '+tokens[0]
                    #connectives[line_no][tokens[2]] = connectives[line_no][tokens[2]]+tokens[0]
                else:
                    #connectives[line_no].append(tokens[2]+':'+tokens[0])
                    connectives[line_no].append(tokens[0])#+':'+tokens[0])
                prev = tokens[1]
                
            print connectives
            connectives_per_doc[doc] = connectives
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