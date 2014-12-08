# Corpora

* Potet 

              |  fr-en 
    :---------|-------:
    systems   |  1    
    references|  1
    docs      |  361    
    sentences |  10755

            "Marion Potet, Emmanuelle Esperança-rodier, Laurent Besacier, Hervé Blanchon.(2012). Collection of a Large Database of French-English SMT Output Corrections. Proceedings of the 8th International Conference on Language Resources and Evaluation (LREC), Istanbul (Turkey), 23-25 May 2012."

            @INPROCEEDINGS{Potet12,
            AUTHOR= "Marion Potet and Emmanuelle Esperança-rodier and Laurent Besacier and Hervé Blanchon",
            TITLE= "Collection of a Large Database of French-English SMT Output Corrections",
            YEAR = {2012},
            PAGES= {33--50},
            BOOKTITLE={8th International Conference on Language Resources and Evaluation (LREC)},
            MONTH={May}
            }

* WMT13's *newstest2013*

              |  de-en | fr-en  | ru-en
    :---------|-------:|-------:|--------:
    systems   |  23    | 19     | 23
    references|  1     | 1      | 1
    docs      |  52    | 52     | 52
    sentences |  3000  | 3000   | 3000

* WMT14's *newstest2014*

              |  de-en | fr-en  | ru-en
    :---------|-------:|-------:|--------:
    systems   |  13    | 8      | 13
    references|  1     | 1      | 1
    docs      |  164   | 176    | 175
    sentences |  3003  | 3003   | 3003

## sgml

Contains the documents in (proper) `sgml` format, that is, using valid XML files (unlike WMT's).

To convert from WMT's bad SGML format we used:

    python -m discotools preprocessing fixwmt --sgml < bad-sgml/newstest2013.de-en.en.sgml > sgml/newstest2013.de-en.ref


## docs

Contains the documents in `doctext` format.

To convert from WMT's bad SGML format to doctext we used:

    python -m discotools preprocessing fixwmt < bad-sgml/newstest2013.de-en.en.sgml > docs/newstest2013.de-en.ref


The original sgml files can be downloaded from WMT's site.

To convert all of them you can run:

    for file in wmt14-data/sgm/system-outputs/newstest2014/de-en/*; do echo $file; python -m discotools preprocessing fixwmt < $file > docs/`basename $file .sgm`; done


## trees

Contains the parsed documents. We used Stanford lexicalised PCG parser. 

To parse one file you can use:

    python -m discotools analysis parsedocs docs/newstest2013.de-en.ref trees/newstest2013.de-en.ref --jobs 10

Note that `discourse.preprocessing.parsedoctext` wraps calls to Stanford parser. You might need to overwrite some of its command line arguments omitted here (e.g. path to Stanford parser, models and grammars).

To parse all of them you can write:

    for file in docs/*; do python -m discotools analysis parsedocs $file trees/`basename $file` --jobs 10; done

## grids

Entity grids.
