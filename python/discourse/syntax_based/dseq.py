"""
Extract d-sequences from PTB-style parse trees (see Louis and Nekova, 2012).


@author: wilkeraziz
"""

import string
import argparse
import sys
from nltk.tree import Tree
from discourse.doctext import writedoctext, iterdoctext
from discourse import command


def _find_subtrees(tree, depth, target_depth, subtrees):
    """
    Recursively searches for subtrees at a certain depth.

    Arguments
    ---------
    nlt.tree.Tree tree: the current subtree
    depth: the current depth
    target_depth: how deep we should go
    subtrees: list of subtrees at the target depth
    """
    if depth + 1 == target_depth:
        subtrees.extend(t for t in tree if isinstance(t, Tree))
    else:
        [_find_subtrees(t, depth + 1, target_depth, subtrees) for t in tree if isinstance(t, Tree)]


def find_subtrees(tree, depth):
    """
    Returns all subtrees at a given depth

    Arguments
    ---------
    tree: either an nltk.tree.Tree or a PTB-formatted string
    depth: the target depth

    Returns
    -------
    list of nlt.tree.Tree objects representing the selected subtrees

    >>> ptb_str = "(ROOT (S (NP (DT The) (VBG following)) (VP (VBP are) (NP (NP (JJ major) (NN news) (NNS items)) (PP (IN in) (NP (NP (VBG leading) (JJ Turkish) (NNS newspapers)) (PP (IN on) (NP (NNP Monday))))))) (. .)))"
    >>> ptb_tree = Tree.fromstring(ptb_str)   
    >>> subtrees = find_subtrees(ptb_str, 2)  # find_subtrees accepts strings
    >>> [t.label() for t in subtrees]         # and it returns a list of subtrees (ojbects of the kind nlt.tree.Tree)
    ['NP', 'VP', '.']
    >>> subtrees = find_subtrees(ptb_tree, 3) # and trees
    >>> [t.label() for t in subtrees]
    ['DT', 'VBG', 'VBP', 'NP']
    >>> subtrees = find_subtrees(ptb_tree, 4) 
    >>> [t.label() for t in subtrees]
    ['NP', 'PP']
    """
    if isinstance(tree, str):
        tree = Tree.fromstring(tree)
    subtrees = []
    _find_subtrees(tree, 0, depth, subtrees)
    return subtrees


def dseqs(tree, depth=2, no_punc=True, lexicalised=False, child_phrase='leftmost', separator='*', backoff=['*']):
    """
    Returns d-sequences of a certain depth.
    
    Remarks
    -------

        * punctuation can be seen both at the leaves and labelling nodes, we deal with both cases
        * punctuation sometimes comes doubled or tripled (e.g. '' ``), we are dealing with it
        * sometimes we would return an empty list, that is why we have the `backoff` option (which is set by default preventing accidents)

    Arguments
    ---------
    tree: either an nltk.tree.Tree or a PTB-formatted string
    depth: the target depth
    no_punc: prevets punctuation (nodes or leaves)
    lexicalised: enables lexicalised patterns
    child_phrase: which child phrase is chosen to annotate the parent (choices: leftmost, rightmost, none)
    separator: string that separates the parent and the child pattern
    backoff: return backoff when no sequences can be produced

    Returns
    -------
    list of syntactic patterns

    >>> ptb_str = "(ROOT (S (NP (DT The) (VBG following)) (VP (VBP are) (NP (NP (JJ major) (NN news) (NNS items)) (PP (IN in) (NP (NP (VBG leading) (JJ Turkish) (NNS newspapers)) (PP (IN on) (NP (NNP Monday))))))) (. .)))"
    >>> dseqs(ptb_str, 2)
    ['NP*DT', 'VP*VBP']
    >>> dseqs(ptb_str, 2, no_punc=False)
    ['NP*DT', 'VP*VBP', '.']
    >>> dseqs(ptb_str, 2, no_punc=False, lexicalised=True)
    ['NP*DT', 'VP*VBP', '.*.']
    >>> dseqs(ptb_str, 2, child_phrase='rightmost')
    ['NP*VBG', 'VP*NP']
    >>> dseqs(ptb_str, 3)
    ['DT', 'VBG', 'VBP', 'NP*NP']
    >>> dseqs(ptb_str, 3, lexicalised=True)
    ['DT*The', 'VBG*following', 'VBP*are', 'NP*NP']
    >>> dseqs(ptb_str, 2, child_phrase='none')
    ['NP', 'VP']
    """
    # convert input to nlt.tree.Tree if str
    if isinstance(tree, str):
        tree = Tree.fromstring(tree)
    
    # deal with punctuation
    if no_punc:
        is_valid = lambda label: any(c not in string.punctuation for c in label)
    else:
        is_valid = lambda label: True

    # index of the child phrase to be selected
    if child_phrase == 'leftmost':
        get_child = lambda parent: parent[0]
    elif child_phrase == 'rightmost':
        get_child = lambda parent: parent[-1]
    elif child_phrase in ['none', '']:
        get_child = lambda parent: None
    else:
        raise ValueError('Unknown option for child_phrase=%s', child_phrase)

    # finds subtrees at given depth
    subtrees = find_subtrees(tree, depth)
    # gathers patterns
    patterns = []
    for parent in subtrees:
        # skip punctuation nodes if no_punc heuristic is enabled
        parent_label = parent.label()
        if no_punc and not is_valid(parent_label):
            continue

        # child node used in annotation
        child = get_child(parent)
        
        if child is None:  # child is being ignored
            patterns.append(parent_label)  
            continue
        
        child_label = None
        if isinstance(child, Tree):  # child is a node
            child_label = child.label()
        elif lexicalised:  # child is a leaf and we are lexicalising items
            child_label = child

        if child_label is None:  # child was not accepted
            patterns.append(parent_label)
            continue

        if is_valid(child_label):
            patterns.append('{0}*{1}'.format(parent_label, child_label))  # annotate with child's label
            
    return patterns if patterns else backoff 


def main(args):
    # reads in documents
    for trees, attrs in iterdoctext(args.input):
        # generator of d-sequences
        sequences = (dseqs(tree, 
                        depth=args.depth, 
                        no_punc=not args.punc, 
                        lexicalised=args.lexicalised, 
                        child_phrase=args.child, 
                        backoff=['*']) 
                    for tree in trees)
        # writes d-sequences
        writedoctext(args.output, 
                (' '.join(patterns) for patterns in sequences),
                **attrs)


@command('dseq', 'analysis')
def argparser(parser=None, func=main):
    if parser is None:
        parser = argparse.ArgumentParser(prog='dseq')
    parser.description = 'Extracts d-sequences of depth d from PTB annotated data'
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter

    parser.add_argument('input', nargs='?', 
            type=argparse.FileType('r'), default=sys.stdin,
            help='parsed corpus in doctext format')
    parser.add_argument('output', nargs='?', 
            type=argparse.FileType('w'), default=sys.stdout,
            help='d-sequences')
    parser.add_argument('--depth', '-d', type=int, default=2)
    parser.add_argument('--punc', '-p', action='store_true',
            help='allow punctuation')
    parser.add_argument('--lexicalised', '-l', action='store_true',
            help='allow lexicalised patterns')
    parser.add_argument('--child', '-c',
            choices=['leftmost', 'rightmost', 'none'], default='leftmost',
            help='annotate parent node with a child node')

    if func is not None:
        parser.set_defaults(func=func)

    return parser


if __name__ == '__main__':
    main(argparser().parse_args())


