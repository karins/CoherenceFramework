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

LANGUAGE = "LANGUAGE"
CHAPTER = "CHAPTER"
SPEAKER = "<SPEAKER"
ID = "ID"
TAG = "<"
NUMBER_PATTERN = re.compile("\d+")
    
def main(args):
    
    if args.target:
        extract_target(args)
    else:
        extract_source(args)

def extract_target(args):
    """
    find matching exerpts for the files in the 'filtered_source' directory, from those in the 'directory' list:
    this presumes that the 'filtered_source' directory has the original language source eg \..\..\europarl\FR, and the 'directory' contains the target language eg
    \..\..\europarl\EN
    NB presumes that these are the original source excerpts and 
        presumes that the param 'filtered_source' points to the original source, in desired language
        from each matched file: find the parallel excerpt via info in <SPEAKER tag
                                extract and store under \DE_to_EN\en_target or whatever
                                --target --filtered_source=C:\Users\Karin\Desktop\europarl\FI_to_EN\fi_source
    --output C:\Users\Karin\Desktop\europarl\FI_to_EN\en_target 
    """
    
    files = [name for name in os.listdir(args.directory) if os.path.isfile(os.path.join(args.directory, name)) ]
    files_to_match = [name for name in os.listdir(args.filtered_source) if os.path.isfile(os.path.join(args.filtered_source, name)) ]
    for matchingfile in files_to_match:
        with open(os.path.join(args.filtered_source, matchingfile)) as match:
            output = []
            for filename in files:
                logging.debug(filename)
                with open(os.path.join(args.directory, filename)) as fi:
                    if filename == matchingfile:
                        logging.debug( filename +' '+matchingfile)
                        #match excerpts:
                        for line in match:
                            if line.startswith(SPEAKER):
                                #extract the id and match with translation
                                for tuple in line.split() :
                                    if tuple.startswith(ID):
                                        id_to_find = re.search(NUMBER_PATTERN,tuple)
                                        if id_to_find:
                                            logging.debug('id_to_find'+id_to_find.group(0))
                                            output = extract_segment(args, fi, output, ID ,id_to_find.group(0))
        if output:
            if not os.path.exists(args.output):
                os.makedirs(args.output)
            with open(os.path.join(args.output, matchingfile ), 'w') as fo:
                for line in output:
                   fo.write(line)

    
def extract_segment(args,  fi, output, criteria, id_match ): 
    store = False
    #check for match:
    for line in fi:
        if line.startswith(SPEAKER):
            store = False
            if criteria == ID:
                matches_both_criteria(criteria, line, args, id_match)
                store = True
                output.append(line)
            else:
                for tuple in line.split():
                    if matches_criteria(criteria, tuple, args):
                        store = True
                        output.append(line)
        #concatenate all the speaker's output
        elif store and not line.startswith(CHAPTER):
            if not line.startswith(TAG): #strip tags
                output.append(line)
        elif line.startswith(CHAPTER):
            store = False
    fi.seek(0)
    return output

def matches_criteria(criteria, tuple, args):
    
    if criteria == LANGUAGE:
        return tuple.startswith(LANGUAGE) and args.language in tuple
    elif criteria == ID:
        if tuple.startswith(ID):
            id_to_match = re.search(NUMBER_PATTERN, tuple)
            if id_to_match: 
                return args == id_to_match.group(0)

def matches_both_criteria(criteria, line, args, id_match):
    languagematch = False
    idmatch = False
    for tuple in line.split():
        if tuple.startswith(LANGUAGE) and args.language in tuple:
            languagematch = True
        if tuple.startswith(ID):
            id_to_match = re.search(NUMBER_PATTERN, tuple)
            if id_to_match and id_match == id_to_match.group(0):
                idmatch = True 
    return languagematch and idmatch

def extract_source(args):
    """
    input: directory to search. Presumes this is text in desired source language.
    predetermined language abbreviation, to specify which language to extract [eg 'FI' will en sure matches for LANGUAGE="FI"]
    format of file will include:
    <SPEAKER ID=142 LANGUAGE="SV"  NAME="Sjöstedt">
    concatenates all data until next SPEAKER tag.
    File is saved in relevant directory (eg europarl\DE_to_EN\de_source where language filtered on is German). 
    Output directory is a parameter determined by user (directory will be created if doesnt exist).
    
"""
    if args.language is None:
            raise ValueError('No language parameter given')
        
    files = [name for name in os.listdir(args.directory) if os.path.isfile(os.path.join(args.directory, name)) ]
    
    for filename in files:
        with open(os.path.join(args.directory, filename)) as fi:
            output = []
            extract_segment(args, fi, output, LANGUAGE, None)
            logging.debug(' filename: '+ filename) 
            if output:
                if not os.path.exists(args.output):
                    os.makedirs(args.output)
                with open(os.path.join(args.output, filename), 'w') as fo:
                    for line in output:
                        fo.write(line)


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
    
    parser.add_argument('--target', dest='target', default ='store_false',
                        action='store_true',
                        help='flag to indicate if extraction is of target language. Defaults to false and extracts source as original language (determined by param). If set to true it will extract matching target.')
    parser.set_defaults(target=False)
    
    parser.add_argument('--filtered_source', nargs='?', 
                        type=str, 
                        help='source for matching')
    
    
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