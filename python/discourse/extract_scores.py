'''

Utility script to extract scores from multiple source files, each containing one score per document. 

Created on 27 Feb 2015

@author: Karin Sim
'''
import argparse
import collections
import logging
import math
import os.path


def output_score(HT_label, HT, HT_output):
    for key, value in HT.iteritems():
        HT_output.write(HT_label + ' ')
        for key, value in value.iteritems():
            
            HT_output.write(str(key))
            HT_output.write(':')
            HT_output.write(value + ' ')
        
        HT_output.write('\n')
    
    logging.info('done: %s', HT_output)
    return key, value

def main(args):
    """
    input: for each model:
            directory containing documents with probability scores for each system (eg ref, edin, online)
            C:\..\..\graph, 
            C:\..\..\gridprobabilities
            
    output: 50% from ref 50% from mixed MT system output
    
    for each model (ibm, graph, grid, AL): as represented by input list of directories:
        add directories to list of models
        create master list of input scores for model: MT and HT
        take directory :
                    -determine ref and extract scores -> HT file
                    
                    # do this 5 times, with shuffled list -> 5 MT files, variously extracted:
                    -determine number of systems and extract scores evenly from them-> MT file 
                    numberofdocs/numberofsystems= filespersystem
                    NB math.ceil(numberofdocs/numberofsystems.0) 
        output all scores to file, in following format: <label> <index1>:<value1> <index2>:<value2> ...
                    """
    MT_label = '-1'
    HT_label = '1'
    MT = collections.OrderedDict()
    HT = collections.OrderedDict()
    
    models = args.model
    print models
    model_idx = 1
    for model in models:
        logging.debug('model= '+model)
        get_ref_scores(model, HT, model_idx)
        get_scores(model, len(HT), args.output, MT, model_idx)
        model_idx +=1
    
    print HT
    print MT
    with open(os.path.join(model, args.output+'.HT_scores'), 'w') as HT_output:
        key, value = output_score(HT_label, HT, HT_output)
        
    with open(os.path.join(model, args.output+'.MT_scores'), 'w') as MT_output:
        key, value = output_score(MT_label, MT, MT_output)
        
def get_ref_scores(directory, HT, model_idx):
    ref = [name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name)) and name.endswith('ref')]
    if None is ref or len(ref)==0:
        raise Exception('No reference system for '+directory)
    with open(os.path.join(directory, ref[0])) as fi:
        lines = [line.strip() for line in fi if not line.startswith('#')]
        for line in lines: 
            items = line.split()
            logging.debug('adding '+items[1])
            if items[0] not in HT:
                HT[items[0]] = {}
            if [model_idx] not in [items[0]]:
                HT[items[0]][model_idx] = {} 
            HT[items[0]][model_idx]= items[1]
        
def get_scores(directory, num_docs, output, MT, model_idx):    
    """ Extract scores, even distribution per system """
    
    systems = [name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name)) and not name.endswith('ref')]
    logging.debug('systems= '+str(systems))
    num_systems = len(systems)
    if None is num_systems or num_systems==0:
        raise Exception('No systems to compare: '+directory)
    lines_per_system = math.ceil(num_docs/float(num_systems))
    
    logging.debug('number of docs= '+str(num_docs)+' number of systems= '+str(num_systems))   
    logging.debug('number of lines per system='+str(math.ceil(num_docs/float(num_systems))))
    
    #read defined number of lines, then move onto next system and extract the same
    index = 0
    for filename in systems:
        logging.debug('file='+filename)
        file = os.path.join(directory, filename)
        logging.debug('path='+file)
        
        with open(os.path.join(directory, filename)) as fi:
            lines = [line.strip() for line in fi if not line.startswith('#')]
            logging.debug('index='+str(index))
            logging.debug('end='+str(int(lines_per_system)+index))
            lines_to_include = lines[index:int(lines_per_system)+index]
            
            #read from index, up to lines_per_system:
            for line in lines_to_include: 
                
                items = line.split()
                logging.debug('adding '+items[1])
                
                if items[0] not in MT:
                    MT[items[0]] = {}
                if [model_idx] not in [items[0]]:
                    MT[items[0]][model_idx] = {} 
                MT[items[0]][model_idx]= items[1]
                index +=1
                if index == lines_per_system:
                    logging.debug('break index='+str(index))
                    break

def parse_args():
    """parse command line arguments"""
    
    parser = argparse.ArgumentParser(description='extracts and combines system scores, each representing a document',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('--model', 
                        default=[],
                        action='append',
                        help='models to be included')
    
    parser.add_argument('--output', nargs='?',
                        type=str, 
                        help='output file for combined scores')
    
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