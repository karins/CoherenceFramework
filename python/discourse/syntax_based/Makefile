# Rules

# 1) Prepare workspace

dirs:
	@mkdir -p build/ibm1/dseq2
	@mkdir -p build/ibm1/dseq2/eval/de-en
	@mkdir -p build/ibm1/dseq2/eval/fr-en
	@mkdir -p build/ibm1/dseq2/eval/ru-en

# 2) IBM model 1 for syntax-based coherence

build/ibm1/dseq2/potet.params: data/potet/dseq2.doctext | dirs
	cat $< | python -m discourse.syntax_based.ibm1 -b -m 30 > $@ 2> $@.log

# 3) Gathers the dseq2 files for the WMT14 data

build/ibm1/dseq2/wmt14.de-en.files: | dirs
	ls data/wmt14/dseq2/doctext/de-en.* > $@

build/ibm1/dseq2/wmt14.fr-en.files: | dirs
	ls data/wmt14/dseq2/doctext/fr-en.* > $@

build/ibm1/dseq2/wmt14.ru-en.files: | dirs
	ls data/wmt14/dseq2/doctext/ru-en.* > $@

# 4) Evaluate IBM models

# no special normalisation 

build/ibm1/dseq2/eval/de-en.rankings: | dirs
	cat build/ibm1/dseq2/wmt14.de-en.files | python -m discourse.syntax_based.compare build/ibm1/dseq2/eval/de-en --args "build/ibm1/dseq2/potet.params" $@ > build/ibm1/dseq2/eval/de-en.summary

build/ibm1/dseq2/eval/fr-en.rankings: | dirs
	cat build/ibm1/dseq2/wmt14.fr-en.files | python -m discourse.syntax_based.compare build/ibm1/dseq2/eval/fr-en --args "build/ibm1/dseq2/potet.params" $@ > build/ibm1/dseq2/eval/fr-en.summary

build/ibm1/dseq2/eval/ru-en.rankings: | dirs
	cat build/ibm1/dseq2/wmt14.ru-en.files | python -m discourse.syntax_based.compare build/ibm1/dseq2/eval/ru-en --args "build/ibm1/dseq2/potet.params" $@ > build/ibm1/dseq2/eval/ru-en.summary

# normalised by number of sentences

build/ibm1/dseq2/eval/de-en.rankings.snorm: | dirs
	cat build/ibm1/dseq2/wmt14.de-en.files | python -m discourse.syntax_based.compare build/ibm1/dseq2/eval/de-en --args "build/ibm1/dseq2/potet.params" --column 3 --exp snorm $@ > build/ibm1/dseq2/eval/de-en.summary.snorm

build/ibm1/dseq2/eval/fr-en.rankings.snorm: | dirs
	cat build/ibm1/dseq2/wmt14.fr-en.files | python -m discourse.syntax_based.compare build/ibm1/dseq2/eval/fr-en --args "build/ibm1/dseq2/potet.params" --column 3 --exp snorm $@ > build/ibm1/dseq2/eval/fr-en.summary.snorm

build/ibm1/dseq2/eval/ru-en.rankings.snorm: | dirs
	cat build/ibm1/dseq2/wmt14.ru-en.files | python -m discourse.syntax_based.compare build/ibm1/dseq2/eval/ru-en --args "build/ibm1/dseq2/potet.params" --column 3 --exp snorm $@ > build/ibm1/dseq2/eval/ru-en.summary.snorm

# normalised by number of patterns

build/ibm1/dseq2/eval/de-en.rankings.pnorm: | dirs
	cat build/ibm1/dseq2/wmt14.de-en.files | python -m discourse.syntax_based.compare build/ibm1/dseq2/eval/de-en --args "build/ibm1/dseq2/potet.params" --column 5 --exp pnorm $@ > build/ibm1/dseq2/eval/de-en.summary.pnorm

build/ibm1/dseq2/eval/fr-en.rankings.pnorm: | dirs
	cat build/ibm1/dseq2/wmt14.fr-en.files | python -m discourse.syntax_based.compare build/ibm1/dseq2/eval/fr-en --args "build/ibm1/dseq2/potet.params" --column 5 --exp pnorm $@ > build/ibm1/dseq2/eval/fr-en.summary.pnorm

build/ibm1/dseq2/eval/ru-en.rankings.pnorm: | dirs
	cat build/ibm1/dseq2/wmt14.ru-en.files | python -m discourse.syntax_based.compare build/ibm1/dseq2/eval/ru-en --args "build/ibm1/dseq2/potet.params" --column 5 --exp pnorm $@ > build/ibm1/dseq2/eval/ru-en.summary.pnorm
# 2.2) decodes with the estimated model (TODO: use a test set)
#data/potet/patterns.ibm1_probs: data/potet/patterns.ibm1 
#	cat data/potet/patterns.doctext | python -m discourse.syntax_based.ibm1_decoder data/potet/patterns.ibm1 > data/potet/patterns.ibm1_probs


# Targets


ibm1: build/ibm1/dseq2/potet.params

wmt14: build/ibm1/dseq2/wmt14.de-en.files build/ibm1/dseq2/wmt14.fr-en.files build/ibm1/dseq2/wmt14.ru-en.files

rankings: build/ibm1/dseq2/eval/de-en.rankings build/ibm1/dseq2/eval/fr-en.rankings build/ibm1/dseq2/eval/ru-en.rankings \
	build/ibm1/dseq2/eval/de-en.rankings.snorm build/ibm1/dseq2/eval/fr-en.rankings.snorm build/ibm1/dseq2/eval/ru-en.rankings.snorm \
	build/ibm1/dseq2/eval/de-en.rankings.pnorm build/ibm1/dseq2/eval/fr-en.rankings.pnorm build/ibm1/dseq2/eval/ru-en.rankings.pnorm 


#alouis: data/potet/patterns.alouis.bigrams data/potet/patterns.mod_alouis.bigrams

.PHONY: clean
clean:
	-rm -fr data/potet/patterns.alouis*
	-rm -fr data/potet/patterns.mod_alouis*
	-rm -fr data/potet/patterns.ibm1*


# 2) A. Louis's model for syntax-based coherence

# 2.1) unigram and bigram counts as proposed by A. Louis
#data/potet/patterns.alouis.bigrams: data/potet/patterns.doctext
#	cat data/potet/patterns.doctext | python -m discourse.syntax_based.alouis data/potet/patterns.alouis

# 2.2) a modified version of her model which includes document boundary tokens and insertion (via null trigger)
#data/potet/patterns.mod_alouis.bigrams: data/potet/patterns.doctext
#	cat data/potet/patterns.doctext | python -m discourse.syntax_based.alouis --insertion --boundary data/potet/patterns.mod_alouis

