"""
Some utilitary functions.

@author waziz
"""
import sys
import itertools
import numpy as np
from collections import defaultdict

try:
    from progressbar import ProgressBar
    _PROGRESSBAR_ = True
except:
    _PROGRESSBAR_ = False

try:
    from doctext import iterdoctext
except:
    print "You need to add 'preprocessing' to your PYTHONPATH"
    sys.exit(0)


def bar(iterable):
    """wraps an iterable with a progress bar"""
    # if progressbar is installed we use it
    return ProgressBar()(iterable) if _PROGRESSBAR_ else iterable


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


def encode_documents(T, null=None):
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
    array([[[0], [1 2 3 1 2], [4]]], dtype=object)
    >>> V1['a'] # note how 'a' gets assigned id 0
    0
    >>> len(V1) # and there will be 5 unique words in the vocabulary
    5
    >>> T2, V2 = encode_documents(corpus, '<null>')
    >>> T2  # note how the first token won't be 0, because that's reserved for the null token
    array([[[1], [2 3 4 2 3], [5]]], dtype=object)
    >>> len(V2) # note how the vocabulary is bigger now (due to the null symbol)
    6
    >>> V2['<null>'] # and finally, the null symbol is assigned id 0
    0
    
    """
    vocab = defaultdict()
    if null is not None:
        register_token(null, vocab)  # make sure id=0 refers to the NULL token
    # register all tokens
    encoded = np.array([[np.array([register_token(t, vocab) for t in S], int) for S in D] for D in T])
    return encoded, vocab


def encode_test_documents(T, vocab):
    """
    Encodes test documents into numpy arrays of ids with a fixed (training) vocab.
    New symbols are assigned id -1.

    >>> vocab = {'<null>':0, 'a':1, 'b':2, 'c':3}
    >>> T = [[['a'], ['b', 'c', 'd', 'b', 'c'], ['e']]]
    >>> encode_test_documents(T, vocab)
    array([[[1], [ 2  3 -1  2  3], [-1]]], dtype=object)
    """
    return np.array([[np.array([vocab.get(t, -1) for t in S], int) for S in D] for D in T])


