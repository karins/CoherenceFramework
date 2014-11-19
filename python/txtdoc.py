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

def writetxtdoc(ostream, lines, **kwargs):
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

def itertxtdocs(istream):
    """
    Iterates over documents
    :param istream: where we are reading from
    :yields: a dictionary containing the attributes of the document ('attrs'), as a dictionary itself, and the sentences ('lines') as a list.
    """
    attrs = None
    content = None
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
                yield doc
                doc = None

    if doc is not None:
        yield doc
