"""
This module distributes call to ExtracGtrid from browncoherence.

ExtractGrid is a simple modification of TestGrid that allows one to use stdin as a source of sentences.

@author waziz
"""
import logging
import argparse
import sys
import os
import gzip
import traceback
import shlex
import subprocess
from time import time
from functools import partial
from multiprocessing import Pool
from sgml import TextFromSGML, MakeSGMLDocs
from ldc import parse_ldc_name_from_path, itertxtdocs, writetxtdoc
from nltk.tree import Tree


def make_workspace(workspace):
    if not os.path.exists(workspace + '/grid'):
        os.makedirs(workspace + '/grid')


def extract_grid_from_sgml(ldc_desc, args):
    """Extract grids for documents in a corpus (already parsed)"""
    n_docs = 0
    try:
        input_path = '{0}/xparse/{1}'.format(args.workspace, ldc_desc['name'])
        output_path = '{0}/grid/{1}'.format(args.workspace, ldc_desc['name'])
        logging.info('Processing %s', input_path)
        with gzip.open(input_path + '.gz', 'r') as fi:
            parser = TextFromSGML(fi.read(), text_under='doc')
            sgmler = MakeSGMLDocs(file=ldc_desc['name'])
            for doc in parser.iterdocs():
                logging.debug('document %s', doc['id'])
                cmd_line = args.ExtractGrid
                cmd_args = shlex.split(cmd_line)
                n_docs += 1
                with gzip.open(output_path + '.gz', 'wb') as fout:
                    if doc['id'] == 'XIN_ENG_20100101.0127':
                        print >> sys.stderr, doc['text']
                    #ptbs = doc['text'].split('\n')
                    #for ptb in ptbs:
                    #    print ptb
                    #    print Tree(ptb).leaves()
                    proc = subprocess.Popen(cmd_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                    (stdoutdata, stderrdata) = proc.communicate(doc['text'])
                    sgmler.add(stdoutdata, id=doc['id'])
            sgmler.writegz(output_path)
    except:
        raise Exception(''.join(traceback.format_exception(*sys.exc_info())))

                #print >> sys.stderr, ptb_str
                #print ' '.join(Tree(ptb_str).leaves())
                #print
    return n_docs


def extract_grid(ldc_desc, args):
    """Extract grids for documents in a corpus (already parsed)"""
    t0 = time()
    try:
        input_path = '{0}/xparse/{1}'.format(args.workspace, ldc_desc['name'])
        output_path = '{0}/grid/{1}'.format(args.workspace, ldc_desc['name'])
        logging.info('Processing %s', input_path)
        with gzip.open(input_path + '.gz', 'rb') as fi:
            with gzip.open(output_path + '.gz', 'wb') as fo:
                for lines, attrs in itertxtdocs(fi):
                    logging.debug('document %s', attrs['id'])
                    cmd_line = args.ExtractGrid
                    cmd_args = shlex.split(cmd_line)
                    with gzip.open(output_path + '.gz', 'wb') as fout:
                        #if doc['id'] == 'XIN_ENG_20100101.0127':
                        #    print >> sys.stderr, doc['text']
                        #ptbs = doc['text'].split('\n')
                        #for ptb in ptbs:
                        #    print ptb
                        #    print Tree(ptb).leaves()
                        proc = subprocess.Popen(cmd_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                        (stdoutdata, stderrdata) = proc.communicate('\n'.join(lines))
                        writetxtdoc(stdoutdata.split('\n'), fo, id=attrs['id']) 
    except:
        raise Exception(''.join(traceback.format_exception(*sys.exc_info())))

                #print >> sys.stderr, ptb_str
                #print ' '.join(Tree(ptb_str).leaves())
                #print
    return time() - t0
    

def parse_command_line():
    parser = argparse.ArgumentParser(description='Extracts entity grids from PTB-style parsed documents',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('workspace', type=str,
            help='where output files will be stored')
    parser.add_argument('--jobs', '-j', type=int, default=4,
            help='number of jobs')
    parser.add_argument('--ExtractGrid', '-x', type=str,
            default='/home/waziz/workspace/browncoherence/bin64/ExtractGrid',
            help="browncoherence::ExtractGrid binary")
    parser.add_argument('--dry-run', '-n', action='store_true',
            help='does not parse')
    parser.add_argument('--verbose', '-v', action='store_true',
            help='more log')
    
    parser.add_argument('--consolidate', action='store_true',
            help='more log')

    args = parser.parse_args()
    logging.basicConfig(level= logging.DEBUG if args.verbose else logging.INFO, 
            format='%(levelname)s %(message)s')
    make_workspace(args.workspace)

    return args



def main(args):

    files = [path.strip() for path in sys.stdin]
    ldc_descriptors = [parse_ldc_name_from_path(path) for path in files]

    # sanity checks
    for ldc_desc in ldc_descriptors:
        required = '{0}/xparse/{1}.gz'.format(args.workspace, ldc_desc['name'])
        if not os.path.exists(required):
            raise Exception('File not found: %s', required)

    # distribute jobs
    pool = Pool(args.jobs)
    logging.info('Distributing %d jobs to %d workers', len(ldc_descriptors), args.jobs)

    t0 = time()
    results = pool.map(partial(extract_grid, args=args), ldc_descriptors)
    dt = time() - t0
    logging.info('Total time: %f seconds', dt)
    
    try:
        # prints a Markdown table if possible
        from tabulate import tabulate
        print tabulate(zip((ldc_desc['name'] for ldc_desc in ldc_descriptors), results),
                headers=['Corpus', 'Time (s)'],
                tablefmt='pipe')
    except ImportError:
        logging.info('Consider installing tabulate to get nice summaries.')
    

if __name__ == '__main__':
    main(parse_command_line())

