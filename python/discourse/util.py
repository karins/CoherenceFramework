"""
Some utilitary functions.

You can test me:
    python -m doctest util.py

Also check my docstrings ;)

@author: wilkeraziz
"""
import sys
import itertools
import numpy as np
import gzip
import glob
import random
from collections import defaultdict, Counter

try:
    from progressbar import ProgressBar, AnimatedMarker, Percentage, Timer, ETA, Bar
    _PROGRESSBAR_ = True
except:
    _PROGRESSBAR_ = False
    
try:
    import tabulate as tab
    _TABULATE_ = True
except:
    _TABULATE_ = False

from doctext import iterdoctext


def bar(iterable, msg='', maxval=None, none=False):
    """wraps an iterable with a progress bar"""
    # if progressbar is installed we use it
    if not _PROGRESSBAR_ or none:
        return iterable
    widgets=[msg, Bar(), ' ', Percentage(), ' ', Timer(), ' ', ETA()]
    if maxval is None:
        b = ProgressBar(widgets=widgets)
    else:
        b = ProgressBar(maxval=maxval, widgets=widgets)
    return b(iterable)


def tabulate(*args, **kwargs):
    """wraps a call to tabulate.tabulate if available"""
    return tab.tabulate(*args, **kwargs) if _TABULATE_ else 'Tip: consider installing tabulate for nice summaries at the end of some processes'


