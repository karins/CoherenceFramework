'''
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
    """ Extract entities and construct grid """
    try:
        with open(args.directory, 'rb' ) as fi:
            with open(args.directory+'_shuffled', 'w') as fo:
                for lines, attributes in iterdoctext(fi):
                    shuffled_doc = random.shuffle(lines) 
                    writedoctext(fo, shuffled_doc, **attributes)

                logging.info('done: %s', args.directory)
    except:
        raise Exception(''.join(traceback.format_exception(*sys.exc_info())))       


def parse_args():
    """parse command line arguments"""
    
    parser = argparse.ArgumentParser(description='implementation of Entity grid using ptb trees as input',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    #parser.add_argument('directory', 
    #       type=str,
            #argparse.FileType('rb'),
    #        help="path for input file")
    parser.add_argument('directory', nargs='?', 
            type=argparse.FileType('r'), default=open(sys.argv[1], 'r'),
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