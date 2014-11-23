"""
This module gets the text content of documents out of LDC GigaWord files.
LDC files come with a bunch of information, we are only interested in the content under <TEXT>,
this modules helps get that.

@author waziz
"""

import gzip
import sys
import argparse
import logging
import traceback
import os
from functools import partial
from multiprocessing import Pool
from docsgml import TextFromSGML, MakeSGMLDocs
from ldc import get_ldc_name
from doctext import writedoctext


def extract_and_save_sgml(sgml_gz, args):
    """Extracts documents from a gzipped sgml file -> file ids"""
    try:
        ids = []
        n = 0
        logging.info('Processing %s', sgml_gz)
        stem = get_ldc_name(sgml_gz)
        with gzip.open(sgml_gz, 'rb') as fi:
            sgmler = MakeSGMLDocs(file=stem)
            parser = TextFromSGML(fi.read(), text_under='text', root='sgml')
            for doc in parser.iterdocs():
                if doc['text']:
                    ids.append(doc['id'])
                    sgmler.add(doc['text'], id=doc['id'])
            sgmler.writegz('{0}/raw/{1}'.format(args.workspace, stem))
            logging.info('%s contains %d documents', stem, len(ids))
        return ids
    except:
        raise Exception(''.join(traceback.format_exception(*sys.exc_info())))

def extract_and_save_txt(sgml_gz, args):
    """Extracts documents from a gzipped sgml file -> file ids"""
    try:
        ids = []
        n = 0
        logging.info('Processing %s', sgml_gz)
        stem = get_ldc_name(sgml_gz)
        with gzip.open(sgml_gz, 'rb') as fi:
            with gzip.open('{0}/raw/{1}.gz'.format(args.workspace, stem), 'wb') as fo:
                parser = TextFromSGML(fi.read(), text_under='text', root='sgml')
                for doc in parser.iterdocs():
                    if doc['text']:
                        ids.append(doc['id'])
                        writedoctext(fo, doc['text'].split('\n'), id=doc['id'])
                logging.info('%s contains %d documents', stem, len(ids))
        return ids
    except:
        raise Exception(''.join(traceback.format_exception(*sys.exc_info())))


def make_workspace(workspace):
    if not os.path.exists(workspace + '/raw'):
        os.makedirs(workspace + '/raw')


def parse_command_line():
    parser = argparse.ArgumentParser(description='Extracts documents from LDC GigaWord data',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('workspace', type=str,
            help='where output files will be stored')
    parser.add_argument('--jobs', '-j', type=int, default=4,
            help='number of jobs')
    parser.add_argument('--sgml', 
            action='store_true',
            help='output SGML files')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
    make_workspace(args.workspace)

    return args


def main(args):
    files = [path.strip() for path in sys.stdin if not path.startswith('#')]
    ldc_names = [get_ldc_name(path) for path in files]

    pool = Pool(args.jobs)
    if args.sgml:
        results = pool.map(partial(extract_and_save_sgml, args=args), files)
    else:
        results = pool.map(partial(extract_and_save_txt, args=args), files)
    logging.info('Documents: %d', len(results))

    data = zip(ldc_names, (len(ids) for ids in results))

    try:
        # prints a Markdown table if possible
        from tabulate import tabulate
        print tabulate(data,
                headers=['Corpus', 'Documents'],
                tablefmt='pipe')
    except:
        # plain table otherwise
        print '\n'.join('{0} {1}'.format(c, n) for c, n in data)


if __name__ == '__main__':
    main(parse_command_line())

