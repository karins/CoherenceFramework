# WMT13 data

## `docs`

Contains the documents in `doctext` format.

To convert from WMT's bad SGML format to doctext we used:

    python -m discourse.docsgml < sgml/newstest2013-src.de.sgml > docs/newstest2013-src.de

The original sgml files can be downloaded from WMT's site.

## `trees`

Contains the parsed documents. We used Stanford lexicalised PCG parser. 

To parse one file you can use:

    python -m discourse.preprocessing.parsedoctext data/wmt3/docs/newstest2013-src.de data/wmt3/trees/newstest2013-src.de --jobs 10

Note that `discourse.preprocessing.parsedoctext` wraps calls to Stanford parser. You might need to overwrite some of its command line arguments omitted here (e.g. path to Stanford parser, models and grammars).

To parse all of them you can write:

    for file in data/wmt3/docs/*; do python -m discourse.preprocessing.parsedoctext $file data/wmt3/trees/`basename $file` --jobs 10; done
