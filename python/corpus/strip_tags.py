'''
Created on 2 Dec 2015

@author: Karin
'''


from bs4 import 
from BeautifulSoup import BeautifulSoup
import argparse

def main(args):
soup = BeautifulSoup(open(file 'r'))


source = soup.source
source.getText()

    logging.debug('file %s'%args.input)
    idx = 0
    with open(args.output+'_untagged', 'w') as outputfile:
        for line in open(args.input, 'r'):
            logging.debug(line)        
            if "<doc" in line :
                outputfile.write(line)
                        

def argparser():
    """parse command line arguments"""
    
    parser = argparse.ArgumentParser(description='Remove the leading alphanumeric from each line.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('input', nargs='?',
                        type=str, 
                        help='input file')
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

