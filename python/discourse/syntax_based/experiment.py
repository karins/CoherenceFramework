"""
@author: wilkeraziz
"""

import sys
import os
import logging
import argparse
import traceback
import itertools
import shlex
import subprocess as sp
import numpy as np
from glob import glob
from functools import partial
from multiprocessing import Pool
from discourse.doctext import iterdoctext, writedoctext
from discourse.syntax_based.dseq import dseqs
from discourse.syntax_based.ibm1_decoder import decode_many as ibm1_decode_many
from discourse.util import smart_open, tabulate


def make_namespace(args):
    experiment = '{0}.d{1}.m{2}'.format(args.training, args.depth, args.m1)
    if args.alias:
        experiment += '.' + args.alias
    names = argparse.Namespace(**{
        'docs': '{0}/docs'.format(args.data),
        'trees': '{0}/trees'.format(args.data),
        'workspace': args.workspace,
        'experiment': experiment,
        'dseqs': '{0}/dseqs{1}'.format(args.workspace, args.depth),
        'ibm1': '{0}/ibm1/{1}'.format(args.workspace, experiment),
        'ibm1_model': '{0}/ibm1/{1}/model'.format(args.workspace, experiment),
        't1': '{0}/ibm1/{1}/model/t1'.format(args.workspace, experiment),
        'ibm1_probs': '{0}/ibm1/{1}/probs'.format(args.workspace, experiment),
        'ibm1_eval': '{0}/ibm1/{1}/eval'.format(args.workspace, experiment),
        })

    if args.namespace:
        for k, v in vars(namespace).iteritems():
            print '{0}={1}'.format(k, repr(v))
        sys.exit(0)
    logging.info('Namespace: %s', names)

    if not args.dry_run:
        for path in [names.workspace, names.dseqs, names.ibm1, names.ibm1_model, names.ibm1_probs, names.ibm1_eval]:
            if not os.path.exists(path):
                os.makedirs(path)

    return names

def file_check(corpus, input_dir, output_dir):
    todo = frozenset(os.path.basename(path) for path in glob('{0}/{1}*'.format(input_dir, corpus)))
    logging.info('%d files matching %s', len(todo), '{0}/{1}*'.format(input_dir, corpus))
    done = frozenset(os.path.basename(path) for path in glob('{0}/{1}*'.format(output_dir, corpus)))
    logging.info('%d files matching %s', len(done), '{0}/{1}*'.format(output_dir, corpus))
    missing = todo - done
    return todo, done, missing

def wrap_dseqs((i, ipath, opath), depth, **kwargs):
    """
    Wrap a call to dseqs. To be used with Pool.map.
    """
    try:
        logging.info('(%d) %s ', i, ipath)
        fi = smart_open(ipath, 'r')
        fo = smart_open(opath, 'w')
        for trees, attrs in iterdoctext(fi):
            sequences = [' '.join(dseqs(tree, depth=depth, **kwargs)) for tree in trees]
            writedoctext(fo, sequences, **attrs)
    except:
        raise Exception(''.join(traceback.format_exception(*sys.exc_info())))

def extract_dseqs(corpus, args, namespace, **kwargs):
    """
    Extracts dsequences for a certain corpus
    """

    logging.info('Extracting d-sequences for: %s', corpus)
    input_dir = namespace.trees
    output_dir = namespace.dseqs

    todo, done, missing = file_check(corpus, input_dir, output_dir)
    if not missing:
        logging.info('all d-sequences of depth %d are there, nothing to be done', args.depth)
        return 
    
    jobs = [(j, '{0}/{1}'.format(input_dir, name), '{0}/{1}'.format(output_dir, name)) for j, name in enumerate(missing)]
    pool = Pool(args.jobs)
    logging.info('Distributing %d jobs to %d workers', len(jobs), args.jobs)
   
    if args.dry_run:
        return 

    pool.map(partial(wrap_dseqs, depth=args.depth, **kwargs), jobs)


def train_ibm1(args, namespace):
    logging.info('Training IBM model 1 with: %s', args.training)
    ll_path = '{0}/likelihood'.format(namespace.ibm1_model)
    output_path = namespace.t1  #'{0}/t1'.format(namespace.ibm1_model)
    if os.path.exists(output_path):
        logging.info('IBM model 1 already exists: %s', output_path)
        return 
    
    input_prefix = '{0}/{1}'.format(namespace.dseqs, args.training)
    training_files = glob(input_prefix + '*')
    logging.info('%d training files matching %s*', len(training_files), input_prefix)
    istream = itertools.chain(*map(smart_open, training_files))
    cmd_line = 'python -m discourse.syntax_based.ibm1 -m {0} -b -p {1} --ll {2} - {3}'.format(args.m1, args.m1_config, ll_path, output_path)
    logging.info(cmd_line)
    cmd_args = shlex.split(cmd_line)

    if args.dry_run:
        return

    proc = sp.Popen(cmd_args, stdin=sp.PIPE)
    proc.communicate(''.join(istream))


