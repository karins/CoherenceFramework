'''
Created on 12 Jan 2015
 
 Constructs an entity grid from a given file containing ptb trees. The file may be English, French or German.
 The entity grid uses the Stanford Parser to identify all nouns in the input text.
 For the English version it additionally determines the grammatical role played by that entity in each particular occurance. 
 The various options are set on the commandline, to ensure correct parser is set.
 
 @author Karin Sim

'''
import argparse
import sys
import traceback
import logging
import gzip
from grid import r2i, i2r
import StanfordDependencies
import numpy as np
from discourse.doctext import iterdoctext, writedoctext
from discourse.util import smart_open, read_documents
from collections import defaultdict

nouns = ['NNP', 'NP','NNS','NN','N','NE']

''' csubj,  
    csubjpass, {xsubj}: controlling subject}, 
    subj,  
    nsubj (nominal subject), 
    nsubjpass
    '''
subject =[ 'csubj', 'csubjpass','subj','nsubj','nsubjpass']

''' pobj (object of a preposition) 
    also dobj ( direct object) 
    and iobj ( indirect object )'''
object= ["pobj","dobj","iobj"] 



def open_file(path):
    if path.endswith('.gz'):
        return gzip.open(path)
    else:
        return open(path)
        
# input is in form of ptb trees. 
def main(args):
    """ Extract entities and construct grid """
    try:
        #for ipath in enumerate(ipaths): 
        #with gzip.open(input_path, 'rb') as fi:
        with open(args.directory, 'rb' ) as fi:
            #with gzip.open(input_path+'_grid' + '.gz', 'wb') as fo:
            with open(args.directory+'_grid', 'w') as fo:
                entities, sentences = extract_grids(fi)
                grid = construct_grid(entities, sentences)
                output_grid(grid, fo) 
                #writedoctext(fo, grid , id=attrs['id'])
            logging.info('done: %s', args.directory)
    except:
        raise Exception(''.join(traceback.format_exception(*sys.exc_info())))       
            
def extract_grids(fi):
    """ Identify entities from ptb trees for document. store in dictionary for grid construction. """
    idx = 0
    entities = defaultdict(lambda : defaultdict(dict))
    #print 'fi='+fi
    for lines, attrs in iterdoctext(fi):
        logging.debug('document %s', attrs['docid'])
        print ' extract '+str(len(lines))+' lines'
        #for line in lines:
        entities, idx =  (convert_tree(line, entities) for line in lines)
        
    return entities, idx        
                
            
        
#from dependencies extract nouns with their grammatical dependencies in given sentence
def convert_tree(line, entities):
    print ' convert_tree with '+line
    sd = StanfordDependencies.get_instance(
            jar_filename='C:\SMT\StanfordNLP\stanford-corenlp-full-2013-11-12\stanford-corenlp-full-2013-11-12\stanford-corenlp-3.3.0.jar',
            backend='subprocess')
    
    #ex='(ROOT(S(NP (PRP$ My) (NN dog))(ADVP (RB also))(VP (VBZ likes)(S(VP (VBG eating)(NP (NN sausage)))))(. .)))'
    #dependencies = sd.convert_tree(ex, debug=True)
    
    idx = 0
    #returns a list of sentences (list of list of Token objects) 
    dependencies = sd.convert_tree(line, debug=True)
    
    for token in dependencies:
        print token
        if token.pos in nouns :
            print ' .. is a noun-'+token.pos
            grammatical_role = '-'
            if token.deprel in subject: 
                grammatical_role = 'S'
            elif token.deprel in object:
                grammatical_role = 'O'
            else:
                grammatical_role = 'X'
            
            ''' if this entity has already occurred in the sentence, store the reference with highest grammatical role , 
            judged here  as S > O > X '''
            if token.lemma in entities and  entities[token.lemma][idx] :
                print str(entities[token.lemma][idx]) + ' comparing to '+str(r2i[grammatical_role])
                if (entities[token.lemma][idx]) < r2i[grammatical_role]:
                    entities[token.lemma][idx] = r2i[grammatical_role]
            else:
                entities[token.lemma][idx] = r2i[grammatical_role]
            ''' entity->list of : sentence_number->grammatical_role'''
    idx +=1
    return entities, idx
    
def construct_grid(entities, sentences):
    """ #construct grid from dictionary, rows are sentences, cols are entities """
    print 'size='+str(len(entities))
    grid = np.zeros(sentences, entities)
    entity_idx = 0
    for entity in entities.keys:
        occurances = entities[entity]
        for sentence in occurances :
            grid [sentence][entity_idx] = occurances[sentence] 
            entity_idx+=1
    return grid

def output_grid(grids, ostream):
    """ output grid  """
    
    for grid in grids:
        #print >> ostream, '# %s' % attr_str
        for i in enumerate( grid) :
            for j in enumerate (grid[i]): #each char representing entity
                    if grid[i][j] == 0:
                        print >> ostream, '-'
                    else:
                        print >> ostream, grid[i][j]
            print >> ostream,  '\n'
        print >> ostream,  '\n'
            
def parse_args():
    """parse command line arguments"""
    
    parser = argparse.ArgumentParser(description='implementation of Entity grid using ptb trees as input',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    #parser.description = 'implementation of Entity grid'
    #parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    
    parser.add_argument('directory', 
            type=str,
            #argparse.FileType('rb'),
            help="path for input file")
    
    #parser.add_argument('language', 
    #        type=argparse.FileType('r'),
    #        help="language of input file: one of English, French or German")
    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')
    
    args = parser.parse_args()
    
    logging.basicConfig(
            level=(logging.DEBUG if args.verbose else logging.INFO), 
            format='%(levelname)s %(message)s')
    return args

if __name__ == '__main__':
     main(parse_args())