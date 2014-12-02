"""
This module can be used to compare alternative document translations under a certain model.
It produces the rankings and a summary of how often each system ranks first.

The following is an example of ranking

#doc #best-to-worst
0 A B C
1 B A C
2 A C B
3 A C B

@author: wilkeraziz
"""

import sys
import argparse
import logging
import subprocess as sp
import shlex
import numpy as np
import os
from tabulate import tabulate


def parse_args():
    """parse command line arguments"""

    parser = argparse.ArgumentParser(description='Compares documents under different models',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('input', nargs='?', 
            type=argparse.FileType('r'), default=sys.stdin,
            help='list of test corpora')

    parser.add_argument('output',  
            type=str,
            help='prefix path to output document probabilities')
    
    parser.add_argument('rankings',  
            type=str,
            help='path to output rankings')

    parser.add_argument('--model',
            choices=['ibm', 'alouis'],
            default='ibm',
            help='available models')

    parser.add_argument('--column', '-k',
            type=int, default=1,
            help='output score used to compare documents (0-based)')

    parser.add_argument('--args',
            type=str,
            help='additional arguments')

    parser.add_argument('--format',
            choices=['plain', 'pipes', 'latex', 'simple', 'grid'],
            default='plain',
            help='output tabulate format')

    parser.add_argument('--exp',
            type=str, default='',
            help='names the experiment (extends output file names with it)')

    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')

    args = parser.parse_args()

    logging.basicConfig(
            level=(logging.DEBUG if args.verbose else logging.INFO), 
            format='%(levelname)s %(message)s')

    return args


def extension(ext):
    return '.' + ext if ext else ''

def main(args):

    # reads in the paths to files containing documents
    files = [path.strip() for path in args.input if not path.startswith('#')]
    # uses the name of the files as system ids
    names = [os.path.basename(path) for path in files]
    logging.info('Comparing %d files using %s model', len(files), args.model)

    # computes the scores for each document by each system
    results = []
    for name, input_path in zip(names, files):
        output_path = '{0}/{1}.{2}{3}'.format(args.output, args.model, name, extension(args.exp))
        cmd_str = 'python -m discourse.syntax_based.ibm1_decoder %s' % args.args
        logging.info('Running: %s < %s > %s', cmd_str, input_path, output_path)
        cmd_args = shlex.split(cmd_str)
        with open(output_path + '.stdout', 'w') as fo:
            with open(output_path + '.stderr', 'w') as fe:
                with open(input_path) as fi:
                    proc = sp.Popen(cmd_args, stdin=fi, stdout=fo, stderr=fe)
                    proc.wait()
        # loads in the score in column args.column
        results.append(np.loadtxt(output_path + '.stdout')[:,args.column])
        logging.info('%s: %d documents', name, len(results[-1]))
    
    # checks that every system produced the same name of documents
    n_docs = [len(R) for R in results]
    if len(frozenset(n_docs)) != 1:
        raise Exception('Not all files contain the same number of documents')

    # total number of documents
    n_docs = n_docs[0]
    # makes the results a numpy array
    results = np.array(results)

    with open(args.rankings + extension(args.exp), 'w') as fo:
        first = np.zeros(len(names), float)
        print >> fo, '#doc\t#best-to-worst'

        # computes and stores rankings
        # and counts how many times each system ranked first
        for i in range(n_docs):
            ranking = sorted(enumerate(results[:,i]), key=lambda (s, r): r, reverse=True)
            first_sys, first_score = ranking[0]
            first[first_sys] += 1
            print >> fo, '{0}\t{1}'.format(i, ' '.join(names[s] for s, r in ranking))
        
        # normalise
        first /= first.sum()
        # print summary
        table = sorted(zip(names, first), key=lambda (name, freq): freq, reverse=True)
        print tabulate(table, ['system', 'first'], tablefmt=args.format)

    



if __name__ == '__main__':

    main(parse_args())


