# Preprocessing data

Some useful scripts to preprocess LDC GigaWord data.

### List of LDC files

The typical input format for the scripts here contains paths to LDC files, one file per line:

``` text
data/ldc/xin_eng_201011.gz
data/ldc/xin_eng_201012.gz
# I am skipping the next file
#data/ldc/xon_eng_201001
```

Note you can use `#` to add comments or skip files.

## Utillitary tools

### docs.py

Extracts raw documents from LDC GigaWord files.
The input is a list of gziped LDC files as in `ldc_files.txt`.


    cat ldc_files.txt | python docs.py data/preprocessed/2010


this will produce an output like this:

    INFO Processing data/ldc/xin_eng_201011.gz
    INFO Processing data/ldc/xin_eng_201012.gz
    INFO xin_eng_201012 contains 5 documents
    INFO xin_eng_201011 contains 5 documents
    INFO Documents: 2
    | Corpus         |   Documents |
    |:---------------|------------:|
    | xin_eng_201011 |           5 |
    | xin_eng_201012 |           5 |


Now `data/preprocessed/2010/raw/` contains the files `xin_eng_201011.gz` and `xin_eng_201012.gz` each of which contains 5 documents.
Documents will be in `doctext` format, unless you use `--sgml` in which case you will get `docsgml`.


### parse.py

Parses documents within sgml-formatted files obtained by `docs.py`.
The input is again a list of gziped LDC files as in `ldc_files.txt`.
This time we also expect the output of `docs.py` to be available.


    cat ldc_files.txt | python parse.py data/preprocessed/2010 --mem 2


will parse documents within files in `data/preprocessed/2010/raw` (which correspond to LDC names in `ldc_files.txt`).
The following is an example run:

    INFO Distributing 2 jobs to 4 workers
    INFO Parsing document xin_eng_201011
    INFO parsing: xin_eng_201011
    INFO Parsing document xin_eng_201012
    INFO parsing: xin_eng_201012
    INFO running: java -mx2g -cp "/home/waziz/tools/discourse/DiscourseFramework.jar:/home/waziz/tools/stanford/stanford-corenlp-full-2014-10-31/stanford-corenlp-3.5.0.jar:/home/waziz/tools/stanford/stanford-corenlp-full-2014-10-31/stanford-corenlp-3.5.0-models.jar" nlp.framework.discourse.ParseTreeConverter
    INFO running: java -mx2g -cp "/home/waziz/tools/discourse/DiscourseFramework.jar:/home/waziz/tools/stanford/stanford-corenlp-full-2014-10-31/stanford-corenlp-3.5.0.jar:/home/waziz/tools/stanford/stanford-corenlp-full-2014-10-31/stanford-corenlp-3.5.0-models.jar" nlp.framework.discourse.ParseTreeConverter
    INFO done: xin_eng_201011 [22.708296 seconds]
    INFO done: xin_eng_201012 [26.485409 seconds]
    INFO Total time: 26.487720 seconds
    | Corpus         |   Time (s) |
    |:---------------|-----------:|
    | xin_eng_201011 |    22.7083 |
    | xin_eng_201012 |    26.4854 |


Now `data/preprocessed/2010/bsgml_trees` contains the parsed documents and `data/preprocessed/2010/log-parse` contains additional information from Stanford Parser.
The folder `bsgml_trees` contains badly sgml-formatted files. By mistake those files weren't true SGML files, they contain SGML-like tags, but the content of documents is not XML compliant. This will be fixed soon.

### sgml2txt.py

Converts the badly formatted sgml files produced by the Java wrapper to Stanford parser into *doctext* files.


### grid.py

Extracts Entity grids from parsed documents using the [*browncoherence*](http://cs.brown.edu/~melsner/manual.html) toolkit.
