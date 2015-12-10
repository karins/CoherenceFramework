"""
This module is the main interface to the programs in this package.

@author: wilkeraziz
"""

import argparse
from discourse import itercommands, iterclasses


def importall():
    """Import modules which contain commands"""
    import discourse.docsgml
    import discourse.doctext
    import discourse.preprocessing.parsedoctext
    import discourse.rankings
    import discourse.entity_based.grid
    import discourse.entity_based.grid_decoder
    import discourse.syntax_based.dseq
    import discourse.syntax_based.ibm1
    import discourse.syntax_based.ibm1_decoder
    import discourse.syntax_based.alouis
    import discourse.syntax_based.alouis_decoder
    import corpus.corpus_pipeline
    

def configure_commands(cls, parser):
    subparsers = parser.add_subparsers(title='subcommands',
            dest='subparser_name', 
            help='additional help')

    for prog_name, prog_parser in sorted(itercommands(cls), key=lambda (n, c): n):
        prog_parser(subparsers.add_parser(prog_name))


def parse_args():
    parser = argparse.ArgumentParser(prog='discotools',
            description="Discourse tools for MT (MODIST)")

    subparsers = parser.add_subparsers(title='subcommands',
            dest='subparser_name', 
            help='additional help')

    importall()

    for cls in sorted(iterclasses()):
        subparser = subparsers.add_parser(cls)
        configure_commands(cls, subparser)
    

    args = parser.parse_args()
    args.func(args)

    return args


if __name__ == '__main__':
    parse_args()
