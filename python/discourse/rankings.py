"""

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
from discourse.util import partial_ordering


def parse_args():
    """parse command line arguments"""

    parser = argparse.ArgumentParser(description='Get rankings',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('output', nargs='?', 
            type=argparse.FileType('w'), default=sys.stdout,
            help='rankings')

    parser.add_argument('--named-system',  
            default=[], action='append', nargs=2,
            help='add a system (name and path to probabilities)')
    
    parser.add_argument('--systems',  
            default=[], nargs='+',
            help='add systems (path to probabilities, the file names the system)')

    parser.add_argument('--column', '-k',
            type=int, default=1,
            help='output score used to compare documents (0-based)')

    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')

    args = parser.parse_args()

    logging.basicConfig(
            level=(logging.DEBUG if args.verbose else logging.INFO), 
            format='%(levelname)s %(message)s')

    return args


def main(args):

    systems = list(args.named_system)
    [systems.append((os.path.basename(path), path)) for path in args.systems]

    if not systems:
        return 
    
    results = []
    for sysname, path in systems:
        results.append(np.loadtxt(path)[:,args.column])
        logging.debug('%s: %d documents', sysname, len(results[-1]))
    
    # checks that every system produced the same number of documents
    n_docs = [len(R) for R in results]
    if len(frozenset(n_docs)) != 1:
        raise Exception("Not all files contain the same number of documents (could you be mixing different language pairs?)")

    # total number of documents
    n_docs = n_docs[0]
    # makes the results a numpy array
    results = np.array(results)
    names = [sysname for sysname, path in systems]
    print >> args.output, '#best-to-worst'
    for i in range(n_docs):
        ranking = partial_ordering(results[:,i], reverse=True, shuf=False)  # random oder for ties
        print >> args.output, ' > '.join(' '.join(names[sysid] for sysid in group) for r, group in ranking)
        #ranking = sorted(enumerate(results[:,i]), key=lambda (_, score): score, reverse=True)
        #print ' '.join(names[sysid] for sysid, score in ranking)

    



if __name__ == '__main__':

    main(parse_args())


