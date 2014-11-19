ARCH_NAME = $(shell uname -m)
ifeq (${ARCH_NAME}, x86_64)
ARCH = 64
else
ARCH = 32
endif

ifeq (${ARCH}, 64)
GSLINCLUDE = -I /usr/include/gsl
GSLLIBS = -L /usr/lib/gsl -lgsl -lgslcblas
else
GSLINCLUDE = -I /usr/include/gsl
GSLLIBS = -L /usr/lib/gsl -lgsl -lgslcblas
endif
GSLINCLUDE := ${GSLINCLUDE} -DHAVE_INLINE -DGSL_RANGE_CHECK_OFF

ifeq (${ARCH}, 64)
LIB = lib64
BIN = bin64
else
LIB = lib32
BIN = bin32
endif

ifeq (${ARCH}, 64)
WNDIR = /usr/local/WordNet-3.0
WNINCLUDE = -idirafter$(WNDIR)/include -DUSE_WORDNET
WNLIBS = -L$(WNDIR)/lib -lWN
else
WNDIR = /usr/local/WordNet-3.0
WNINCLUDE = -idirafter$(WNDIR)/include -DUSE_WORDNET
WNLIBS = -L$(WNDIR)/lib -lWN
endif

#if you want WORDNET, set WORDNET = 1, otherwise set WORDNET = 
WORDNET = 1
ifeq ($(strip $(WORDNET)),)
WNINCLUDE =
WNLIBS =
endif

BOOST_LIBS = -lboost_iostreams

WARNINGS = -Woverloaded-virtual -Wall -Wno-sign-compare

CFLAGS = $(WARNINGS) -Iinclude $(WNINCLUDE) $(TAO_PETSC_INCLUDE) $(GSLINCLUDE)
LIBFLAGS = $(GSLLIBS) $(WNLIBS) $(TAO_PETSC_LIBS) $(BOOST_LIBS)
#OPTFLAGS = -g # -pg
OPTFLAGS = -O3

vpath %.h include
vpath %.cc src
#vpath %.o lib

LIBS = \
	$(LIB)/Tree.o \
	$(LIB)/headFinder.o \
	$(LIB)/ntInfo.o \
	$(LIB)/setLabs.o \
	$(LIB)/treeInfo.o \
	$(LIB)/common.o \
	$(LIB)/Inserter.o \
	$(LIB)/DialogueInserter.o \
	$(LIB)/Disentangler.o \
	$(LIB)/MultiwayDisentangler.o \
	$(LIB)/Vocab.o \
	$(LIB)/NP.o \
	$(LIB)/Sent.o \
	$(LIB)/Document.o \
	$(LIB)/Transcript.o \
	$(LIB)/MaxEntSelection.o \
	$(LIB)/OWLQN.o \
	$(LIB)/TerminationCriterion.o \
	$(LIB)/CoherenceModel.o \
	$(LIB)/JointModel.o \
	$(LIB)/MixtureModel.o \
	$(LIB)/FeatureSet.o \
	$(LIB)/DiscSyntaxConditional.o \
	$(LIB)/NewEntityModel.o \
	$(LIB)/EGridModel.o \
	$(LIB)/NaiveEGrid.o \
	$(LIB)/NaiveMaxEntEGrid.o \
	$(LIB)/NaiveMaxEntEGridT.o \
	$(LIB)/NaiveMaxEntEGridF.o \
	$(LIB)/PronounModel.o \
	$(LIB)/PronounHandler.o \
	$(LIB)/TimeModel.o \
	$(LIB)/SpeakerModel.o \
	$(LIB)/MentionModel.o \
	$(LIB)/ge.o \
	$(LIB)/stripTree.o \
	$(LIB)/IBM.o \
	$(LIB)/TopicIBM.o \
	$(LIB)/ECIBM.o \
	$(LIB)/PronounIBM.o \
	$(LIB)/WordIBM.o \
	$(LIB)/digamma.o \
	$(LIB)/LDA.o
.SUFFIXES : 
.PRECIOUS : $(LIB)/%.o

something :
	@echo "Try the name of a specific program, or 'make everything'."

everything: TestSent TestGrid ExtractGrid Train TrainOnThreads Insert TrainMixture TrainDiscMixture TrainWSJDiscMixture Featurize TrainFromFeatures Average DiscriminateRand Discriminate DiscriminateDiscRand RankDisentangle TestDisentangle ChatStyleTranscript Print

$(LIB)/%.o : %.cc %.h
	g++ $(CFLAGS) $(OPTFLAGS) -c -o $@ $<

$(LIB)/%.o : %.cc
	g++ $(CFLAGS) $(OPTFLAGS) -c -o $@ $<

% : $(LIB)/%.o $(LIBS)
	g++ $(OPTFLAGS) -o $(BIN)/$@ $^ $(CFLAGS) $(LIBFLAGS)

.PHONY : clean

clean:
	-rm $(LIB)/*
	-rm $(BIN)/*
