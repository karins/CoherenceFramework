"""
@author: wilkeraziz
"""

import sys
import os
import numpy as np
import itertools
import argparse
import logging
import modeleval
import wmtgold
from functools import partial
from tabulate import tabulate
from scipy import stats
from collections import namedtuple
from scipy.stats import spearmanr
from discourse.util import make_total_ordering
from discourse import command


RankerData = namedtuple('RankerData', 'alias systems rankings first intervals comparisons confidence')


def read_rankings(istream, tiebreak=False):
    """
    Read partial rankings from stream.

    Arguments
    ---------
    istream: input stream, one document per line, ranking is made of system names in order, from best to worst
        within a group systems are space separated, groups are separated with a greater than symbol '>'
        example: "A B C > D E F > G"
    tiebreak: by default ties are allowed, the ranking in the example above would be 1 1 1 2 2 2 3,
        otherwise we can break ties at random producing for example: 2 1 3 4 6 5 7

    Returns
    -------
    numpy array such that R[d,s] is the ranking of system s for document d
    system names
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
    """returns confidence intervals with a certain confidence level (1-pvalue)"""
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
    """
    Paired bootstrap resampling using a pairwise metric
    """
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
    """
    Compares diferent systems as ranked by a given model.
    """
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


def modelcmp(rankers, args, alias, header, metric, scale=100):
    systems = rankers[0].systems
    refsysid = rankers[0].systems.index(args.refsys)
    rankers_names = [ranker.alias for ranker in rankers]
    cmp_id = '_'.join(sorted(ranker.alias for ranker in rankers))

    R = np.array([ranker.rankings for ranker in rankers])
    logging.info('Assessing models: %s', alias)
    model_assessments = metric(R) * scale # assess_models(R, refsysid) 
    model_table = sorted(np.column_stack((rankers_names, model_assessments)),
            key=lambda row: float(row[1]), 
            reverse=True)
    for fmt in args.tablefmt:
        with open('{0}.modelcmp-{1}.{2}.{3}'.format(args.output, alias, cmp_id, fmt), 'w') as fo:
            print >> fo, tabulate(model_table,
                    headers=['model', header],
                    tablefmt=fmt,
                    floatfmt=".2f")
    logging.info('Confidence: %s', alias)
    confidence = paired_bootstrap_resampling(R, args.rounds, metric=metric) * 100
    for fmt in args.tablefmt:
        with open('{0}.modelcmp-{1}-confidence.{2}.{3}'.format(args.output, alias, cmp_id, fmt), 'w') as fo:
            print >> fo, tabulate(np.column_stack((rankers_names, confidence)),
                    headers=rankers_names,
                    tablefmt=fmt,
                    floatfmt=".2f")
    return model_assessments
    

def main(args):
    
    logging.basicConfig(
            level=(logging.DEBUG if args.verbose else logging.INFO), 
            format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')


    rankers = test_all_rankers(args.ranker, args.rounds, args.pvalue)

    for r, ranker in enumerate(rankers):
        # clean up system names
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
    # M - number of models
    # D - number of documents
    # S - number of systems
    # rankers_rankings is (M,D,S) 
    # the tranpose is (D,S,M)
    #rankings = np.array([ranker.rankings for ranker in rankers]).transpose((1,2,0))[:,refsysid,:]
    if args.refsys is not None:
        system_names = rankers[0].systems
        R = np.array([ranker.rankings for ranker in rankers])

        for metricname in args.metric:
            if metricname == 'ranks_higher':
                metricfunc = partial(modeleval.ranks_higher, sysid=refsysid, strictly=True)
                infix = 'refgt'
            elif metricname == 'no_worse':
                metricfunc = partial(modeleval.ranks_higher, sysid=refsysid, strictly=False)
                infix = 'refge'
            elif metricname == 'top1':
                metricfunc = partial(modeleval.top1, sysid=refsysid, exclusive=False)
                infix = 'first'
            elif metricname == 'top1x':
                metricfunc = partial(modeleval.top1, sysid=refsysid, exclusive=True)
                infix = 'firstx'

            #A = modelcmp(rankers, args, infix, infix, metric=metricfunc)
            

        A1 = modelcmp(rankers, args, 'refgt', 'refgt', metric=partial(modeleval.ranks_higher, sysid=refsysid, strictly=True))
        A2 = modelcmp(rankers, args, 'refge', 'refge', metric=partial(modeleval.ranks_higher, sysid=refsysid, strictly=False))
        A3 = modelcmp(rankers, args, 'firstx', 'firstx', metric=partial(modeleval.top1, sysid=refsysid, exclusive=True))
        A4 = modelcmp(rankers, args, 'first', 'first', metric=partial(modeleval.top1, sysid=refsysid, exclusive=True))
        A5 = modelcmp(rankers, args, 'EW', 'EW', metric=partial(modeleval.expected_win, sysid=refsysid))
        H = ['refgt', 'refge', 'firstx', 'first', 'EW']
        ALL = [rankers_names, A1, A2, A3, A4, A5]
        if args.pair in wmtgold.WMT14_RANKINGS:
            gold=np.array([wmtgold.WMT14_RANKINGS[args.pair][sysname] for sysname in system_names], float)
            A6 = modelcmp(rankers, args, 'gold', 'gold', scale=1.0, metric=partial(modeleval.rho, sysid=refsysid, gold_rankings=gold))
            ALL.append(A6)
            H.append('gold')
        
        model_table = sorted(np.column_stack(ALL),
                key=lambda row: float(row[1]), 
                reverse=True)
        for fmt in args.tablefmt:
            with open('{0}.modelcmp-allinone.{1}.{2}'.format(args.output, cmp_id, fmt), 'w') as fo:
                print >> fo, tabulate(model_table,
                        headers=['model'] + H,
                        tablefmt=fmt,
                        floatfmt=".2f")




        # spearman rho
        f_rho = np.zeros((len(rankers), len(rankers)))
        f_pvalue = np.zeros((len(rankers), len(rankers)))
        r_rho = np.zeros((len(rankers), len(rankers)))
        r_pvalue = np.zeros((len(rankers), len(rankers)))
        for r1, r2 in itertools.combinations(range(len(rankers)), 2):
            f_rho[r1,r2], f_pvalue[r1,r2] = spearmanr(rankers[r1].first, rankers[r2].first)
            f_rho[r2,r1], f_pvalue[r2,r1] = spearmanr(rankers[r2].first, rankers[r1].first)
            r_rho[r1,r2], r_pvalue[r1,r2] = spearmanr(rankers[r1].comparisons[refsysid,:], rankers[r2].comparisons[refsysid,:])
            r_rho[r2,r1], r_pvalue[r2,r1] = spearmanr(rankers[r2].comparisons[refsysid,:], rankers[r1].comparisons[refsysid,:])
        for fmt in args.tablefmt:
            with open('{0}.modelcmp-spearman-first.{1}.{2}'.format(args.output, cmp_id, fmt), 'w') as fo:
                print >> fo, tabulate(np.column_stack((rankers_names, f_rho, f_pvalue)),
                    headers=rankers_names + rankers_names,
                    tablefmt=fmt,
                    floatfmt='.4f')
            with open('{0}.modelcmp-spearman-ref.{1}.{2}'.format(args.output, cmp_id, fmt), 'w') as fo:
                print >> fo, tabulate(np.column_stack((rankers_names, r_rho, r_pvalue)),
                    headers=rankers_names + rankers_names,
                    tablefmt=fmt,
                    floatfmt='.4f')


@command('sigtest', 'scripts')
def argparser(parser=None, func=main):
    """parse command line arguments"""

    if parser is None:
        parser = argparse.ArgumentParser(prog='sigtest')

    parser.description = 'Significance tests'
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter

    parser.add_argument('output', 
            type=str,
            help='output prefix')
    parser.add_argument('--refsys', 
            type=str,
            help='a reference system')
    parser.add_argument('--pair', 
            type=str,
            help='language pair (to compare with goldstandard)')
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
    parser.add_argument('--metric',
            default=['ranks_higher'], action='append',
            choices=['top1', 'top1x', 'no_worse', 'EW'])
    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')

    if func is not None:
        parser.set_defaults(func=func)

    return parser


if __name__ == '__main__':
    main(argparser().parse_args())
