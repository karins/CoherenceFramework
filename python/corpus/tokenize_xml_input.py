# -*- coding: utf-8 -*-
"""
Created on Mon Feb 29 12:17:20 2016

@author: karin
"""
import nltk.tokenize

def main():

    print('file %s'%args.input)
    idx = 0
    with open('tokenised.'+args.output, 'w') as outputfile:
        
        for line in open(args.input, 'r'):
            #logging.debug(line)        
            if "<>" in line :
                tokenized_content = nltk.tokenize(content)
                outputfile.write("%s%s%s\n" %(start_tag, tokenized_content, end_tag))

return sentence;
    
def argparser():
    """parse command line arguments"""
    
    parser = argparse.ArgumentParser(description='tokenize xml',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('input', nargs='?',
                        type=str, 
                        help='input file')
    
    args = parser.parse_args()
    
    logging.basicConfig(
            level=(logging.DEBUG if args.verbose else logging.INFO), 
            format='%(levelname)s %(message)s')
    return args


if __name__ == '__main__':
    main(argparser())    