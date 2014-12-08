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


WMT_DE_EN = {
'newstest2014.de-en.ref': 0,
'newstest2014.de-en.onlineB.0': 1,
'newstest2014.de-en.uedin-syntax.3035': 2,
'newstest2014.de-en.onlineA.0': 2,
'newstest2014.de-en.LIMSI-KIT-Submission.3359': 3,
'newstest2014.de-en.uedin-wmt14.3025': 3,
'newstest2014.de-en.eubridge.3569': 3,
'newstest2014.de-en.kit.3109': 4,
'newstest2014.de-en.RWTH-primary.3266': 4,
'newstest2014.de-en.DCU-ICTCAS-Tsinghua-L.3444': 5,
'newstest2014.de-en.CMU.3461': 5,
'newstest2014.de-en.rbmt4.0': 5,
'newstest2014.de-en.rbmt1.0': 6,
'newstest2014.de-en.onlineC.0': 7}

WMT_FR_EN = {
'newstest2014.fr-en.ref': 0,
'newstest2014.fr-en.uedin-wmt14.3024': 1,
'newstest2014.fr-en.kit.3112': 2,
'newstest2014.fr-en.onlineB.0': 2,
'newstest2014.fr-en.Stanford-University.3496': 2,
'newstest2014.fr-en.onlineA.0': 3,
'newstest2014.fr-en.rbmt1.0': 4,
'newstest2014.fr-en.rbmt4.0': 5,
'newstest2014.fr-en.onlineC.0': 6}

WMT_RU_EN = {
'newstest2014.ru-en.ref': 0,
'newstest2014.ru-en.AFRL-Post-edited.3431': 1,
'newstest2014.ru-en.onlineB.0': 2,
'newstest2014.ru-en.onlineA.0': 3,
'newstest2014.ru-en.PROMT-Hybrid.3084': 3,
'newstest2014.ru-en.PROMT-Rule-based.3085': 3,
'newstest2014.ru-en.uedin-wmt14.3364': 3,
'newstest2014.ru-en.shad-wmt14.3464': 3,
'newstest2014.ru-en.onlineG.0': 3,
'newstest2014.ru-en.AFRL.3349': 4,
'newstest2014.ru-en.uedin-syntax.3166': 5,
'newstest2014.ru-en.kaznu1.3549': 6,
'newstest2014.ru-en.rbmt1.0': 7,
'newstest2014.ru-en.rbmt4.0': 8}

WMT_RANKINGS = {'de-en': WMT_DE_EN, 'fr-en': WMT_FR_EN, 'ru-en': WMT_RU_EN}

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


def assess_models(R, refid, allow_ties=False):
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
    if not allow_ties:
        return np.array([np.array([float(sum(rankings[refid] < r for r in rankings))/(S-1) for rankings in docs]).mean() for docs in R])
    else:
        return np.array([np.array([float(sum(rankings[refid] <= r for r in rankings))/(S-1) for rankings in docs]).mean() for docs in R])


def assess_models_EW(R, refid):
    M, D, S = R.shape
    ref_wins = np.zeros((M, S))
    ref_loses = np.zeros((M, S))
    for m in xrange(M):
        for d in xrange(D):
            for s in xrange(S):
                if s == refid:
                    continue
                if R[m,d,refid] < R[m,d,s]:
                    ref_wins[m,s] += 1
                elif R[m,d,refid] > R[m,d,s]:
                    ref_loses[m,s] += 1

    score = np.zeros(M)
    for m in xrange(M):
        for s in xrange(S):
            if s == refid: 
                continue
            score[m] += ref_wins[m,s]/(ref_wins[m,s] + ref_loses[m,s])

    return score/S


def assess_models_top1(R, refid, allow_ties=True):
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
    with_ties = np.zeros(M, float)
    no_ties = np.zeros(M, float)
    for m in xrange(M):
        for d in xrange(D):
            if R[m,d,refid] == 1:
                with_ties[m] += 1
                if sum(r == 1 for r in R[m,d,:]) == 1:
                    no_ties[m] += 1
    return with_ties/D if allow_ties else no_ties/D


def assess_models_spearmanr(R, refid, gold_rankings):
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
    gold = np.concatenate((gold_rankings[:refid], gold_rankings[refid+1:]))
    mean_rankings = R.mean(1)
    ids = range(S)
    ids.remove(refid)
    hyp = mean_rankings[:,ids]
    return np.array([spearmanr(hyp[m], gold)[0] for m in xrange(M)])



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
    #confidence = paired_bootstrap_resampling(R, args.rounds, metric=partial(assess_models, refid=refsysid))
    confidence = paired_bootstrap_resampling(R, args.rounds, metric=metric) * 100
    for fmt in args.tablefmt:
        with open('{0}.modelcmp-{1}-confidence.{2}.{3}'.format(args.output, alias, cmp_id, fmt), 'w') as fo:
            print >> fo, tabulate(np.column_stack((rankers_names, confidence)),
                    headers=rankers_names,
                    tablefmt=fmt,
                    floatfmt=".2f")
    return model_assessments
    

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
    """
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
    """
    # M - number of models
    # D - number of documents
    # S - number of systems
    # rankers_rankings is (M,D,S) 
    # the tranpose is (D,S,M)
    #rankings = np.array([ranker.rankings for ranker in rankers]).transpose((1,2,0))[:,refsysid,:]
    if args.refsys is not None:
        system_names = rankers[0].systems
        R = np.array([ranker.rankings for ranker in rankers])

        """
        model_assessments = assess_models(R, refsysid) 
        model_table = sorted(np.column_stack((rankers_names, model_assessments * 100)),
                key=lambda row: float(row[1]), 
                reverse=True)
        for fmt in args.tablefmt:
            with open('{0}.modelcmp-goal.{1}.{2}'.format(args.output, cmp_id, fmt), 'w') as fo:
                print >> fo, tabulate(model_table,
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
        """
        A1 = modelcmp(rankers, args, 'refgt', 'refgt', metric=partial(assess_models, refid=refsysid, allow_ties=False))
        A2 = modelcmp(rankers, args, 'refge', 'refge', metric=partial(assess_models, refid=refsysid, allow_ties=True))
        A3 = modelcmp(rankers, args, 'firstx', 'firstx', metric=partial(assess_models_top1, refid=refsysid, allow_ties=False))
        A4 = modelcmp(rankers, args, 'first', 'first', metric=partial(assess_models_top1, refid=refsysid, allow_ties=True))
        A5 = modelcmp(rankers, args, 'EW', 'EW', metric=partial(assess_models_EW, refid=refsysid))
        H = ['refgt', 'refge', 'firstx', 'first', 'EW']
        ALL = [rankers_names, A1, A2, A3, A4, A5]
        if args.pair in WMT_RANKINGS:
            gold=np.array([WMT_RANKINGS[args.pair][sysname] for sysname in system_names], float)
            A6 = modelcmp(rankers, args, 'gold', 'gold', scale=1.0, metric=partial(assess_models_spearmanr, refid=refsysid, gold_rankings=gold))
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
