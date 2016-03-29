'''

Takes as input a document with <doc> tags and outputs in doctext format.

Created on 19 Nov 2015

@author: Karin
'''
import argparse, logging



def main(args):
    
    logging.debug('file %s'%args.input)
    idx = 0
    with open(args.output+'.doctext', 'w') as outputfile:
        for line in open(args.input, 'r'):
            logging.debug(line)        
            if "<doc" in line :
                outputfile.write('# doc src=LIG id='+str(idx)+'\n')
                idx+=1
            elif "</doc>" in line:
                outputfile.write('\n')
            elif "<src"not in line:
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