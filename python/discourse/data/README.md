# Corpora

* Potet 

            "Marion Potet, Emmanuelle Esperança-rodier, Laurent Besacier, Hervé Blanchon.(2012). Collection of a Large Database of French-English SMT Output Corrections. Proceedings of the 8th International Conference on Language Resources and Evaluation (LREC), Istanbul (Turkey), 23-25 May 2012."

            @INPROCEEDINGS{Potet12,
            AUTHOR= "Marion Potet and Emmanuelle Esperança-rodier and Laurent Besacier and Hervé Blanchon",
            TITLE= "Collection of a Large Database of French-English SMT Output Corrections",
            YEAR = {2012},
            PAGES= {33--50},
            BOOKTITLE={8th International Conference on Language Resources and Evaluation (LREC)},
            MONTH={May}
            }

* WMT13

* WMT14

## `docs`

Contains the documents in `doctext` format.

To convert from WMT's bad SGML format to doctext we used:

    python -m discourse.docsgml < sgml/newstest2013-src.de.sgml > docs/newstest2013-src.de

The original sgml files can be downloaded from WMT's site.

To convert all of them you can run:

    for file in wmt14-data/sgm/system-outputs/newstest2014/de-en/*; do echo $file; python -m discourse.docsgml < $file > data/wmt14/docs/`basename $file .sgm`; done

## `trees`

Contains the parsed documents. We used Stanford lexicalised PCG parser. 

To parse one file you can use:

    python -m discourse.preprocessing.parsedoctext data/docs/newstest2013-src.de data/trees/newstest2013-src.de --jobs 10

Note that `discourse.preprocessing.parsedoctext` wraps calls to Stanford parser. You might need to overwrite some of its command line arguments omitted here (e.g. path to Stanford parser, models and grammars).

To parse all of them you can write:

    for file in data/docs/*; do python -m discourse.preprocessing.parsedoctext $file data/trees/`basename $file` --jobs 10; done
