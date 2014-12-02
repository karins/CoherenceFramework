"""
@author: wilkeraziz
"""

import sys
import os
import numpy as np
import itertools
import argparse
import logging
from tabulate import tabulate
from scipy import stats
from collections import namedtuple
    

RankerData = namedtuple('RankerData', 'alias systems rankings first intervals comparisons confidence')


def read_rankings(istream):
    """
    Read rankings from stream.
    """

    # read in rankings
    system_set = set()
    rankings = []
    for line in istream:
        if line.startswith('#'):
            continue
        line = line.strip()
        if not line: 
            continue
        rankings.append(line.split())
        system_set.update(rankings[-1])

    # convert to return type
    names2id = {sysname: i for i, sysname in enumerate(sorted(system_set))}
    n_docs = len(rankings)
    n_systems = len(names2id)
    R = np.zeros((n_docs, n_systems), int)
    for d, ordered_names in enumerate(rankings):
        for r, sysname in enumerate(ordered_names, 1):
            R[d, names2id[sysname]] = r

    return R, sorted(system_set)

def assess_first(rankings):
    """
    Arguments
    ---------
    ranking: numpy array such that ranking[d,s] is systems' s ranking wrt document d
    Returns
    -------
    first: numpy array such that first[s] is the ratio at wich s is ranked first
    """
    N, M = rankings.shape
    first = np.zeros(M)
    for d in xrange(N):
        first[rankings[d].argmin()] += 1
    first /= N
    return first


def assess_comparisons(rankings):
    """
    Arguments
    ---------
    ranking: numpy array such that ranking[d,s] is systems' s ranking wrt document d
    Returns
    -------
    comparisons: numpy array such that comparisons[s1,s2] is the ratio at which s1 ranks strictly higher than s2
    """
    N, M = rankings.shape
    # comparisons[s1,s2]: how many times s1 ranks better than s2
    comparisons = np.zeros((M,M))
    # count
    for d in xrange(N):
        for s1, s2 in itertools.combinations(range(M), 2):
            # we ignore ties
            if rankings[d,s1] < rankings[d,s2]:
                comparisons[s1,s2] += 1
            elif rankings[d,s2] < rankings[d,s1]:
                comparisons[s2,s1] += 1

    # return normalised counts
    return comparisons/N


def bootstrap_resampling(R, rounds, metric):
    """
    Computes confidence intervals by bootstrap resampling
    """
    N, M = R.shape
    assessments = []
    for i in xrange(rounds):
        batch = np.random.choice(N, size=N, replace=True)
        assessments.append(metric(R[batch,:]))
    return np.sort(assessments, 0)
    

def get_confidence_intervals(assessments, p_value=0.05):
    N = assessments.shape[0]
    l = int(N * p_value/2)
    u = int(N * (1 - p_value/2))
    return assessments[(l, u),:].transpose()


def paired_bootstrap_resampling(R, rounds, metric):
    N, M = R.shape
    wins = np.zeros((M, M))
    for i in xrange(rounds):
        batch = np.random.choice(N, size=N, replace=True)
        assessments = metric(R[batch,:])
        # count victories
        for s1, s2 in itertools.combinations(range(M), 2):
            if assessments[s1,s2] > assessments[s2,s1]:
                wins[s1,s2] += 1
            elif assessments[s2,s1] > assessments[s1,s2]:
                wins[s2,s1] += 1
    return wins/rounds


def get_refsysid(systems, suffix='ref'):
    refs = [i for i, sysname in enumerate(systems) if sysname.endswith(suffix)]
    if len(refs) > 1:
        raise Exception('More than one reference system')
    elif len(refs) == 0:
        raise Exception('No reference system')
    return refs[0]


def test_ranker(ranker, rankings, systems, rounds=1000, p_value=0.95):
    
   
    # 1) FIRST
    first = assess_first(rankings)
    f_assessments = bootstrap_resampling(rankings, rounds, metric=assess_first)
    intervals = get_confidence_intervals(f_assessments, p_value)

    # 2) COMPARISONS
    comparisons = assess_comparisons(rankings)
    confidence = paired_bootstrap_resampling(rankings, rounds, metric=assess_comparisons)
    
    return RankerData(alias=ranker, 
            rankings=rankings, 
            systems=systems, 
            first=first, 
            intervals=intervals, 
            comparisons=comparisons, 
            confidence=confidence)


