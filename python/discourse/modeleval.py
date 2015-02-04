import numpy as np
from scipy.stats import spearmanr


def ranks_higher(R, sysid, strictly=True):
    """
    How often a system rank higher than others.

    Arguments
    ---------
    R[m,d,s]: is the ranking of system s in document d by model m
    sysid: is the index of the system we are taking as reference
    strictly: strictly higher or not 

    Returns
    -------
    goodness[m] = average across documents of the rate at which model m scores sysid higher than other systems
    """
    M, D, S = R.shape
    # for each model
    #   for each document
    #       computes the rate at which the references scores higher than other systems (the denominator S-1 excludes the ref)
    #   and returns the average across documents for that given model
    if strictly:
        return np.array([np.array([float(sum(rankings[sysid] < r for r in rankings))/(S-1) for rankings in docs]).mean() for docs in R])
    else:
        return np.array([np.array([float(sum(rankings[sysid] <= r for r in rankings))/(S-1) for rankings in docs]).mean() for docs in R])


def expected_win(R, sysid):
    """
    WMT's expected win metric.

    Arguments
    ---------
    R[m,d,s]: is the ranking of system s in document d by model m
    sysid: is the index of the system we are taking as reference

    Returns
    -------
    expectedwin[m]
    """
    M, D, S = R.shape
    ref_wins = np.zeros((M, S))
    ref_loses = np.zeros((M, S))
    for m in xrange(M):
        for d in xrange(D):
            for s in xrange(S):
                if s == sysid:
                    continue
                if R[m,d,sysid] < R[m,d,s]:
                    ref_wins[m,s] += 1
                elif R[m,d,sysid] > R[m,d,s]:
                    ref_loses[m,s] += 1

    score = np.zeros(M)
    for m in xrange(M):
        for s in xrange(S):
            if s == sysid: 
                continue
            score[m] += ref_wins[m,s]/(ref_wins[m,s] + ref_loses[m,s])

    return score/S


def top1(R, sysid, exclusive=False):
    """
    Arguments
    ---------
    R[m,d,s]: is the ranking of system s in document d by model m
    exclusive: whether or not we allow the first ranking to be shared with other systems

    Returns
    -------
    goodness[m] = average across documents of the rate at which model m is ranked first
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
            if R[m,d,sysid] == 1:
                with_ties[m] += 1
                if sum(r == 1 for r in R[m,d,:]) == 1:
                    no_ties[m] += 1
    return no_ties/D if exclusive else with_ties/D


def rho(R, sysid, gold_rankings):
    """
    Arguments
    ---------
    R[m,d,s]: is the ranking of system s in document d by model m
    sysid: a reference system

    Returns
    -------
    goodness[m] = average spearman rank correlation between model and gold standard excluding the reference system
    """
    M, D, S = R.shape
    # for each model
    #   for each document
    #       computes the rate at which the references scores higher than other systems (the denominator S-1 excludes the ref)
    #   and returns the average across documents for that given model
    gold = np.concatenate((gold_rankings[:sysid], gold_rankings[sysid+1:]))
    mean_rankings = R.mean(1)
    ids = range(S)
    ids.remove(sysid)
    hyp = mean_rankings[:,ids]
    return np.array([spearmanr(hyp[m], gold)[0] for m in xrange(M)])
