"""
It turns out that dealing with SGML files is very annoying.
This will convert SGML of SGML-like files into plain text files.

Not to lose document boundaries we use a very simple format:
    1) the header of a document is its first line, it starts with '#' 
    and contains space sparated key-value pairs
    keys and values are strings without quotes

    2) a document only contains non-empty lines

    3) an empty line separates adjacent documents

Example:

# id=doc1
This is a doc.
It has two sentences.

# id=doc2
This is another, this one has a single sentence.

@author waziz
"""
import logging
import argparse
import sys
import os
import traceback
import re
import gzip
import numpy as np
from time import time
from functools import partial
from multiprocessing import Pool
from docsgml import MakeSGMLDocs
from ldc import get_ldc_name 
from nltk.tree import Tree
from doctext import writedoctext


def make_workspace(workspace):
    if not os.path.exists(workspace + '/trees'):
        os.makedirs(workspace + '/trees')


def badsgml2goodsgml(ldc_name, args):
    path = '{0}/bsgml_trees/{1}'.format(args.workspace, ldc_name)
    logging.info('Processing %s', path)
    n_lines = []
    try:
        with open(path, 'r') as fi:
            lines = fi.read().split('\n')
            doc_re = re.compile('<doc id="(.+)">')
            doc_id, doc_lines = None, None
            sgmler = MakeSGMLDocs(file=ldc_name)
            for line in lines:
                # try to match <doc ...
                m = doc_re.match(line)
                if m is not None:
                    # starts a doc
                    doc_id = m.group(1)
                    doc_lines = []
                # try to match </doc>
                elif line == '</doc>':
                    # add the doc to an actual SGML file
                    sgmler.add('\n'.join(doc_lines), id=doc_id)
                    n_lines.append(len(doc_lines))
                    doc_lines = None
                    doc_id = None
                # if there is an open doc, append lines to it
                elif line and doc_lines is not None:
                    doc_lines.append(line)
                    #print >> sys.stderr, ptb_str
                    #print ' '.join(Tree(ptb_str).leaves())
            sgmler.writegz('{0}/trees/{1}'.format(args.workspace, ldc_name))
    except:
        raise Exception(''.join(traceback.format_exception(*sys.exc_info())))

    return n_lines


def badsgml2text(ldc_name, args):
    path = '{0}/bsgml_trees/{1}'.format(args.workspace, ldc_name)
    logging.info('Processing %s', path)
    n_lines = []
    try:
        with open(path, 'r') as fi:
            with gzip.open('{0}/trees/{1}.gz'.format(args.workspace, ldc_name), 'wb') as fo:
                lines = fi.read().split('\n')
                doc_re = re.compile('<doc id="(.+)">')
                doc_id, doc_lines = None, None
                for line in lines:
                    # try to match <doc ...
                    m = doc_re.match(line)
                    if m is not None:
                        # starts a doc
                        doc_id = m.group(1)
                        doc_lines = []
                    # try to match </doc>
                    elif line == '</doc>':
                        # add the doc to an actual SGML file
                        n_lines.append(len(doc_lines))
                        writedoctext(fo, doc_lines, id=doc_id)
                        doc_lines = None
                        doc_id = None
                    # if there is an open doc, append lines to it
                    elif line and doc_lines is not None:
                        doc_lines.append(line)
                        #print >> sys.stderr, ptb_str
                        #print ' '.join(Tree(ptb_str).leaves())
    except:
        raise Exception(''.join(traceback.format_exception(*sys.exc_info())))

    return n_lines
    

def parse_command_line():
    parser = argparse.ArgumentParser(description='Converts from SGML (or sgml-like) to plain text',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('workspace', type=str,
            help='where output files will be stored')
    parser.add_argument('--jobs', '-j', type=int, default=4,
            help='number of jobs')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
    make_workspace(args.workspace)

    return args



def main(args):

    files = [path.strip() for path in sys.stdin if not path.startswith('#')]
    ldc_names = [get_ldc_name(path) for path in files]

    # sanity checks
    for ldc_name in ldc_names:
        if not os.path.exists('{0}/bsgml_trees/{1}'.format(args.workspace, ldc_name)):
            raise Exception('File not found: %s', '{0}/bsgml_trees/{1}'.format(args.workspace, ldc_name))

    # distribute jobs
    pool = Pool(args.jobs)
    logging.info('Distributing %d jobs to %d workers', len(ldc_names), args.jobs)

    t0 = time()
    # results = pool.map(partial(fix_bad_sgml, args=args), ldc_names)
    results = pool.map(partial(badsgml2text, args=args), ldc_names)
    dt = time() - t0
    logging.info('Total time: %f seconds', dt)
    
    try:
        # prints a Markdown table if possible
        from tabulate import tabulate
        print tabulate(zip(ldc_names, 
                            (len(result) for result in results),
                            (sum(result) for result in results), 
                            (np.mean(result) for result in results)),
                        headers=['Corpus', 'Documents', 'Total Sentences', 'Average Document Length'],
                        tablefmt='pipe')
    except ImportError:
        logging.info('Consider installing tabulate to get nice summaries.')
    

if __name__ == '__main__':
    main(parse_command_line())


