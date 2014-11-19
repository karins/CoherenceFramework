import sys
from xml.dom import minidom

'''
Created on 3 Nov 2014

@author: Karin
'''


#retrieve counts from file and tally scores
#TODO: capture ones in MT which dont occur in HT at all

#takes path+filename, and file count, presumes filename has suffix count from 0
def compute_nonconsecutive_bigrams():
    allScores = {}
    for index in range(int(sys.argv[2])):
        print 'idx:'+str(index)
        print 'file: '+sys.argv[1]+str(index)
        print 'output file:'+sys.argv[2]
        all_scores = read_and_tally(open(sys.argv[1]+str(index), 'r'), allScores)
    
    output_results(all_scores, sys.argv[2])
    #compute_coherence(open(sys.argv[1]+str(index), 'r'), all_scores, 172)

def read_and_tally(f1, allScores):
    
    #read each line (stored as eg  NP*np VP*vbp), and increment counts .
    #store as [NP*np][NP*np][2]
    #         [NP*np][VP*vbp][1]
    
    previousTuples = []
    emptyString = ""
    #for 
    for line in f1:
        print 'line is '+line
        tuples = line.split()
        
        for tuple in tuples:
            
            print 'tuple is '+tuple
            #key is in dict and so is mapping
            if(allScores.has_key(tuple)== False):
                mapping = {}
                allScores[tuple] = mapping
            
                
            if(not previousTuples):#ie first sentence of doc
                if (emptyString in allScores[tuple]):
                    mapping = allScores[tuple]
                    count = mapping[emptyString]
                    count+=1
                    mapping[emptyString] = count
                elif (emptyString not in allScores[tuple]):
                    mapping = allScores[tuple]
                    mapping[emptyString] = 1
            else:
                #create a mapping from each item of this sentence to each item in last
                for previousItem in previousTuples:
                    print 'prevItem is '+previousItem
                    
                    if(previousItem in allScores[tuple]):
                        mapping = allScores[tuple]
                        count = mapping[previousItem]
                        count+=1
                        mapping[previousItem] = count
                    else:
                        mapping = allScores[tuple]
                        mapping[previousItem]=1
                                        
                print 'now='+str(len(allScores))
            
        previousTuples = tuples;
    
    return allScores


def compute_consecutive_bigrams():
    allScores = {}
    for index in range(int(sys.argv[2])):
        print 'idx:'+str(index)
        print 'file: '+sys.argv[1]+str(index)
        print 'output file:'+sys.argv[2]
        all_scores = count_bigrams(open(sys.argv[1]+str(index), 'r'), allScores)
    
    output_results(all_scores, sys.argv[2])

def count_bigrams(f1, allScores):
    
    #read each line (stored as eg  NP*np VP*vbp or NP*np , VP*vbz NP*np .), and increment counts .
    #store as [NP*np][NP*np][2]
    #         [NP*np][VP*vbp][1]
    
    #previousTuples = []
    previousItem = None
    emptyString = ""
    #for 
    for line in f1:
        print 'line is '+line
        tuples = line.split()
        
        for tuple in tuples:
            
            print 'tuple is '+tuple
            #key is in dict and so is mapping
            if(allScores.has_key(tuple)== False):
                mapping = {}
                allScores[tuple] = mapping
            
                
            if(previousItem is None ):#ie first sentence of doc
                if (emptyString in allScores[tuple]):
                    mapping = allScores[tuple]
                    count = mapping[emptyString]
                    count+=1
                    mapping[emptyString] = count
                elif (emptyString not in allScores[tuple]):
                    mapping = allScores[tuple]
                    mapping[emptyString] = 1
            else:
                #create a mapping from each item of this sentence to each item in last
                #for previousItem in previousTuples:
                print 'prevItem is '+previousItem
                    
                if(previousItem in allScores[tuple]):
                    mapping = allScores[tuple]
                    count = mapping[previousItem]
                    count+=1
                    mapping[previousItem] = count
                    print 'incrementing to '+str(count)
                else:
                    mapping = allScores[tuple]
                    mapping[previousItem]=1
                                    
            #print 'now='+str(len(allScores))
            #if(previousItem): print 'upating prev from '+previousItem +" to "+tuple
            previousItem = tuple;
    
    return allScores


def output_results(allScores, file):
    print 'results: '
    for item in allScores:
        #print item
        mappings = allScores[item]
        for key  in mappings:
            print item +' : '+key +' : '+str(mappings[key])
        

def get_unigrams(file):
    unigrams = {}
    #file format:
    #CONJP*rb      1 
    #WHNP*wp      18
    for line in file:
        print 'line='+line
        tuples =line.split()
        #for unigram in tuples:
        unigrams[tuples[0]] = tuples[1]
        print 'added '+tuples[0]+' : '+unigrams[tuples[0]]
            
    print 'returning '+str(len(unigrams))
    return unigrams
    
def get_bigrams(file):
    #file format:
    #NP-TMP*np :  : 3
    #NP-TMP*np : NP*prp : 2
    
    bigrams = {}
    for line in file:
        tuples =line.split(' : ')
        #for bigram in tuples:
        print 'mapping '+tuples[0]+' to '+tuples[1]+' with count '+tuples[2]
        #value =(tuples[1], tuples[2]) 
        bigrams[tuples[0]+':'+tuples[1]] = tuples[2]
        
    print 'returning '+str(len(bigrams))+' bigrams'
    return bigrams

def read_xml():
##xmldoc = minidom.parse(sys.argv[1]+str(index))
        xmldoc = minidom.parse(sys.argv[1])
        docs = xmldoc.getElementsByTagName('doc')
        print 'no. of docs= '+str(len(docs))
        for doc in docs:
            doc.childNodes[0].data
            

def get_bigram(prev_item,item, bigrams):
    if bigrams.has_key(item+':'+ prev_item):
        print 'get_bigram: '+item+':'+ prev_item+'->'+bigrams[item+':'+ prev_item]
        return float(bigrams[item+':'+ prev_item])               
    else:
        print item+':'+ prev_item+' not in map, return 0'
        return 0.0

def get_unigram(item,  unigrams):
    if unigrams.has_key(item):
        print 'get_unigram: '+item+'-> '+unigrams[item]
        return float(unigrams[item])
    else:
        print item+' not in map, return 0'
        return 0.0
    
def test(allScores):
    #"C:\\SMT\\datasets\\corpus-PE\\corpus\\output_graph\\PEofMT_2ndhalf.en.ptb.syntax_productions_annotated_rerun" 2
    
    results = allScores['NP*ex']
    #NP*ex : NP*prp : 1
    #NP*ex : NP*dt : 1
    #NP*ex : . : 3
    #NP*ex : VP*vbz : 2
    #NP*ex : NP*np : 1
    #NP*ex : ADVP*rb : 1
    #NP*ex : VP*vbp : 1
        
    
    #with direct bigrams:
    #NP*ex : CC : 1
    #NP*ex : . : 1
    #NP*ex : , : 1

#takes path+filename, and file count, presumes filename has suffix count from 0
compute_nonconsecutive_bigrams()
