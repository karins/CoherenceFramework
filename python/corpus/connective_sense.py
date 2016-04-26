# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 07:59:21 2016

@author: karin
"""

'''
Takes as input a list of connectives, as output by discourse tagger (Pitler and Nenkova, http://www.cis.upenn.edu/~nlp/software/discourse.html)
 and previously extracted by script (analyse_connectives.py)

Created on 6 Oct 2015

@author: Karin
'''  
#! /usr/bin/python
#-*-coding:utf-8-*-
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
    
    #MT_connectives_per_doc = defaultdict(list)
    #PE_connectives_per_doc  = defaultdict(list)
    
    
#def  extract_connective_errors(input_directory_pe, input_directory_mt, output):    
    #MT_connectives_per_doc = defaultdict(list)
    #PE_connectives_per_doc  = defaultdict(list)
    
    PE_connectives_per_doc = extract_connectives(args.pe,  defaultdict(list))
    MT_connectives_per_doc = extract_connectives(args.mt,  defaultdict(list))
    compare_sense(PE_connectives_per_doc, MT_connectives_per_doc, args.output)
    
def compare_sense(PE_connectives_per_doc, MT_connectives_per_doc, output):
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
    5 Temporal:when
    """ 
    logging.debug('deriving connective errors...')
    errors_per_doc = defaultdict(list)
    #errors_missing = defaultdict(list)
    #errors_sense = defaultdict(list)
    #errors_deleted = defaultdict(list)
    """presume that the errors for PE_files will include all docs under consideration - check if that is case"""
    for doc,lines in PE_connectives_per_doc.items():
        #PE_connectives = lines
        logging.debug('DOCID=%s' %doc)
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
                print 'comparing %s', connective
                print 'to %s ',[con for con in PE_connectives]
                if connective.lower() not in [con.lower() for con in PE_connectives]:#PE_connectives:
                    #deleted_MT_connectives.append(connective)
                    deleted_MT_connectives.append(connective+':'+MT_connectives_per_doc[doc][line][connective])
            #inserted_PE_connectives =[connective for connective in PE_connectives if connective not in MT_connectives_per_doc[doc][lineno]]
                
            for connective in PE_connectives:
                print 'checking %s against' %connective
                print MT_connectives_per_doc[doc][line]
                #if connective not in MT_connectives_per_doc[doc][line]:
                if connective.lower() not in [mt.lower for mt in MT_connectives_per_doc[doc][line]]:#MT_connectives_per_doc[doc][line]:
                    #inserted_PE_connectives.append(connective)
                    inserted_PE_connectives.append(connective+':'+MT_connectives_per_doc[doc][line][connective])
            print 'deleted_MT_connectives: inserted_PE_connectives'
            print deleted_MT_connectives
            print inserted_PE_connectives
            if deleted_MT_connectives or inserted_PE_connectives:
                #if lineno > 0:
                #    lineno+1
                errors_per_doc[doc][lineno]= {inserted_in_PE: inserted_PE_connectives,  removed_in_PE: deleted_MT_connectives}
        """        
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
                 """  
    print errors_per_doc
    #if not os.path.exists(output): 
    #    os.makedirs(output)
    #with open(os.path.join(output+'connective_errors'), 'w') as output: 
    f = open( output+'_json', 'w')
    f.write( json.dumps(errors_per_doc ) )
    #f = open( output+'_t'+threshold+'_json', 'w')
    with open(output+'_anal', 'w') as output_anal:
        with open(output+'_txt', 'w') as output:
            for doc,lines in errors_per_doc.items():
        #for k,values in errors.items():
                output.write('doc='+str(doc)+' \t')
                for line, connective_lists in lines.items():
                    #print(line)
                    if connective_lists:
                        output.write('\n\t \t line:'+str(line))
                    #errors_per_doc[doc][lineno]= {inserted_in_PE                        
                    
                    if connective_lists[removed_in_PE]:
                        output.write('\n\t\t\t\t removed:')# +str(removed_in_PE))
                        #if connective_lists[removed_in_PE]:
                        output_anal.write('\n'+str(doc)+'\t \t line:'+str(line)+' replaced ')
                    
                    for connective in connective_lists[removed_in_PE]:
                        #for connective in connectives:
                        output.write('\t' +connective+'\t')
                        output_anal.write('\t' +connective+'\t'+connective_lists[removed_in_PE][connective])
                        
                    if connective_lists[inserted_in_PE]:
                        if connective_lists[removed_in_PE]:
                            output_anal.write('with \t')
                            for connective in connective_lists[inserted_in_PE]:
                                output_anal.write('\t' +connective+'\t')
                        output.write('\t inserted:')# +str(inserted_in_PE))
                    for connective in connective_lists[inserted_in_PE]:
                    #for ind,connectives in connective_lists.items():
                        #print 'type:%s', ind
                        output.write('\t' +connective+'\t')
                        
                output.write('\n')
                
    #print errors_per_doc
    
def extract_connectives(outputfile, connectives_per_doc):
#def extract_connectives(directory, connectives_per_doc):   
    #files = [name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name)) ]
    #for filename in files:
    
    allconnectives = yaml.safe_load(open(outputfile+'_json'))
    logging.info('extracting connectives from: '+outputfile)
     
        #doc = map(int, re.findall("\d+",filename))[0]
#     connectives = defaultdict(list)
    for doc, lines in allconnectives.items():
        print 'DOCID=%s' %doc
        docid = int(doc)
        connectives = defaultdict(list)
        connective_sense = defaultdict(list)
        for line, connectivelist in lines.items():
            #connectives = defaultdict(list)
            line_no = int(line)
            connectives[line_no]=[]  
            connective_sense[line_no]= {}#defaultdict()  
        #with open(os.path.join(directory, filename)) as fi:
            prev = ''
            #for line in fi:
            for connective in connectivelist:
                #items = line.split()
                #for item in items:
                #line_no = items[0]
                
                #item = items[1]
                #tokens = item.split('#')
                tokens = connective.split('#')
                print 'line='+line+' dc= '+tokens[0]+' sense='+tokens[2]
                if tokens[1] == prev:
                    print 'is shared: '#+ connectives[line_no][tokens[2]]+tokens[0]
                    temp = connectives[line_no][-1]
                    print 'was '+temp
                    print 'now='+temp+' '+tokens[0]
                    #connectives[line_no][-1] = temp+' '+tokens[0]
                    #connectives[line_no][-1] = {}#temp+' '+tokens[0]
                    connectives[line_no][-1] = temp+' '+tokens[0]                    
                    #connective_sense[line_no][temp+' '+tokens[0]] = tokens[2]
                    #connective_sense[line_no][temp] = None #+' '+tokens[0]] = tokens[2]
                    connective_sense[line_no][temp+' '+tokens[0]] = tokens[2]
                    #tidyup prev
                    connective_sense[line_no].pop(temp)
                    #connectives[line_no][tokens[2]] = connectives[line_no][tokens[2]]+tokens[0]
                else:
                    #connectives[line_no].append(tokens[2]+':'+tokens[0])
                    connectives[line_no].append(tokens[0])
                    connective_sense[line_no][tokens[0]]=tokens[2]
                prev = tokens[1]
                
            
            #connectives_per_doc[docid] = connectives
            connectives_per_doc[docid] = connective_sense
    print 'from extract_connectives, returning:'
    print connectives_per_doc
    return connectives_per_doc

def argparser():
    """parse command line arguments"""
    
    parser = argparse.ArgumentParser(description='Remove the leading alphanumeric from each line.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('--pe', nargs='?',
                        type=str, 
                        help='input directory')
    
    parser.add_argument('--mt', nargs='?',
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