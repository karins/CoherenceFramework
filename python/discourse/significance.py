"""
@author: wilkeraziz
"""

import sys
import os
import numpy as np
import itertools
import argparse
import logging
from functools import partial
from tabulate import tabulate
from scipy import stats
from collections import namedtuple
from discourse.util import make_total_ordering
from scipy.stats import spearmanr


RankerData = namedtuple('RankerData', 'alias systems rankings first intervals comparisons confidence')


def read_rankings(istream, tiebreak=False):
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
        groups = [g.split() for g in line.split('>')]
        rankings.append(groups)
        [system_set.update(g) for g in groups]

    # convert to return type
    names2id = {sysname: i for i, sysname in enumerate(sorted(system_set))}
    n_docs = len(rankings)
    n_systems = len(names2id)
    R = np.zeros((n_docs, n_systems), int)
    for d, groups in enumerate(rankings):
        if not tiebreak:
            for r, group in enumerate(groups, 1):
                for sysname in group:
                    R[d, names2id[sysname]] = r
        else:
            for r, sysname in enumerate(make_total_ordering(groups), 1):
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
    return np.array([sum(r == 1 for r in rankings[:,s]) for s in xrange(M)], float)/N


def assess_first_noties(rankings):
    """
    Arguments
    ---------
    ranking: numpy array such that ranking[d,m] is the ref's ranking by model m in document d
    Returns
    -------
    goodness: numpy array such that goodness[m] is the ratio at wich ranking[d,m] == 1 
    """
    N, M = rankings.shape
    goodness = np.zeros(M)
    skip = 0
    for d in xrange(N):
        # if there is a tie at the first position
        if sum(r == 1 for r in rankings[d,:]) > 1:
            skip += 1
            continue
        goodness[rankings[d,:].argmin()] += 1

    logging.info('Skipping %d out of %d', skip, N)
    return np.array([sum(r == 1 for r in rankings[:,m]) for m in range(M)], float)/N


