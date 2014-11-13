# Preprocessing data

Some useful scripts.


## giga2docs.py

Extracts documents from LDC GigaWord files.
The input is a list of gzipped LDC files as in `ldc_files.txt`.


    cat ldc_files.txt | python ldc_gigaword.py data/preprocessed/2010 


this will produce an output like this:

    INFO Processing data/ldc/xin_eng_201011.gz
    INFO Processing data/ldc/xin_eng_201012.gz
    INFO xin_eng_201012 contains 5 documents
    INFO xin_eng_201011 contains 5 documents
    INFO Documents: 2
    | Corpus   |   Documents |
    |:---------|------------:|
    | xin_eng  |          10 |


Now `data/preprocessed/2010/sgml/` contains the files `xin_eng_201011.gz` and `xin_eng_201012.gz` each of which contains 5 documents.
A very simple sgml markup is used to preserve document boundaries.

# Markdown tables

I often use tabulate to dump markdown tables, you can easily install it with `pip`


    sudo pip install tabulate
