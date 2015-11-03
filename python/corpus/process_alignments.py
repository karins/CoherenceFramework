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



def read_alignments(istream, threshold, output):
    """ format of file: 1-0 2-1 3-2 4-3 5-4 6-5 representing MT:PE for each word of each line in doc """
    #map: line -> error_type
    errors = defaultdict(list)
    MT = [[]]#np.zeros(3, )
    PE = [[]]#np.zeros(3, )
    
    """ store as 2 vectors representing MT alignments and PE alignments 
        log structural errors as reorderings exceeding magnitude of threshold variable
    """
    line_no = 0
    lines = istream.readlines()
    MT = [0 for i in range(len(lines))]
    PE = [0 for i in range(len(lines))]
    for line in lines:
        
        items = line.split()
        print 'line_no='+str(line_no) 
        num_items =len(items)
        print 'num_items='+str(num_items)
        
        MT[line_no] = [0 for i in range(num_items)]
        PE[line_no] = [0 for i in range(num_items)]
        #print MT
        
        #print PE
        prev_state = r2i.get('NONE')
        for i in range(num_items):
            print items[i]
            #num = items[i].split('-')
            num = [int(n) for n in items[i].split('-')]
            MT[line_no][i] = num[0]
            PE[line_no][i] = num[1]
            if num[0] !=  num[1]:
                
                """CURRENTLY THIS ONLY LOGS ERRORS WHERE EDIT DISTANCE EXCEEDS THRESHOLD EG DIFFERENCE OF MORE THAN 4 IN ALIGNMENTS"""
                if num[0] > num[1]:
                    if prev_state == r2i.get('DEL'):
                        print "delete"
                        state = r2i.get('DEL')
                if num[0] < num[1]:
                    print "insert"
                    state = r2i.get('INS')
            line_number = line_no+1#start from 1 to keep in line with alignments..
            if num[0] >  num[1] and ((num[0] - num[1]) > int(threshold)):
                print line.rstrip('\n\r ')
                #errors[line_number].append(line.rstrip('\n\r '))
                errors[line_number] =[line.rstrip('\n\r ')]
            elif num[0] < num[1] and (num[1] - num[0] > threshold):
                line.rstrip('\n\r ')
                #errors[line_number].append(line.rstrip('\n\r '))
                errors[line_number] =[line.rstrip('\n\r ')]
        line_no +=1
    #print MT
    print "-- "
    #print PE
    print 'Potential structural errors:'+str(len(errors))
    #print errors
    for k,v in errors.items():
        print '%s : %s' %(k,v)
    print 'Potential structural errors:'+str(len(errors))  
    f = open( output+'_t'+threshold+'_json', 'w')
    f.write( json.dumps(errors) )
    
    return PE    

#def log_errors(line, prev_state, MT, PE):
  #  if prev_state == 
    
def analyse():
    """ Determine which errors are potentially discourse-related..."""
    
        
def main(args):
    """load data and compute the coherence"""
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

