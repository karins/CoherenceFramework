'''
Created on 9 Oct 2015

@author: Karin
'''
import argparse, logging, os
import json

def main(args):
    """ Take errors from error file and insert into reference file, with relevant markup. 
    Errors may take various forms. Input may be parsed file or plain text.
PE:
1      after#9#Temporal 
5      but#43#Comparison 
5      as#58#Temporal 
6      because#2#Contingency 
7      Indeed#7#Expansion 
MT:
0      Yet#17#Comparison     
1      when#10#Temporal     
5      but#13#Comparison 
6      because#2#Contingency 
7      Indeed#5#Expansion 
 
  Actual error injected into postedited sentence, which is then replaced in copy of postedited corpus. - in the case of lexical and discourse connective errors. 
  For structural errors entire sentence is replaced. [As MT too distant from REF stylistically.]
  The overall effect is that of isolating discourse errors in the corpus.
    """
    
    inject_errors(args.directory+os.sep+'pe',args.directory+os.sep+'mt',  args.errors, args.alignments)
    
def inject_errors(pe, mt, errors, alignments):
    """ params: plain text reference file to be injected, post-edited version, machine-translated version, list of errors 
    PE: (S1 (S (S (NP (NP (DT Another) (JJ crucial) (NN step)) (PP (IN for#39#0) (NP (NP (DT the) (NNPS Balkans
    MT: (S1 (S (CC Yet#17#Comparison) (S (NP (NP (DT a) (JJ crucial) (NN step)) (PP (IN for#18#0) (NP (NP (DT the) (NNPS Balkans))
    1 find position of connective in sentence
    
    
     
    discourse connectives:
    0      Yet#17#Comparison 
    1      when#10#Temporal 
    5      but#13#Comparison 
    pe:
    1      after#9#Temporal 
    5      but#43#Comparison 
    5      as#58#Temporal 
    'Yet' wrongly in MT, deleted in pe -> reinsert 
    'when' becomes 'after' in PE    -> replace
    'as' missing in MT, inserted in PE ->insert
    """
    
    inject_clausal_errors(pe, mt, errors)
    inject_lexical_errors(pe, mt, errors)
    #inject_discourse_errors(pe, mt, errors)
    
def inject_clausal_errors(pe_text, mt_text, alignments_file):
    
    
def inject_lexical_errors(pe_text, mt_text, error_file):
    """
    lexical errors: 
    0      step Balkans world Iraq North Korea crisis Iran weapons Kosovo  
    1      public opportunity attention province decision fate  
    2      tats-unis friends intention end year decision Kosovo Serbia  
    0      step Balkans world Iraq North Korea crisis Iran weapons Kosovo  
    1      public opportunity attention province decision fate  
    2      United States friends intention end year decision Kosovo Serbia
    
    Using list of extracted errors: 
    1. find position of item in MT: find correct line, then locate within line
    2. find new position in PE
    3. replace in PE
    
    error list of format below, where 
    0 = removed : nouns in MT but not in PE, so need added to reverse error
    1 = inserted : nouns in PE which are absent in MT, so should be removed to reverse error
    doc_1    32    [0, ['tant']]
    doc_1    2    [1, ['United', 'States']]
    doc_1    5    [1, ['UN', 'fact']]
    doc_1    6    [1, ['Serbian']] 
    """
    removed_in_PE = 0
    inserted_in_PE = 1 
    #for pe in pe_text:
    files = [name for name in os.listdir(pe_text) if os.path.isfile(os.path.join(pe_text, name)) ]
    for filename in files:
        logging.info(filename)
        
        MT_files = [name for name in os.listdir(mt_text) if os.path.isfile(os.path.join(mt_text, name)) ]
        for mt_filename in MT_files:
        
            with open(os.path.join(pe_text, filename)) as pe_doc:
                pe_lines = pe_doc.readlines()
                with open(os.path.join(mt_text, mt_filename))as mt_doc:
                    mt_lines = mt_doc .readlines()
                    
                    #my_dict = eval(mt_doc.read())
                    
                    errors = json.load(open(error_file+'_json'))
                    print errors 
                    for doc, lines in errors.items():
                        print doc
                        #for line_no, error in line.items():
                        for line, error_types in lines.items():
                            print line
                            #print error 
                            #for type, lexical_items in error.items():
                            for error_type, words in error_types.items():
                                print 'type=%s'% error_type
                            #error_type = error[0]
                            
                            
                            #lexical_items = error[1]
                                if int(error_type) == removed_in_PE:
                                    print 'type=removed in PE->reinsert to revert'
                                    print words
                                    #for word in words:
                                    """ find position via alignments and check if straight reversion is feasible """
                                        
                                    pe_words = pe_lines[line] 
                                    
                                elif int(error_type) == inserted_in_PE:
                                    print 'type=insert in PE->remove to revert'
                                    print words
                             
                            for word in words:
                                print word
                            
                    #mt_doc.write(str(error_dict))
                    #mt_doc.close() 
                    #with open(error_file) as errors:
                    """   for line in errors:
                            items = line.split('\t')
                            #for item in items:
                            #    print item
                                #doc_1    32    [0, ['tant']]
                            print 'doc= %s line= %s error: %s ' % (items[0],items[1],items[2])
                            #[1, ['Contact', 'Group', 'United', 'States', 'United', 'Kingdom']]
                            error = dict([0, ['tant']])
                            #dict( items[2])
                            if error.has_key(removed_for_PE):
                                print 'type=remove from PE'+error.get(removed_for_PE)
                            elif error.has_key(inserted_for_PE):
                                print 'type=insert in PE:'+error.get(inserted_for_PE)
"""  
  
        """     for idx, mt_line in enumerate(mt_text):
        #for idx, mt_line in enumerate(mt_text):
            #error_line :
            if error[0] == idx:
                loc = mt_line.find(error[2])
                
                for idx, pe_line in enumerate(pe_text):
                    loc2 = pe_line.find(error[1])
                    #pe_line.replace(pe, mt,)
                    print 'pe line was: '+pe_line
                    pe_line[loc2] = error[2]
                    print 'pe line now: '+pe_line
         
        """
    
def argparser():
    """parse command line arguments"""
    
    parser = argparse.ArgumentParser(description='Remove the leading alphanumeric from each line.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('directory', nargs='?',
                        type=str, 
                        help='input directory')
    parser.add_argument('--errors', nargs='?',
                        type=str, 
                        help='error list')
    parser.add_argument('--output', nargs='?',
                        type=str, 
                        help='output directory')
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