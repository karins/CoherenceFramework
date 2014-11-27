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

@author waziz
"""
from itertools import ifilter

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


def main():
    """Use this to convert a list of documents (one document per file) into a single doctext"""
    import sys
    import os
    
    if len(sys.argv) > 1:
        print >> sys.stderr, 'python -m discourse.doctext < corpus.files > corpus.doctext'
        sys.exit(0)

    files = [path.strip() for path in sys.stdin if not path.startswith('#')]
    for path in files:
        doc_name = os.path.basename(path)
        with open(path) as fi:
            lines = [line.strip() for line in fi]
            writedoctext(sys.stdout, lines, id=doc_name)

if __name__ == '__main__':
    main()

