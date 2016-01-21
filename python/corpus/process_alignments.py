'''

Processes MT-PE hter alignments to extract ones of interest for discourse.

Created on 2 Oct 2015

@author: Karin
'''
import argparse, sys
import logging, itertools
import numpy as np
from collections import defaultdict
import json

r2i = {'SHI':4,'INS': 3, 'DEL': 2, 'SUB': 1, 'NONE': 0}
i2r = {v: k for k, v in r2i.iteritems()}

def get_doc_alignments(istream):
    
    """ format of file: 1-0 2-1 3-2 4-3 5-4 6-5 representing MT:PE for each word of each line in doc """
    doc_alignments = defaultdict(list)
    
    MT = [[]]
    PE = [[]]
    doc_tag='<doc'
    end_tag='</'
    start_tag = '<srcset'
    """ store as 2 vectors representing MT alignments and PE alignments 
        log structural errors as reorderings exceeding magnitude of threshold variable
    """
    line_no = 0
    docid=0
    lines = istream.readlines()
    MT = [0 for i in range(len(lines))]
    PE = [0 for i in range(len(lines))]
    for line in lines:
        if doc_tag in line:
            #extract id from <doc id=1>
            idx = line.find('=')
            docid= line[idx+1:-2]
            logging.debug( 'DOCTAG: %s' %(docid))
            line_no = -1
            doc_alignments[docid] = defaultdict(list)
        elif end_tag not in line and start_tag not in line:
            line_number = line_no+1
            items = line.split()
            doc_alignments[docid][line_number] = line
            return doc_alignments            

def read_alignments(istream,  output,threshold):
    """ format of file: 1-0 2-1 3-2 4-3 5-4 6-5 representing MT:PE for each word of each line in doc """
    logging.debug('using threshold=%s',threshold)
    doc_alignments = defaultdict(list)
    errors = defaultdict(list)
    doc_errors = defaultdict(list)
    
    MT = [[]]
    PE = [[]]
    doc_tag='<doc'
    end_tag='</'
    start_tag = '<srcset'
    """ store as 2 vectors representing MT alignments and PE alignments 
        log structural errors as reorderings exceeding magnitude of threshold variable
    """
    line_no = 0
    docid=0
    lines = istream.readlines()
    MT = [0 for i in range(len(lines))]
    PE = [0 for i in range(len(lines))]
    for line in lines:
        if doc_tag in line:
            
            idx = line.find('=')
            docid= line[idx+1:-2]
            logging.debug( 'DOCTAG: %s' %(docid))
            line_no = -1
            doc_errors[docid] = defaultdict(list)
            doc_alignments[docid] = defaultdict(list)
        elif end_tag not in line and start_tag not in line:
            
            items = line.split()
            logging.debug( 'line_no='+str(line_no)) 
            num_items =len(items)
            
            
            MT[line_no] = [0 for i in range(num_items)]
            PE[line_no] = [0 for i in range(num_items)]
            """ start from 1 to keep in line with alignments.."""
            line_number = line_no+1 
            doc_alignments[docid][line_number] = line
            
            prev_state = r2i.get('NONE')
            for i in range(num_items):
                #print items[i]
                #num = items[i].split('-')
                num = [int(n) for n in items[i].split('-')]
                MT[line_no][i] = num[0]
                PE[line_no][i] = num[1]
                """if num[0] !=  num[1]:
                    
                    #CURRENTLY THIS ONLY LOGS ERRORS WHERE EDIT DISTANCE EXCEEDS THRESHOLD EG DIFFERENCE OF MORE THAN 4 IN ALIGNMENTS
                    
                    if num[0] > num[1]:
                        if prev_state == r2i.get('DEL'):
                            #print "delete"
                            state = r2i.get('DEL')
                    if num[0] < num[1]:
                        #print "insert"
                        state = r2i.get('INS')
                        """
                #line_number = line_no+1#start from 1 to keep in line with alignments..
                if num[0] >  num[1] and ((num[0] - num[1]) > int(threshold)):
                    logging.debug( line.rstrip('\n\r '))
                    #errors[line_number].append(line.rstrip('\n\r '))
                    errors[line_number] =[line.rstrip('\n\r ')]
                    doc_errors[docid][line_number] =[line.rstrip('\n\r ')]
                    break
                elif num[0] < num[1] and (num[1] - num[0] > int(threshold)):
                    logging.debug(line.rstrip('\n\r '))
                    errors[line_number].append(line.rstrip('\n\r '))
                    doc_errors[docid][line_number] =[line.rstrip('\n\r ')]
                    break
            line_no +=1
    #print MT
    #print "-- "
    #print PE
    logging.debug( 'Potential structural errors in '+str(len(doc_errors))+' docs')
    
    #print errors
    num = 0
    for docid, lines in doc_errors.items():
        for k,v in lines.items():
            logging.debug( '%s -> %s : %s' %(docid,k,v))
            num += len(lines)
       
    f = open( output+'_t'+str(threshold)+'_json', 'w')
    f.write( json.dumps(doc_errors) )
    #print 'doc_alignments'
    #print doc_alignments
    f = open( output+'_doc_alignments_json', 'w')
    f.write( json.dumps(doc_alignments) )
    logging.debug( 'Potential structural errors:%s',num)
    return output+'_t'+str(threshold)+'_json',output+'_doc_alignments_json'    

#def log_errors(line, prev_state, MT, PE):
  #  if prev_state == 
    
def analyse():
    """ Determine which errors are potentially discourse-related..."""
    
        
def main(args):
    """load data and read in alignments"""
    logging.basicConfig(
            level=(logging.DEBUG if args.verbose else logging.INFO), 
            format='%(levelname)s %(message)s')
    alignments = read_alignments(args.input, args.threshold, args.output)
    analyse()
    logging.info('Read in %d rows of alignments', len(alignments))

def argparser(parser=None, func=main):
    """parse command line arguments"""
    
    if parser is None:
        parser = argparse.ArgumentParser(prog='process_alignments')

    parser.description = 'Process alignments to extract PE error information '
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    
    parser.add_argument('input', nargs='?', 
            type=argparse.FileType('r'), default=sys.stdin,
            help='input file containing alignments')
    parser.add_argument('--output', nargs='?', 
            type=str, default=sys.stdout,
            help='output error analysis')
    parser.add_argument('--threshold', nargs='?', 
            default=4, help='threshold for reordering error analysis')
    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')
   
    if func is not None:
        parser.set_defaults(func=func)
     
    return parser
    
if __name__ == '__main__':
     main(argparser().parse_args())

