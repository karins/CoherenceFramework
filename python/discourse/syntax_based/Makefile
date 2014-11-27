
# Rules

# 1) Potet corpus

# 1.1) gather files with syntactic patterns 
data/potet/patterns.files:
	ls -v data/potet/patterns/* > data/potet/patterns.files

# 1.2) make a doctext
data/potet/patterns.doctext: data/potet/patterns.files
	cat data/potet/patterns.files | python ../preprocessing/doctext.py > data/potet/patterns.doctext

# 2) A. Louis's model for syntax-based coherence

# 2.1) unigram and bigram counts as proposed by A. Louis
data/potet/patterns.alouis.bigrams: data/potet/patterns.doctext
	cat data/potet/patterns.doctext | PYTHONPATH=../preprocessing python alouis.py data/potet/patterns.alouis

# 2.2) a modified version of her model which includes document boundary tokens and insertion (via null trigger)
data/potet/patterns.mod_alouis.bigrams: data/potet/patterns.doctext
	cat data/potet/patterns.doctext | PYTHONPATH=../preprocessing python alouis.py --insertion --boundary data/potet/patterns.mod_alouis

# 2) IBM model 1 for syntax-based coherence

# 2.1) estimate a model
data/potet/patterns.ibm1: data/potet/patterns.doctext
	cat data/potet/patterns.doctext | PYTHONPATH=../preprocessing/ python ibm1.py -b -m 30 > data/potet/patterns.ibm1 2> data/potet/patterns.ibm1.log

# 2.2) decodes with the estimated model (TODO: use a test set)
data/potet/patterns.ibm1_probs: data/potet/patterns.ibm1
	cat data/potet/patterns.doctext | PYTHONPATH=../preprocessing/ python ibm1_decoder.py data/potet/patterns.ibm1 > data/potet/patterns.ibm1_probs


# Targets

potet: data/potet/patterns.doctext

ibm1: data/potet/patterns.ibm1 data/potet/patterns.ibm1_probs

alouis: data/potet/patterns.alouis.bigrams data/potet/patterns.mod_alouis.bigrams

.PHONY: clean
clean:
	-rm -fr data/potet/patterns.alouis*
	-rm -fr data/potet/patterns.mod_alouis*
	-rm -fr data/potet/patterns.ibm1*
