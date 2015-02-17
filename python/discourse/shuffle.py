'''

Utility script to shuffle lines within documents. These documents can be concatenated within a
larger input text file, but must be of the doctext format used elsewhere in this codebase.
(see readme) 

Created on 11 Feb 2015

@author: Karin
'''
import sys
import random
import argparse
import traceback
import logging
from discourse.doctext import iterdoctext, writedoctext


def main(args):
    """ Extract documents and shuffle sentences within each document """
    try:
        fi = open(args.directory, 'r')
        with open('{0}.shuffled'.format(args.directory), 'w') as fo:
            for lines, attributes in iterdoctext(fi):
                random.shuffle(lines)
                logging.debug('shuffled: %s', lines)
                writedoctext(fo, lines, **attributes)
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