def pairwise(iterable):
    """
    Iterate over pairs in the sequence: pairwise((s1, s2, ..., sn)) -> (s1,s2), (s2, s3), ...(sn-1, sn)

    >>> seq = [1,2,3,4]
    >>> list(pairwise(seq))
    [(1, 2), (2, 3), (3, 4)]

    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


def ibm_pairwise(document, e0=0):
    """
    Iterate over pairs of adjacent sentences (e0..en, f1..fm) introducing the null symbol e0.

    Arguments
    ---------
    document: a list sentences represented bysyntactic patterns 
    e0: the id of the null symbol (typically 0)

    Returns
    -------
    A generator of sentence pairs where e0..en is the first sentence and f1..fm is the second one (and e0 is inserted by this method)

    >>> doc = [[1], [2,3,4], [5]]
    >>> list(ibm_pairwise(doc))
    [(array([0, 1]), [2, 3, 4]), (array([0, 2, 3, 4]), [5])]

    """
    return ((np.concatenate((np.array([e0], int), _E)), F) for _E, F in pairwise(document))


def partial_ordering(elements, reverse=False, shuf=False):
    sorted_ids = sorted(range(len(elements)), key=lambda i: elements[i], reverse=reverse)
    if not shuf:
        make_list = lambda g: list(g) 
    else:
        make_list = sorted(g, key=lambda _: random.random())
    return [(e, make_list(g)) for e, g in itertools.groupby(sorted_ids, key=lambda i: elements[i])]


def make_total_ordering(partial):
    """
    Returns an iterator over a total ordering (ties are randomly broken) from a partial ordering
    Arguments
    ---------
    partial: ordered list of groups (within a group elements are tied)
    Returns
    -------
    total ordering: a generator of elements respecting that partial ordering, however with ties randomly broken

    Eg.
    make_total_ordering([[1,2], [3,4,5]])
    might produce
    [1,2,3,4,5]
    or
    [2,1,3,5,4]
    but will never produce
    [1,3,2,4,5] (note the partial ordering was not respected)
    """
    return itertools.chain(*(sorted(group, key=lambda _: random.random()) for group in partial))

def _partial_ordering(elements, shuf=True, reverse=False):
    """
    Returns a "random partial ordering", that is, a partial ordering, where tied elements are sorted at random.

    Arguments
    ---------
    elements: list of elements to be sorted
    shuf: whether or not to shuffle ties (defaults to True)
    reverse: asc vs desc order

    Returns
    -------
    partial ordering (sorted ids)

    >>> x = [1, 1, 5, 6, 5, 7, 4, 3, 5]
    >>> f = lambda l, order: [l[i] for i in order]
    >>> all(f(x, partial_ordering(x)) == sorted(x) for _ in range(10))
    True
    """
    if not shuf:
        my_cmp = cmp
    else:
        my_cmp = lambda x, y: cmp(x,y) if x != y else cmp(0, random.choice([-1,1]))
    return tuple(i for i, e in sorted(enumerate(elements), key=lambda (i, e): e, cmp=my_cmp, reverse=reverse))


def read_documents(istream, doc_boundaries=False):
    """reads documents from an input stream"""
    def wrap_doc(sentences):
        """wraps a doc with document tags if requested"""
        return itertools.chain(['<doc>'], sentences, ['</doc>']) if doc_boundaries else sentences

    return [[line.split() for line in wrap_doc(lines)] for lines, attrs in iterdoctext(istream)]


def register_token(t, vocab):
    """adds a token t to the vocab if not there"""
    i = vocab.get(t, None)
    if i is None:
        i = len(vocab)
        vocab[t] = i
    return i

def find_least_common(T):
    counter = Counter(itertools.chain(*(itertools.chain(*((p for p in S) for S in D )) for D in T)))
    if not counter:
        return frozenset(), 0
    sorted_pairs = counter.most_common()
    n = sorted_pairs[-1][1]
    return frozenset(u for u, c in itertools.takewhile(lambda (u, c): c == n, reversed(sorted_pairs))), n


def encode_documents(T, null='<null>', unk='<unk>', ignore=frozenset()):
    """
    Encodes the corpus using numpy arrays of integers.

    Arguments
    ---------
    T: corpus as returned by `read_documents`
    null: null symbol, if not None, it will get id 0

    Returns
    -------
    corpus and vocab (a defaultdict)

    >>> doc = [['a'], ['b', 'c', 'd', 'b', 'c'], ['e']]
    >>> corpus = [doc]
    >>> T1, V1 = encode_documents(corpus)
    >>> T1 
    array([[array([0]), array([1, 2, 3, 1, 2]), array([4])]], dtype=object)
    >>> V1['a'] # note how 'a' gets assigned id 0
    0
    >>> len(V1) # and there will be 5 unique words in the vocabulary
    5
    >>> T2, V2 = encode_documents(corpus, '<null>')
    >>> T2  # note how the first token won't be 0, because that's reserved for the null token
    array([[array([1]), array([2, 3, 4, 2, 3]), array([5])]], dtype=object)
    >>> len(V2) # note how the vocabulary is bigger now (due to the null symbol)
    6
    >>> V2['<null>'] # and finally, the null symbol is assigned id 0
    0
    
    """
    vocab = defaultdict()
    register_token(null, vocab)  # make sure id=0 refers to the NULL token
    register_token(unk, vocab)
    wrap_token = lambda t: t if t not in ignore else unk
    # register all tokens
    encoded = np.array([[np.array([register_token(wrap_token(t), vocab) for t in S], int) for S in D] for D in T])
    return encoded, vocab


def encode_test_documents(T, vocab, unk='<unk>'):
    """
    Encodes test documents into numpy arrays of ids with a fixed (training) vocab.
    New symbols are assigned id -1.

    >>> vocab = {'<null>':0, 'a':1, 'b':2, 'c':3}
    >>> T = [[['a'], ['b', 'c', 'd', 'b', 'c'], ['e']]]
    >>> encode_test_documents(T, vocab)
    array([[array([1]), array([ 2,  3, -1,  2,  3]), array([-1])]], dtype=object)
    """
    assert unk in vocab, 'Your vocab does not assign an id to unknonw symbols'
    unk_id = vocab['<unk>']
    return np.array([[np.array([vocab.get(t, unk_id) for t in S], int) for S in D] for D in T])


def smart_open(path, *args, **kwargs):
    if path.endswith('.gz'):
        return gzip.open(path, *args, **kwargs)
    else:
        return open(path, *args, **kwargs)

if __name__ == '__main__':
    print >> sys.stderr, __doc__
