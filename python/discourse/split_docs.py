'''
Created on 20 Mar 2015

@author: Karin
'''
import sys
import argparse
import traceback
import logging
from discourse.doctext import iterdoctext


def main(args):
    """ Extract documents and output each document to separate file"""
    try:
        fi = open(args.directory, 'r')
        idx = 0
        for lines, attributes in iterdoctext(fi):
            with open('{0}.{1}'.format(args.directory, idx), 'w') as fo:
            
                logging.debug('done: %s', args.directory)
                logging.debug('doc: %s', lines)
                for line in lines:
                    print >> fo, line
                idx+=1
            logging.info('done: %s', args.directory)
    except:
        raise Exception(''.join(traceback.format_exception(*sys.exc_info())))       


    
def parse_args():
    """parse command line arguments"""
    
    parser = argparse.ArgumentParser(description='shuffles lines within a document',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('directory', nargs='?',
                        type=str, 
                        help='input corpus in doctext format')
    
    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')
    
    args = parser.parse_args()
    
    logging.basicConfig(
            level=(logging.DEBUG if args.verbose else logging.INFO), 
            format='%(levelname)s %(message)s')
    return args
    
if __name__ == '__main__':
     main(parse_args())    