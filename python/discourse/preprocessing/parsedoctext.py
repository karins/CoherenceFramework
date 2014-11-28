"""
This module distributes jobs to Stanford Core NLP.
The goal is to split sentences from SGML documents (such as produced by docs.py)
and parse them with a PCFG parser.

This module delegates the actual call to the parser to a Java wrapper.
Unfortunately, the java wrapper does not actually use a DOM implementation, so even though
the output file will look like an XML, the text content will not comply with XML formatting.
This means the best way to get the parse trees out of the sgml-formatted output of the java 
wrapper is with a SAX parser (sgml.py contains one).

@author waziz
"""
import logging
import argparse
import sys
import os
import gzip
import shlex
import subprocess
import multiprocessing
import traceback
import time
import itertools
from multiprocessing import Pool
from functools import partial
from ldc import get_ldc_name
from discourse.doctext import iterdoctext, writedoctext
from nltk.tree import Tree
from discourse.util import tabulate


def parse(content, args):
    """
    Parse a number of segments. 
    
    Arguments
    ---------
    mem: how much memory is available to the parser
    parser: path to jar
    models: path to jar
    grammar: path to gz
    threads: how many threads are available to the parser
    maxlength: segment maximum length (longer segments are skipped and the output is an empty parse tree: (())
    empty_seg: the token that marks an empty segment

    Returns
    -------
    list of parse trees (as strings)
    """
    params = {'mem': args.mem,
            'parser': args.parser,
            'models': args.models,
            'grammar': args.grammar,
            'threads': args.threads,
            'maxlength': args.max_length,
            }
    cmd_line = 'java -mx%(mem)dg -cp "%(parser)s:%(models)s" edu.stanford.nlp.parser.lexparser.LexicalizedParser -nthreads %(threads)d -sentences newline -maxLength %(maxlength)d -outputFormat oneline %(grammar)s -' % (params)
    cmd_args = shlex.split(cmd_line)
    logging.debug('running: %s', cmd_line)
    proc = subprocess.Popen(cmd_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate('\n'.join(content))
    # before returning we replace trees of empty segments (marked as so) by empty trees
    output = [line.strip() for line in stdout.split('\n')]
    return [ptb if seg != args.empty_seg else '(())' for seg, ptb in itertools.izip(content, output)]


def wrap_parse(doc, args):
    """
    Wraps a call to `parse` in a try/except block so that one can use a Pool
    and still get decent error messages.

    Arguments
    ---------
    doc: a tuple (segments, attributes), segments are strings
    args: a namespace, see `parse`

    Returns
    -------
    parse trees and time to parse
    """
    try:
        t0 = time.time()
        content, attrs = doc
        logging.info('Parsing document whose attributes are %s', attrs)
        trees = parse(content, args)
        dt = time.time() - t0
        return trees, dt 
    except:
        raise Exception(''.join(traceback.format_exception(*sys.exc_info())))


def parse_args():
    parser = argparse.ArgumentParser(description='Extracts documents from LDC GigaWord data',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input', nargs='?', 
            type=argparse.FileType('r'), default=sys.stdin,
            help='input corpus in doctext format')
    parser.add_argument('output', nargs='?', 
            type=argparse.FileType('w'), default=sys.stdout,
            help='PTB-style parse trees in doctext format')
    parser.add_argument('--empty-seg', '-e',
            type=str, default='<EMPTY>',
            help='stanford skips empty segments, so does doctext, thus one should have empty segments marked with a token, this is the token you have used to flag empty segments when you produced doctext files')
    parser.add_argument('--max-length', '-m',
            type=int, default=150,
            help='maximum sentence length (necessary to prevent Stanford from crashing)')
    parser.add_argument('--jobs', '-j', type=int, default=4,
            help='number of jobs (documents in parallel)')
    parser.add_argument('--mem', type=int, default=10,
            help='memory (in G) for each instance of the stanford parser')
    parser.add_argument('--threads', type=int, default=4,
            help='nuber of threads for each instance of the stanford parser')
    parser.add_argument('--parser', type=str, 
            default='/home/waziz/tools/stanford/stanford-parser-full-2014-10-31/stanford-parser.jar',
            help='Path to Stanford parser (jar)')
    parser.add_argument('--models', type=str, 
            default='/home/waziz/tools/stanford/stanford-parser-full-2014-10-31/stanford-parser-3.5.0-models.jar',
            help='Path to Stanford parser models (jar)')
    parser.add_argument('--grammar', type=str, 
            default='/home/waziz/tools/stanford/stanford-parser-full-2014-10-31/englishPCFG.ser.gz',
            help='Path to Stanford gramar (gz)')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')

    return args


def main(args):

    # reads docs from input
    docs = list(iterdoctext(args.input))

    # distributes the jobs
    pool = Pool(args.jobs)
    logging.info('Distributing %d jobs to %d workers', len(docs), args.jobs)
    result = pool.map(partial(wrap_parse, args=args), docs)

    # stores the output
    times = []
    for (content, attrs), (trees, dt) in itertools.izip(docs, result):
        writedoctext(args.output, trees, **attrs)
        times.append(dt)

    # dumps a summary
    print >> sys.stderr, tabulate(enumerate(times), headers=['doc', 'time'], tablefmt='pipe')


if __name__ == '__main__':
    main(parse_args())
