#-*-coding:utf-8-*-
'''
Filters corpora from European Parliament to extract specific language and create directional corpus.
Stores as source. Ideally create parallel target. This is done by matching extracted source strings.
Created on 30 Mar 2015

@author: Karin Sim
'''
import argparse
import collections
import logging
import os
import re


def main(args):
    """
    input: directory to search. Presumes this is text in desired source language.
    predetermined language abbreviation, to specify which language to extract [eg 'FI' will en sure matches for LANGUAGE="FI"]
    format of file will include:
    <SPEAKER ID=142 LANGUAGE="SV"  NAME="Sjöstedt">
    concatenates all data until next SPEAKER tag.
    File is saved in relevant directory (eg europarl\DE_to_EN\de_source where language filtered on is German). 
    Output directory is a parameter determined by user (directory will be created if doesnt exist). 
"""
    output = []
    LANGUAGE = "LANGUAGE"
    CHAPTER = "CHAPTER"
    SPEAKER = "<SPEAKER"
    TAG = "<"
    
    files = [name for name in os.listdir(args.directory) if os.path.isfile(os.path.join(args.directory, name)) ]
    
    for filename in files:
        with open(os.path.join(args.directory, filename)) as fi:
            
            store = False
            #check for language match:
            for line in fi:
                if line.startswith(SPEAKER):
                    store = False
                    tuples =line.split()
                    
                    for tuple in tuples:
                        if tuple.startswith(LANGUAGE) and args.language in tuple:
                            logging.debug('language '+ tuple)
                            store = True
                            output.append(line)
                            
                #concatenate all the speaker's output
                elif store and not line.startswith(CHAPTER):
                    #strip tags
                    if not line.startswith(TAG):
                        output.append(line)
                elif line.startswith(CHAPTER):
                    store = False
            logging.debug(' filename: '+ filename) 
            if not os.path.exists(args.output):
                os.makedirs(args.output)
            with open(os.path.join(args.output, filename), 'w') as fo:
                for line in output:
                    fo.write(line)


def parse_args():
    """parse command line arguments"""
    
    parser = argparse.ArgumentParser(description='extracts and combines system scores, each representing a document',
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