import gzip
import sys
import argparse
import logging
import traceback
import os
import re
from itertools import izip
from collections import defaultdict
from functools import partial
from multiprocessing import Pool
import shlex
import subprocess
import xml.parsers.expat
from xml.dom.minidom import getDOMImplementation

# some stuff for parsing XML files
documents = []
filename = None
docid = None
current_doc = None
current_text = None
reading_text = False

# regex to decompose LDC file names
ldc_name_re = re.compile('([a-z]+)_([a-z]+)_([0-9]{4})([0-9]{2})')

# XML parsing methods

def start_element(name, attrs):
    """starts a document"""
    global current_doc, docid, reading_text
    if name == 'DOC':
        current_doc = []
        docid = attrs['id']
    elif name == 'TEXT':
        reading_text = True


def end_element(name):
    """ends a document"""
    global current_doc, docid
    if name == 'DOC':
        documents.append((docid, current_doc))
        current_doc = None
        docid = None
    elif name == 'TEXT':
        reading_text = False

def char_data(data):
    """stores non blank lines in a document"""
    global reading_text
    if reading_text:
        # encode utf-8 into a python string
        line = data.encode('utf-8').strip()
        if line:
            current_doc.append(line)

def get_file_stem(sgml_gz):
    """returns the name of the file without the parent directory and without extension"""
    return os.path.splitext(os.path.basename(sgml_gz))[0]

def parse_ldc_name(sgml_gz):
    """parse LDC file name, returns a dictionary with info"""
    stem = get_file_stem(sgml_gz)
    corpus, lang, year, month = ldc_name_re.match(stem).groups()
    return {'corpus':corpus, 'language':lang, 'year':year, 'month':month}

def iter_docs(sgml_gz):
    """Iterates over documents in a given file sgm file -> {'id':doc_id, 'data':doc_sentences}"""
    parser = xml.parsers.expat.ParserCreate()

    parser.StartElementHandler = start_element
    parser.EndElementHandler = end_element
    parser.CharacterDataHandler = char_data
    with gzip.open(sgml_gz, 'rb') as fi:
        content = fi.read()
        # the <sgml> tags are added to make sure the file has a single root
        parser.Parse('<sgml>{0}</sgml>'.format(content), 1)
        for did, doc in documents:
            yield {'id': did, 'text':'\n'.join(seg for seg in doc)}


def extract_and_save(sgml_gz, args):
    """Extracts documents from a gzipped sgml file -> file ids"""
    try:
        ids = []
        n = 0
        logging.info('Processing %s', sgml_gz)
        stem = get_file_stem(sgml_gz)
        dom = getDOMImplementation()
        sgml_docs = dom.createDocument(None, 'docs', None)
        sgml_docs.documentElement.setAttribute('file', stem)
        for doc in iter_docs(sgml_gz):
            if doc['text']:
                ids.append(doc['id'])
                sgml_doc = sgml_docs.createElement('doc')
                sgml_doc.setAttribute('id', doc['id'])
                # decode python strings into utf-8
                sgml_doc.appendChild(sgml_docs.createTextNode(doc['text'].decode('utf-8')))
                sgml_docs.documentElement.appendChild(sgml_doc)
        with gzip.open('{0}/sgml/{1}.gz'.format(args.workspace, stem), 'wb') as fout:
            # returns utf-8 encoded into python string
            fout.write(sgml_docs.toprettyxml(encoding='utf-8'))
        logging.info(' %d documents', len(ids))
        return ids
    except:
        raise Exception(''.join(traceback.format_exception(*sys.exc_info())))

def make_workspace(workspace):
    if not os.path.exists(workspace):
        os.makedirs(workspace)
        os.makedirs(workspace + '/sgml')
        #os.makedirs(workspace + '/parse')
        #os.makedirs(workspace + '/txt')
        #os.makedirs(workspace + '/log')

def parse_command_line():
    parser = argparse.ArgumentParser(description='Extracts documents from LDC GigaWord data',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('workspace', type=str,
            help='where output files will be stored')
    parser.add_argument('--jobs', '-j', type=int, default=4,
            help='number of jobs')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
    make_workspace(args.workspace)

    return args

def main(args):
    files = [path.strip() for path in sys.stdin]

    pool = Pool(args.jobs)
    results = pool.map(partial(extract_and_save, args=args), files)
    logging.info('Documents: %d', len(results))

    data = defaultdict(list)
    n_documents = defaultdict(int)
    
    for sgml_gz, ids in izip(files, results):
        ldc_info = parse_ldc_name(sgml_gz)
        n_documents['{0}_{1}'.format(ldc_info['corpus'], ldc_info['language'])] += len(ids)

    try:
        # prints a Markdown table if possible
        from tabulate import tabulate
        print tabulate(sorted(n_documents.iteritems(), key=lambda (c, n): n),
                headers=['Corpus', 'Documents'],
                tablefmt='pipe')
    except:
        # plain table otherwise
        for corpus, n_docs in sorted(n_documents.iteritems(), key=lambda (c, n): n):
            print corpus, ndocs


if __name__ == '__main__':
    main(parse_command_line())