def test_all_rankers(rankers, rounds, p_value):
    # test each ranker
    rankers_data = []
    for ranker, path in rankers:
        logging.info('Comparing systems using %s: %s', ranker, path)
        rankings, systems = read_rankings(open(path))
        rankers_data.append(test_ranker(ranker, rankings, systems, rounds, p_value))
    return rankers_data
    

def main(args):

    rankers = test_all_rankers(args.ranker, args.rounds, args.pvalue)
    odirs = [os.path.split(path)[0] for _, path in args.ranker]

    for r, ranker in enumerate(rankers):
        # clean up system names
        #prefix = os.path.commonprefix(ranker.systems)
        #short_names = [sysname[len(prefix):] for sysname in ranker.systems]
        short_names = ranker.systems

        # 1) ranked first
        first_table = sorted(np.column_stack((short_names, ranker.first, ranker.intervals)),
                key=lambda row: row[1], 
                reverse=True)
        for fmt in args.tablefmt:
            with open('{0}/{1}.first.{2}'.format(odirs[r], ranker.alias, fmt), 'w') as fo:
                print >> fo, tabulate(first_table, 
                        headers=['system', 'first', 'lower', 'upper'],
                        tablefmt=fmt)
        
        # 2) all pairwise comparisons
        pairwise_table = np.column_stack((short_names, ranker.comparisons))
        confidence_table = np.column_stack((short_names, ranker.confidence))
        for fmt in args.tablefmt:
            with open('{0}/{1}.comparisons.{2}'.format(odirs[r], ranker.alias, fmt), 'w') as fo:
                print >> fo, tabulate(pairwise_table, 
                        headers=short_names,
                        tablefmt=fmt)
            with open('{0}/{1}.confidence.{2}'.format(odirs[r], ranker.alias, fmt), 'w') as fo:
                print >> fo, tabulate(confidence_table, 
                        headers=short_names,
                        tablefmt=fmt)

        # 3) reference wins
        if args.refsys is not None:
            refsysid = ranker.systems.index(args.refsys)
            ref_table = sorted(np.column_stack((short_names, ranker.comparisons[refsysid,:], ranker.confidence[refsysid,:])),
                    key=lambda row: row[1],
                    reverse=True)
            for fmt in args.tablefmt:
                with open('{0}/{1}.ref.{2}'.format(odirs[r], ranker.alias, fmt), 'w') as fo:
                    print >> fo, tabulate(ref_table, 
                        headers=['system', 'reference wins', 'confidence'],
                        tablefmt=fmt)
    

    # 4) model comparison

    # M - number of models
    # D - number of documents
    # S - number of systems
    # rankers_rankings is (M,D,S) 
    # the tranpose is (D,S,M)
    if args.refsys is not None:
        rankings = np.array([ranker.rankings for ranker in rankers]).transpose((1,2,0))[:,refsysid,:]
        rankers_names = [ranker.alias for ranker in rankers]
        comparisons = assess_comparisons(rankings)
        confidence = paired_bootstrap_resampling(rankings, args.rounds, metric=assess_comparisons)
        model_table = np.column_stack((rankers_names, confidence))
        cmp_id = '_'.join(sorted(ranker.alias for ranker in rankers))
        for fmt in args.tablefmt:
            with open('{0}/modelcmp.{1}.{2}'.format(args.output, cmp_id, fmt), 'w') as fo:
                print >> fo, tabulate(np.column_stack((rankers_names, confidence)), 
                        headers=rankers_names, 
                        tablefmt=fmt)


def parse_args():
    """parse command line arguments"""

    parser = argparse.ArgumentParser(description='Significance tests',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('output', 
            type=str,
            help='output prefix')
    parser.add_argument('--refsys', 
            type=str,
            help='a reference system')
    parser.add_argument('--ranker', 
            default=[],
            nargs=2, action='append',
            help='ranker and rankings')
    parser.add_argument('--rounds', 
            type=int, default=1000,
            help='number of rounds in bootstrap resampling')
    parser.add_argument('--pvalue', '-p',
            type=float, default=0.05,
            help='p-value')
    parser.add_argument('--tablefmt', 
            default=['plain'], action='append',
            choices=['plain', 'pipes', 'latex', 'simple', 'grid'],
            help='add an output tabulate format')
    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')

    args = parser.parse_args()

    logging.basicConfig(
            level=(logging.DEBUG if args.verbose else logging.INFO), 
            format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

    return args


if __name__ == '__main__':
    main(parse_args())
