'''
Created on 18 Nov 2015

@author: Karin
'''
from discourse import command

from corpus.extract_lexical_cohesion_errors import extract_nouns, derive_errors
from corpus.extract_connectives import extract_connectives
from corpus.compare_connectives import extract_connective_errors as connective_errors
from corpus.inject_errors import inject_errors 
from process_alignments import read_alignments
import os, argparse,logging, sys

error_path =  os.sep+'errors'
injected_corpus_path =  os.sep+ 'artificial_corpus'
error_type_all = 0
error_type_lexical = 1
error_type_connectives = 2
error_type_structural = 3

def make_workspace(workspace, corpus):
    if not os.path.exists(workspace + error_path):
        os.makedirs(workspace + error_path)
    if not os.path.exists(workspace + injected_corpus_path):
        os.makedirs(workspace + injected_corpus_path)
    #if not os.path.exists( output_directory):
     #   os.makedirs( output_directory)
    
    return workspace + error_path , workspace + injected_corpus_path+os.sep+corpus

def main(args):

        # pipeline
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
    #if not os.path.exists(args.workspace +os.sep+ 'MT_PE_hter_alignments'):
    #if not os.path.isfile(args.alignments):
    #if not os.path.exists(args.alignments):
    if not args.alignments:
        raise Exception("MT_PE_hter_alignments file %s is not present at %s " %(args.alignments,args.workspace))

    #process_alignments(  ,error_path+os.sep+'lexical_errors')
    threshold = args.threshold
    structural_errors_file, alignments_file = read_alignments(args.alignments,  errors+os.sep+'structural_errors',threshold=4)
    structural_errors = 'structural_errors_t'+str(threshold)
    #logging("error type for corpus= %s" %(args.error_type))
    logging.debug( "error type="+str(args.error_type))
    #print int(args.error_type) == error_type_lexical
    
    if int(args.error_type) == error_type_lexical:
        logging.debug( "lexical")
        PE_nouns_per_doc = extract_nouns(args.workspace+os.sep+'tagged'+os.sep+'pe', args.output)
        MT_nouns_per_doc = extract_nouns(args.workspace+os.sep+'tagged'+os.sep+'mt',args.output)
        derive_errors(PE_nouns_per_doc, MT_nouns_per_doc, errors+os.sep+'lexical_errors')
    
    if int(args.error_type) == error_type_connectives:
        extract_connectives(args.workspace+os.sep+'tagged'+os.sep+'pe', errors,'connectives.pe')
        extract_connectives(args.workspace+os.sep+'tagged'+os.sep+'mt', errors,'connectives.mt')
        connective_errors(errors+os.sep+'connectives.pe',errors+os.sep+'connectives.mt' ,errors+os.sep+'connective_errors')        
    
    logging.debug( "INJECTING ERRORS")
    """inject_errors(pe, mt, lexical_errors, alignments, structural, discourse_errors, output):"""
    #inject_errors(get_doctext_dir(args,'pe'), get_doctext_dir(args,'mt'), errors, structural_errors, alignments_dict, args.error_type, args.output)
    inject_errors(get_doctext_dir(args,'pe'), get_doctext_dir(args,'mt'), errors, structural_errors_file, alignments_file, args.error_type, output)

def get_doctext_dir(args, subdir):
    return args.workspace +os.sep+ 'doctext'+os.sep+subdir+os.sep+args.corpus+'_'+subdir+'.doctext'

@command('pipeline', 'corpus')
def argparser(parser=None, func=main):
#def parse_args():
    """parse command line arguments"""

    parser = argparse.ArgumentParser(prog='pipeline',description='Pipeline',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--workspace', 
            type=str, 
            help='where everything happens')
    parser.add_argument('--alignments', nargs='?', 
            type=argparse.FileType('r'), default=sys.stdin,
            help='alignments for MT-PE hter edits, doc separated')
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
    args = parser.parse_args()
    
    logging.basicConfig(
            level=(logging.DEBUG if args.verbose else logging.INFO), 
            format='%(levelname)s %(message)s')
    return args

if __name__ == '__main__':
    main(argparser())
    #main(argparser().parse_args())