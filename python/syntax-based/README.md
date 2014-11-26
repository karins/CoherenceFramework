# Syntax-based coherence

We are investigating models inspired by

> [Annie Louis and Ani Nenkova, A coherence model based on syntactic patterns, Proceedings of EMNLP-CoNLL, 2012.](http://www.aclweb.org/anthology/D/D12/D12-1106.pdf)

in the context of SMT.

# Requirements

Add `preprocessing` to your `PYTHONPATH`.


# Optional

* install `progressbar` from Google code for improved feedback

```bash
wget https://python-progressbar.googlecode.com/files/progressbar-2.3.tar.gz
tar -xzvf progressbar-2.3.tar.gz
cd progressbar-2.3
sudo python setup.py install --record files.txt
```


# A. Louis's model for syntax-based coherence

This produces unigram and bigram counts as proposed by Annie Louis.

    cat data/potet/patterns.doctext | PYTHONPATH=../preprocessing python alouis.py data/potet/patterns.alouis

A modified version which includes document boundary tokens and insertion counts (null trigger) can also be obtained:

    cat data/potet/patterns.doctext | PYTHONPATH=../preprocessing python alouis.py --insertion --boundary data/potet/patterns.mod_alouis

# IBM1 for syntax-based coherence

This estimates a distribution `t(pattern|trigger)` from a collection of documents, where (trigger, pattern) is a pair of syntactic patterns occurring in adjacent sentences:

    cat data/potet/patterns.doctext | PYTHONPATH=../preprocessing python ibm1.py -b -m 20 > data/potet/patterns.ibm1.20