def decode_ibm1(corpus, args, namespace):
    """
    Computes IBM 1 probabilities for a certain corpus.
    """

    logging.info('Decoding with IBM model 1: %s', corpus)
    input_dir = namespace.dseqs
    output_dir = namespace.ibm1_probs

    todo, done, missing = file_check(corpus, input_dir, output_dir)
    if not missing:
        logging.info('all IBM1 probabilities are there, nothing to be done')
        return 

    if args.dry_run:
        return 
    
    ipaths = ['{0}/{1}'.format(input_dir, name) for name in missing]
    opaths = ['{0}/{1}'.format(output_dir, name) for name in missing]
    ibm1_decode_many(namespace.t1, ipaths, opaths, jobs=args.jobs)


def evaluate(corpus, model, args, namespace):
    logging.info('Evaluate (model=%s): %s', model, corpus)
    input_dir = namespace.ibm1_probs
    output_dir = '{0}/{1}'.format(namespace.ibm1_eval, corpus)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    names = sorted([os.path.basename(path) for path in glob('{0}/{1}*'.format(input_dir, corpus))])
    if not names:
        logging.info('nothing to do')
        return 
    logging.info('Evaluating %d systems for %s', len(names), corpus)

    results = []
    for name in names:
        results.append(np.loadtxt('{0}/{1}'.format(input_dir, name))[:,args.column])
        logging.debug('%s: %d documents', name, len(results[-1]))
    
    # checks that every system produced the same number of documents
    n_docs = [len(R) for R in results]
    if len(frozenset(n_docs)) != 1:
        raise Exception("Not all files contain the same number of documents (could you be mixing different language pairs?)")

    if args.dry_run:
        return 

    # total number of documents
    n_docs = n_docs[0]
    # makes the results a numpy array
    results = np.array(results)
    refsys = None
    if args.refsys:
        if args.refsys in names:
            logging.info('Using %s as reference', args.refsys)
            refsys = args.refsys
        else:
            logging.info('Unknown system %s cannot be used as reference', args.refsys)
    with open('{0}/rankings'.format(output_dir), 'w') as fo:
        print >> fo, '#best-to-worst'
        # computes and stores rankings
        # and counts how many times each system ranked first
        for i in range(n_docs):
            ranking = sorted(enumerate(results[:,i]), key=lambda (_, score): score, reverse=True)
            print >> fo, ' '.join(names[sysid] for sysid, score in ranking)
        

def parse_args():
    """parse command line arguments"""

    parser = argparse.ArgumentParser(description='Pipeline',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('workspace', 
            type=str, 
            help='where everything happens')
    parser.add_argument('--data', 
            type=str, default='../data',
            help='data folder (where we find corpora: text and parse trees)')
    parser.add_argument('--training', 
            type=str, default='potet.ref',
            help='training corpus')
    parser.add_argument('--dev', 
            type=str, # default='newstest2013.de-en',
            help='dev corpus')
    parser.add_argument('--test', 
            type=str, # default='newstest2014.de-en',
            help='test corpus')
    parser.add_argument('--jobs', 
            type=int, default=10,
            help='jobs in parallel')
    parser.add_argument('--dry-run', '-n',
            action='store_true',
            help='only stage operations')
    parser.add_argument('--namespace',
            action='store_true',
            help='print namespace and exit')
    parser.add_argument('--alias',
            type=str, default='',
            help='name the experiment (re model)')
    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')


    # d-sequences
    dseq_group = parser.add_argument_group('d-sequences')
    dseq_group.add_argument('--depth', 
            type=int, default=2,
            help='depth of d-sequences')

    # IBM1
    ibm_group = parser.add_argument_group('IBM model 1')
    ibm_group.add_argument('--m1', 
            type=int, default=30,
            help='ibm model 1 iterations')
    ibm_group.add_argument('--m1-config', 
            type=str, default='',
            help='additional options to dicourse.syntax_based.ibm1')
    
    # eval
    eval_group = parser.add_argument_group('Evaluation')
    eval_group.add_argument('--column', '-k',
            type=int, default=1,
            help='output score used to compare documents (0-based)')
    eval_group.add_argument('--refsys',
            type=str,
            help='choose a reference system (e.g. newstest2013.de-en.ref)')
    eval_group.add_argument('--tablefmt', 
            default=['plain'], action='append',
            choices=['plain', 'pipes', 'latex', 'simple', 'grid'],
            help='add an output tabulate format')

    args = parser.parse_args()

    logging.basicConfig(
            level=(logging.DEBUG if args.verbose else logging.INFO), 
            format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

    return args



def main(args):

    # make namespace
    namespace = make_namespace(args)

    # pipeline
    extract_dseqs(args.training, args, namespace, backoff='[*]')
   
    if args.dev:
        extract_dseqs(args.dev, args, namespace, backoff=['*'])
    if args.test:
        extract_dseqs(args.test, args, namespace, backoff=['*'])

    train_ibm1(args, namespace)
    
    if args.test:
        decode_ibm1(args.test, args, namespace)
        evaluate(args.test, namespace.t1, args, namespace)


if __name__ == '__main__':
    main(parse_args())
