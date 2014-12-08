"""
This module implements helper functions to deal with multiple documents stored in a single plain text file.

Not to lose document boundaries we use a very simple format:
    1) the header of a document is its first line, it starts with '#' 
    and contains space sparated key-value pairs
    keys and values are strings without quotes

    2) a document only contains non-empty lines

    3) an empty line separates adjacent documents

Example:

# id=doc1
This is a doc.
It has two sentences.

# id=doc2
This is another, this one has a single sentence.

@author: wilkeraziz
"""
from itertools import ifilter
from discourse import command


def writedoctext(ostream, lines, **kwargs):
    """
    Dumps a document (this function never writes empty lines within the document)
    :param ostream: where we are printing to
    :param lines: list of sentences in the document
    :param **kwargs: attributes of the document
    """
    attr_str = ' '.join('{0}={1}'.format(k, v) for k, v in kwargs.iteritems())
    print >> ostream, '# %s' % attr_str
    for line in ifilter(lambda x: x.strip(), lines):
        print >> ostream, line
    print >> ostream


def iterdoctext(istream):
    """
    Iterates over documents
    :param istream: where we are reading from
    :yields: a tuple containing the content of the document (as a list of lines) and the attributes of the document (as a dictionary)
    """
    doc = None
    for line in istream:
        line = line.strip()
        if doc is None:
            if line.startswith('#'):
                line = line.replace('#', '')
                doc = {'attrs': {k:v for k, v in [kv.split('=') for kv in line.split()]},
                        'lines': []}
        else:
            if line:
                doc['lines'].append(line)
            else:
                yield doc['lines'], doc['attrs']
                doc = None

    if doc is not None:
        yield doc['lines'], doc['attrs']


def iteraddheader(istream):
    """
    Iterates over documents adding headers
    :param istream: where we are reading from
    :yields documents line by line, including starting header and empty line separating documents 
    Chain it with `iterdoctext` to read documents from a file which misses headers:

    >>> import sys
    >>> stream = 'a b c'.split() + [''] + 'd e f'.split()
    >>> _ = [writedoctext(sys.stdout, doc, **attrs) for doc, attrs in iterdoctext(iteraddheader(stream))]
    # id=0
    a
    b
    c
    <BLANKLINE>
    # id=1
    d
    e
    f
    <BLANKLINE>
    >>> stream = 'a b c'.split() + [''] + 'd e f'.split() + ['']
    >>> _ = [writedoctext(sys.stdout, doc, **attrs) for doc, attrs in iterdoctext(iteraddheader(stream))]
    # id=0
    a
    b
    c
    <BLANKLINE>
    # id=1
    d
    e
    f
    <BLANKLINE>
    """
    
    first = True
    n = 0
    for line in istream:
        if first:
            yield '# id={0}'.format(n)
            first = False
            n += 1
        elif not line.strip():
            first = True
        yield line


def main(args):
    """
    Use this to convert a list of documents (one document per file) into a single doctext
    """
    import sys
    import os
    
    if not args.add_header:
        # in this mode the input is a list of files (1 document per file)
        files = [path.strip() for path in args.input if not path.startswith('#')]
        for path in files:
            doc_name = os.path.basename(path)
            with open(path) as fi:
                lines = [line.strip() for line in fi]
                writedoctext(args.output, lines, id=doc_name)
    else:
        # in this mode the input is a stream of documents separated by 1 empty line (to be a doctext file, documents need an added header)
        for content, attrs in iterdoctext(iteraddheader(args.input)):
            writedoctext(args.output, content, **attrs)


@command('doctext', 'preprocessing')
def argparser(parser=None, func=main):
    """parse command line arguments"""
    import argparse
    import sys

    if parser is None:
        parser = argparse.ArgumentParser(prog='doctext')
    
    parser.description = 'Create doctext files'

    parser.add_argument('input', nargs='?', 
            type=argparse.FileType('r'), default=sys.stdin,
            help='list of files or (see --add-header)')
    parser.add_argument('output', nargs='?', 
            type=argparse.FileType('w'), default=sys.stdout,
            help='doctext file containing all documents')
    parser.add_argument('--add-header', '-a',
            action='store_true',
            help='switches to a different mode in which the input is seen as a container of documents, separated by 1 empty line (as in doctext), but missing a header')

    if func is not None:
        parser.set_defaults(func=func)
        
    return parser


if __name__ == '__main__':
    main(argparser().parse_args())
