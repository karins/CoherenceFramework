'''
Extract errors deemed related to entity-based cohesion.
Created on 8 Oct 2015

@author: Karin
'''
#! /usr/bin/python
#-*-coding:utf-8-*-
import argparse, logging, os
from collections import defaultdict
import cPickle as pickle
#import pickle
import json
import re

NOUNS = set(['NNP','NNPS', 'NNS', 'NN', 'N', 'NE'])
error2int= {"removed_in_PE" : 0, "inserted_in_PE" : 1} 
int2error= {0 :"removed_in_PE", 1:"inserted_in_PE"}
removed_in_PE = 0
inserted_in_PE = 1

def main(args):
    """ Extract nouns out of parsed file. Presumption is that if Noun is edited out of MT then it is an error, not mere lexical whim. 
    input format: (S1 (S (NP (DT The) (NN public)) (VP (MD will) (ADVP (RB soon)) (VP (AUX have) (NP (DT the) (NN opportunity) ...
    
    Process lists to derive lexical errors.
    format -: extracted list:   2      United States reverts to ->2      tats-unis 
    """
    
    PE_nouns_per_doc = extract_nouns(args.directory+os.sep+'pe', args.output)
    MT_nouns_per_doc = extract_nouns(args.directory+os.sep+'mt',args.output)
    
    derive_errors(PE_nouns_per_doc, MT_nouns_per_doc, args.errorfile)
    
def derive_errors(PE_nouns_dict, MT_nouns_dict, output):
    """
        lexical errors: 
        0      step Balkans world Iraq North Korea crisis Iran weapons Kosovo  
        1      public opportunity attention province decision fate  
        2      tats-unis friends intention end year decision Kosovo Serbia  
        
        0      step Balkans world Iraq North Korea crisis Iran weapons Kosovo  
        1      public opportunity attention province decision fate  
        2      United States friends intention end year decision Kosovo Serbia
        
        ->extracted list:   2      United States reverts to ->2      tats-unis   
        in format: line_no , type_error [0-1-2]  , noun(s)
        becomes 2    2 United States|tats-unis 
        
        0 = removed holds nouns in MT but not in PE, so need added to reverse error
        1 = inserted holds nouns in PE which are absent in MT, so should be removed to reverse error 
        """
    
    errors = defaultdict(defaultdict)
    
    for doc_id, PE_nouns_lines in PE_nouns_dict.items():
        logging.debug( 'DOC=%s'%doc_id)
        
        errors[doc_id] = defaultdict(list)
        
        MT_nouns_lines = MT_nouns_dict.get(doc_id)
        
        if not MT_nouns_lines:
            """ no lexical errors in that doc??- unlikely?"""
            #errors[doc_id]={inserted_for_PE, PE_nouns_lines}
            #errors[doc_id][PE_nouns_lines][inserted_in_PE]= PE_nouns_lines
            #errors[doc_id] = [PE_nouns_lines][inserted_in_PE]
            #errors[doc_id] = [PE_line_no]={inserted_in_PE: inserted_PE_nouns
            print 'no lexical errors in that doc??- unlikely?'
        else:
        
            for PE_line_no, PE_nouns in PE_nouns_lines.items():
                
                matched = False
                for MT_line_no, MT_nouns in MT_nouns_lines.items():
                    
                    if MT_line_no == PE_line_no:
                        deleted_MT_nouns =[noun for noun in MT_nouns if noun not in PE_nouns] 
                        inserted_PE_nouns =[noun for noun in PE_nouns if noun not in MT_nouns]
                        
                        if deleted_MT_nouns or inserted_PE_nouns:
                            errors[doc_id][PE_line_no]= {inserted_in_PE: inserted_PE_nouns,  removed_in_PE: deleted_MT_nouns}
                            
                        matched = True
                        break
                if not matched:
                    """  not in MT, only in PE, so inserted_for_PE"""
                    errors[doc_id][PE_line_no]={inserted_in_PE: PE_nouns, removed_in_PE:[]}
            if len(set(MT_nouns_lines) - set(PE_nouns_lines)) >0:
                """ in MT only, so removed_for_PE  """
                noun_list = list(set(MT_nouns_lines) - set(PE_nouns_lines))
                #logging.debug( noun_list)
                print '&&& MT ONLY: ' 
                print noun_list
                #for MT_line_no, MT_nouns in noun_list.iteritems():
                #    errors[doc_id][MT_line_no]={inserted_in_PE:[], removed_in_PE:MT_nouns}

    f = open( output+'_json', 'w')
    f.write( json.dumps(errors) )
    
    """ pickle not handling foreign chars- not sure if unicode issue""" 
    """with open(output+'_pickle', 'wb') as file:
        pickle.dump(errors, file,pickle.HIGHEST_PROTOCOL)
        file.flush()
        file.close()
       """ 
    
    #print errors
    with open( output, 'wb') as fo:
        for docid, lines in errors.items():
            for line, error_types in lines.items():
                for type, words in error_types.items():
                    fo.write(str(docid)+'\t'+str(line)+'\t'+str(type)+'\t')
                    for word in words:
                        fo.write(word+' \t')
                    fo.write('\n')
               
def printit(errors):
    for docid, lines in errors.items():
        #print 'no lines %s'%len(lines) 
        for line in lines.items():
            logging.debug('line :'+ line)
            """for error_type,items in type.items():
           #print str(docid)+'\t'+str(lines[0]) +error_type
           print '%s \t %s \t %s' %(docid, lines[0],error_type)
           for item in items:
               print item
       """    
def extract_nouns(directory, output):
    nouns = defaultdict(list)
    files = [name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name)) ]
    for filename in files:
        logging.info('extracting nouns for filename'+filename) 
        
        doc = map(int, re.findall("\d+",filename))[0]
        nouns[doc]= defaultdict(list)
        with open(os.path.join(output, filename ), 'w') as fo:
            with open(os.path.join(directory, filename)) as fi:
                if not os.path.exists(output):
                    os.makedirs(output)
                line_no = 0
                nouns[doc][line_no] = []
                for line in fi:
                    
                    fo.write(str(line_no)+' \t ')
                    items = line.split()
                    for i in range(len(items)):
                        item = items[i]
                        #(S1 (S (NP (DT The) (NN public))
                        for NOUN in NOUNS:
                            if NOUN == item.lstrip('('):
                                logging.debug(items[i+1].rstrip(')'))
                                if '#' not in items[i+1]:
                                    nouns[doc][line_no].append(items[i+1].rstrip(')').lower())
                                    fo.write(items[i+1].rstrip(')')+' ')
                    fo.write(' \n')
                    line_no +=1 
                
    return nouns
                            
def argparser():
    """parse command line arguments"""
    
    parser = argparse.ArgumentParser(description='Remove the leading alphanumeric from each line.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('directory', nargs='?',
                        type=str, 
                        help='input directory')
    
    parser.add_argument('--output', nargs='?',
                        type=str, 
                        help='output directory')
    
    parser.add_argument('--errorfile', nargs='?',
                        type=str, 
                        help='error file')
    parser.add_argument('--verbose', '-v',
            action='store_true',
            help='increase the verbosity level')
    
    args = parser.parse_args()
    
    logging.basicConfig(
            level=(logging.DEBUG if args.verbose else logging.INFO), 
            format='%(levelname)s %(message)s')
    return args


if __name__ == '__main__':
    main(argparser())