'''
Main entry point for the corpus codebase. Calls the individual scripts in correct order with the various
accummulated parameters.

Created on 18 Nov 2015

@author: Karin
'''
#! /usr/bin/python
#-*-coding:utf-8-*-
from discourse import command

from corpus.extract_lexical_cohesion_errors import extract_nouns, derive_errors
from corpus.extract_connectives import extract_connectives
from corpus.compare_connectives import extract_connective_errors as connective_errors
from corpus.inject_errors import inject_errors 
from corpus.process_alignments import read_alignments
import os, argparse,logging, sys
from corpus.inject_errors import error_type_all, error_type_lexical, error_type_structural, error_type_connectives

error_path =  os.sep+'errors'
injected_corpus_path =  os.sep+ 'artificial_corpus'


def make_workspace(workspace, corpus):
    if not os.path.exists(workspace + error_path):
        os.makedirs(workspace + error_path)
    if not os.path.exists(workspace + injected_corpus_path):
        os.makedirs(workspace + injected_corpus_path)
    if not os.path.exists(workspace+os.sep+'temp'):
        os.makedirs(workspace+os.sep+'temp')
    return workspace + error_path , workspace + injected_corpus_path+os.sep+corpus

def main(args):
        
    """ presumes that files are in format below, ie doctext, have been parsed, also tagged.
    For doctext, see discotools in adjacent directory.
    For parsing, present as ptb files, utility code in adjacent directory.
    For tagger, pass ptb files to Pitler Nenkova tagger- which will ensure connectives are flagged.
    If these directories are not as expected, error will be thrown.
    $workspace$\parsed
    $workspace$\tagged
    $workspace$\doctext
    The following directories will be created:
    $workspace$\errors - for storing the error files derived for each error type
    $workspace$\artificial_corpus - for storing the corpus which has artificially injected discourse errors of type:
            -lexical, 
            -clausal, 
            -connective
    """
    if not os.path.exists(args.workspace):
        raise Exception("workspace path does not exist")  
    """ paths for errors and newly created corpus: """ 
    errors, output = make_workspace(args.workspace, args.corpus)
    
    if not os.path.exists(args.workspace +os.sep+ 'tagged'):
        raise Exception("tagged files are not present at "+args.workspace+os.sep+'tagged')
    if not os.path.exists(args.workspace +os.sep+ 'doctext'):
        raise Exception("doctext source files are not present at "+args.workspace+os.sep+'doctext')
    
    if not args.alignments:
        raise Exception("MT_PE_hter_alignments file %s is not present at %s " %(args.alignments,args.workspace))

    #threshold = args.threshold
    structural_errors_file, alignments_file = read_alignments(args.alignments,  errors+os.sep+'structural_errors',int(args.threshold))
    
    logging.debug( "error type="+str(args.error_type))
    
    if int(args.error_type) == error_type_lexical or int(args.error_type)== error_type_all :
        logging.debug( "deriving lexical errors..")
        PE_nouns_per_doc = extract_nouns(args.workspace+os.sep+'tagged'+os.sep+'pe', args.workspace+os.sep+'temp')
        MT_nouns_per_doc = extract_nouns(args.workspace+os.sep+'tagged'+os.sep+'mt',args.workspace+os.sep+'temp')
        derive_errors(PE_nouns_per_doc, MT_nouns_per_doc, errors+os.sep+'lexical_errors')
    
    if int(args.error_type) == error_type_connectives or int(args.error_type)== error_type_all :
        logging.debug( "deriving connective errors..")
        extract_connectives(args.workspace+os.sep+'tagged'+os.sep+'pe', errors,'connectives.pe')
        extract_connectives(args.workspace+os.sep+'tagged'+os.sep+'mt', errors,'connectives.mt')
        connective_errors(errors+os.sep+'connectives.pe',errors+os.sep+'connectives.mt' ,errors+os.sep+'connective_errors')        
    
    logging.debug( "INJECTING ERRORS...")
    """inject_errors(pe, mt, lexical_errors, alignments, structural, discourse_errors, output):"""
    inject_errors(get_doctext_dir(args,'pe'), get_doctext_dir(args,'mt'), errors, structural_errors_file, alignments_file, int(args.error_type), output)

def get_doctext_dir(args, subdir):
    return args.workspace +os.sep+ 'doctext'+os.sep+subdir+os.sep+args.corpus+'_'+subdir+'.doctext'

@command('corpus_pipeline', 'corpus')
def argparser(parser=None, func=main):

    """parse command line arguments"""

    parser = argparse.ArgumentParser(prog='corpus_pipeline',description='Corpus Pipeline',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--workspace', 
            type=str, 
            help='where everything happens')
    parser.add_argument('--alignments', nargs='?', 
            type=argparse.FileType('r'), default=sys.stdin,
            help='alignments for MT-PE hter edits, doc separated format- see script match_hter_alignments for this')
    parser.add_argument('--error_type', nargs='?',
                        type=str, 
                        help='--which type of errors to generate, 0 for all, 1 for just lexical, 2 for just connectives, 3 for just clausal')
    parser.add_argument('--corpus', nargs='?',
                        type=str, 
                        help='--name of corpus file')
    
    parser.add_argument('--output', nargs='?',
                        type=str, 
                        help='output directory')
    parser.add_argument('--threshold', nargs='?',
                        type=str, 
                        help='threshold variable controlling how much alignments can differ before registered as structural error')
    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')
    parser.add_argument('--logfile', nargs='?',
                        type=str, 
                        help='logfile directory')
    args = parser.parse_args()
    
    #logging.basicConfig(
     #       level=(logging.DEBUG if args.verbose else logging.INFO), 
      #      format='%(levelname)s %(message)s')
    logging.basicConfig(filename=args.logfile,filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
            level=(logging.DEBUG if args.verbose else logging.INFO))
    return args

if __name__ == '__main__':
    main(argparser())
    