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
from multiprocessing import Pool
from functools import partial
from ldc import get_ldc_name


def make_workspace(workspace):
    if not os.path.exists(workspace + '/parse'):
        os.makedirs(workspace + '/parse')
    if not os.path.exists(workspace + '/log-parse'):
        os.makedirs(workspace + '/log-parse')


def parse(input_gz, parse_out, parse_err, args):
    """Parse one gzipped sgml file"""
    params = {'mem': args.mem,
            'framework': args.discourse_framework,
            'corenlp': args.corenlp,
            'models': args.corenlp_models,
            'converter': args.converter
            }
    cmd_line = 'java -mx%(mem)dg -cp "%(framework)s:%(corenlp)s:%(models)s" %(converter)s' % (params)
    cmd_args = shlex.split(cmd_line)
    logging.info('running: %s', cmd_line)
    if args.dry_run:
        return False
    with gzip.open(input_gz, 'rb') as fin:
        with open(parse_out, 'wb') as fout:
            with open(parse_err, 'wb') as ferr:
                proc = subprocess.Popen(cmd_args, stdin=subprocess.PIPE, stdout=fout, stderr=ferr)
                proc.communicate(fin.read())
    return True


def parse_and_save(did, args):
    try:
        t0 = time.time()
        logging.info('Parsing document %s', did)
        input_gz = '{0}/sgml/{1}.gz'.format(args.workspace, did)
        parse_out = '{0}/parse/{1}'.format(args.workspace, did)
        parse_err = '{0}/log-parse/{1}'.format(args.workspace, did)
        logging.info('parsing: %s', did)
        parse(input_gz, parse_out, parse_err, args)
        dt = time.time() - t0
        logging.info('done: %s [%f seconds]', did, dt)
        return dt 
    except:
        raise Exception(''.join(traceback.format_exception(*sys.exc_info())))


def parse_command_line():
    parser = argparse.ArgumentParser(description='Extracts documents from LDC GigaWord data',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('workspace', type=str,
            help='where output files will be stored')
    parser.add_argument('--jobs', '-j', type=int, default=4,
            help='number of jobs')
    parser.add_argument('--dry-run', '-n', action='store_true',
            help='does not parse')
    parser.add_argument('--discourse-framework', '-d', type=str,
            default='/home/waziz/tools/discourse/DiscourseFramework.jar',
            help="Path to Karin's discourse framework (jar)")
    parser.add_argument('--converter', '-c', type=str,
            default='nlp.framework.discourse.ParseTreeConverter',
            help="Class in Karin's framework which wraps the parser")
    parser.add_argument('--corenlp', type=str, 
            default='/home/waziz/tools/stanford/stanford-corenlp-full-2014-10-31/stanford-corenlp-3.5.0.jar',
            help='Path to Stanford Core NLP (jar)')
    parser.add_argument('--corenlp-models', type=str, 
            default='/home/waziz/tools/stanford/stanford-corenlp-full-2014-10-31/stanford-corenlp-3.5.0-models.jar',
            help='Path to Stanford Core NLP models (jar)')
    parser.add_argument('--mem', type=int, default=1,
            help='memory (in G) for each instance of the stanford parser')
    parser.add_argument('--threads', type=int, default=4,
            help='nuber of threads for each instance of the stanford parser')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
    make_workspace(args.workspace)

    return args


def main(args):

    files = [path.strip() for path in sys.stdin]
    ldc_names = [get_ldc_name(path) for path in files]

    # sanity checks
    for ldc_name in ldc_names:
        if not os.path.exists('{0}/sgml/{1}.gz'.format(args.workspace, ldc_name)):
            raise Exception('File not found: %s', '{0}/sgml/{1}.gz'.format(args.workspace, ldc_name))

    pool = Pool(args.jobs)
    logging.info('Distributing %d jobs to %d workers', len(ldc_names), args.jobs)
    t0 = time.time()
    result = pool.map(partial(parse_and_save, args=args), ldc_names)
    dt = time.time() - t0
    logging.info('Total time: %f seconds', dt)

    data = zip(ldc_names, result)

    try:
        # prints a Markdown table if possible
        from tabulate import tabulate
        print tabulate(data,
                headers=['Corpus', 'Time (s)'],
                tablefmt='pipe')
    except:
        # plain table otherwise
        print '\n'.join('{0} {1}'.format(corpus, time) for corpus, time in data)

if __name__ == '__main__':
    main(parse_command_line())
