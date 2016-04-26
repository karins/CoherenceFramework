# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 12:52:59 2016

@author: karin
"""

START_BRACKET ="["
END_BRACKET ="]_"
SEGMENT_PATTERN="(d+/[d+\-d+])"
NUMBER_PATTERN = re.compile("\d+")

def main(args):
    """ Iterate through all *.rel files and extract the rhetorical relations.
    Store relation instances with the segments in which they occur.
    input:  elaboration(4/[6-88])
            narration(7/15)
    track: elaboration  -> plaintext of 7 and 15
                        -> ngrams 
    in parallel: extract from ptb file:
        POS tags
        root to cue path
        parent 
        siblings
    as byproduct, extract plaintext, ie without brackets
    
    /home/karin/annodis/annotations_expert/texte/A  and ../../B: all .rel and .seg files
    /home/karin/annodis/annotations_expert/texte/A  and ../../B: all .ac and .aa files where ac is plaintext
    """

    """ iterate rel files: """
    files = [name for name in os.listdir(args.directory) if os.path.isfile(os.path.join(args.directory, name)) ]
    for filename in files:
        with open(os.path.join(args.directory, filename)) as fi:
            output = []
            for line in fi:
                idx = line '('
                relation= line[0:idx]
                seg_to_find = re.search(NUMBER_PATTERN,line)
                if seg_to_find:
                    logging.debug(['seg_to_find'+[seg for seg in seg_to_find ])
        #logging.debug('seg_to_find'+seg_to_find.group(0)
            """find .seg file match"""                
                """
                for tuple in line.split('(',')') :
                    if tuple.startswith(ID):
                        id_to_find = re.search(NUMBER_PATTERN,tuple)
                        if id_to_find:
                            logging.debug('id_to_find'+id_to_find.group(0))
                            logging.debug('line ='+line )
                            name_to_match = re.search(NAME_PATTERN, line)
                            if name_to_match:
                                logging.debug('name_to_match: '+name_to_match.group(1))
"""
            
    
    for filename in files:
        with open(os.path.join(args.directory, filename)) as fi:
            output = []
            #extract_segment(args, fi, output, LANGUAGE, None)
            for line in fi:
                if line.startswith(START_BRACKET):
                    
            logging.debug(' filename: '+ filename) 
            if output:
                if not os.path.exists(args.output):
                    os.makedirs(args.output)
                with open(os.path.join(args.output, filename), 'w') as fo:
                    for line in output:
                        fo.write(line)



""" Remove leading and tailing square brackets (segmentation details)
    input: [﻿word]_1 """



def parse_args():
    """parse command line arguments"""
    
    parser = argparse.ArgumentParser(description='extracts and filters according to language parameter',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('directory', nargs='?',
                        type=str, 
                        help='input corpus')
    
    parser.add_argument('--language', nargs='?',
                        type=str, 
                        help='predetermined language abbreviation, to specify which language to extract')
    
    
    parser.add_argument('--output', nargs='?',
                        type=str, 
                        help='output file for combined extracts')
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