def assess_comparisons(rankings):
    """
    Arguments
    ---------
    ranking: numpy array such that ranking[d,s] is systems' s ranking wrt document d
    Returns
    -------
    comparisons: numpy array such that comparisons[s1,s2] is the rate at which s1 ranks strictly higher than s2
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
 

def get_confidence_intervals(assessments, p_value=0.05):
    N = assessments.shape[0]
    l = int(N * p_value/2)
    u = int(N * (1 - p_value/2))
    return assessments[(l, u),:].transpose()


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


def assess_models(R, refid):
    """
    Arguments
    ---------
    R[m,d,s] is the ranking of system s in document d by model m

    Returns
    -------
    goodness[m] = average across documents of the rate at which model m scores the reference higher than every other system
    """
    M, D, S = R.shape
    # for each model
    #   for each document
    #       computes the rate at which the references scores higher than other systems (the denominator S-1 excludes the ref)
    #   and returns the average across documents for that given model
    return np.array([np.array([float(sum(rankings[refid] < r for r in rankings))/(S-1) for rankings in docs]).mean() for docs in R])


def paired_bootstrap_resampling(R, rounds, metric):
    """
    Arguments
    ---------
    R such that T[m,d,s] is the ranking model m assigns to system s for document d 
    """
    M, D, S = R.shape
    wins = np.zeros((M, M))
    for i in xrange(rounds):
        batch = np.random.choice(D, size=D, replace=True)
        assessments = metric(R[:,batch,:])
        # count victories
        for m1, m2 in itertools.combinations(range(M), 2):
            if assessments[m1] > assessments[m2]:
                wins[m1,m2] += 1
            elif assessments[m2] > assessments[m1]:
                wins[m2,m1] += 1
    return wins/rounds


def paired_bootstrap_resampling_pairwise(R, rounds, pairwise_metric):
    N, M = R.shape
    wins = np.zeros((M, M))
    for i in xrange(rounds):
        batch = np.random.choice(N, size=N, replace=True)
        assessments = pairwise_metric(R[batch,:])
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
    confidence = paired_bootstrap_resampling_pairwise(rankings, rounds, pairwise_metric=assess_comparisons)
    
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
    #odirs = [os.path.split(path)[0] for _, path in args.ranker]

    for r, ranker in enumerate(rankers):
        # clean up system names
        #prefix = os.path.commonprefix(ranker.systems)
        #short_names = [sysname[len(prefix):] for sysname in ranker.systems]
        short_names = ranker.systems

        # 1) ranked first
        first_table = sorted(np.column_stack((short_names, ranker.first * 100 , ranker.intervals * 100)),
                key=lambda row: float(row[1]), 
                reverse=True)
        for fmt in args.tablefmt:
            with open('{0}.syscmp-first.{1}.{2}'.format(args.output, ranker.alias, fmt), 'w') as fo:
                print >> fo, tabulate(first_table, 
                        headers=['system', 'first', 'lower', 'upper'],
                        tablefmt=fmt,
                        floatfmt=".2f")
        
        # 2) all pairwise comparisons
        pairwise_table = np.column_stack((short_names, ranker.comparisons * 100))
        confidence_table = np.column_stack((short_names, ranker.confidence * 100))
        for fmt in args.tablefmt:
            with open('{0}.syscmp-pairwise.{1}.{2}'.format(args.output, ranker.alias, fmt), 'w') as fo:
                print >> fo, tabulate(pairwise_table, 
                        headers=short_names,
                        tablefmt=fmt,
                        floatfmt=".2f")
            with open('{0}.syscmp-confidence.{1}.{2}'.format(args.output, ranker.alias, fmt), 'w') as fo:
                print >> fo, tabulate(confidence_table, 
                        headers=short_names,
                        tablefmt=fmt,
                        floatfmt=".2f")

        # 3) reference wins
        if args.refsys is not None:
            refsysid = ranker.systems.index(args.refsys)
            ref_table = sorted(np.column_stack((short_names, ranker.comparisons[refsysid,:] * 100, ranker.confidence[refsysid,:] * 100)),
                    key=lambda row: float(row[1]),
                    reverse=True)
            for fmt in args.tablefmt:
                with open('{0}.syscmp-ref.{1}.{2}'.format(args.output, ranker.alias, fmt), 'w') as fo:
                    print >> fo, tabulate(ref_table, 
                        headers=['system', 'reference wins', 'confidence'],
                        tablefmt=fmt,
                        floatfmt=".2f")

    # 4) model comparison

    rankers_names = [ranker.alias for ranker in rankers]
    cmp_id = '_'.join(sorted(ranker.alias for ranker in rankers))
    cmp_first = np.column_stack([ranker.first for ranker in rankers])
    cmp_ref = np.column_stack([ranker.comparisons[refsysid,:] for ranker in rankers])
    for fmt in args.tablefmt:
        with open('{0}.modelcmp-first.{1}.{2}'.format(args.output, cmp_id, fmt), 'w') as fo:
            print >> fo, tabulate(np.column_stack((short_names, cmp_first * 100)), 
                    headers=rankers_names,
                    tablefmt=fmt,
                    floatfmt=".2f")
        with open('{0}.modelcmp-ref.{1}.{2}'.format(args.output, cmp_id, fmt), 'w') as fo:
            print >> fo, tabulate(np.column_stack((short_names, cmp_ref * 100)), 
                    headers=rankers_names,
                    tablefmt=fmt,
                    floatfmt=".2f")
    # M - number of models
    # D - number of documents
    # S - number of systems
    # rankers_rankings is (M,D,S) 
    # the tranpose is (D,S,M)
    #rankings = np.array([ranker.rankings for ranker in rankers]).transpose((1,2,0))[:,refsysid,:]
    if args.refsys is not None:
        R = np.array([ranker.rankings for ranker in rankers])
        model_assessments = assess_models(R, refsysid)
        for fmt in args.tablefmt:
            with open('{0}.modelcmp-goal.{1}.{2}'.format(args.output, cmp_id, fmt), 'w') as fo:
                print >> fo, tabulate(np.column_stack((rankers_names, model_assessments * 100)),
                        headers=['model', 'ref wins'],
                        tablefmt=fmt,
                        floatfmt=".2f")
        logging.info('Comparing models')
        confidence = paired_bootstrap_resampling(R, args.rounds, metric=partial(assess_models, refid=refsysid))
        for fmt in args.tablefmt:
            with open('{0}.modelcmp-confidence.{1}.{2}'.format(args.output, cmp_id, fmt), 'w') as fo:
                print >> fo, tabulate(np.column_stack((rankers_names, confidence * 100)),
                        headers=rankers_names,
                        tablefmt=fmt,
                        floatfmt=".2f")

        # spearman rho
        f_rho = np.zeros((len(rankers), len(rankers)))
        f_pvalue = np.zeros((len(rankers), len(rankers)))
        for r1, r2 in itertools.combinations(range(len(rankers)), 2):
            F1 = rankers[r1].first
            F2 = rankers[r2].first
            f_rho[r1,r2], f_pvalue[r1,r2] = spearmanr(rankers[r1].first, rankers[r2].first)
            f_rho[r2,r1], f_pvalue[r2,r1] = spearmanr(rankers[r2].first, rankers[r1].first)
        print tabulate(np.column_stack((rankers_names, f_rho, f_pvalue)),
            headers=rankers_names + rankers_names,
            tablefmt='plain',
            floatfmt='.4f')




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
