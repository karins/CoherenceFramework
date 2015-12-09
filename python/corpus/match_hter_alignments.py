'''
Created on 21 Oct 2015

@author: Karin
'''

import argparse,logging
from collections import defaultdict

def match_alignments_to_doc(documents, file, output):
    
    """ for each document in documents, get lines 
        format in documents: docs[doc_id] = [doc_start,doc_end,lines_in_doc]"""
    doc_alignments = defaultdict(list)
    alignments = file.readlines()
    prevDocFinish = -1
    logging.DEBUG( 'no. docs='+str(len(documents)))
    for doc in documents:
    
        logging.DEBUG( '<doc id='+str(doc)+'>')
        doc_alignments[doc] = []
        lines = documents[doc] 
        
        alignment = prevDocFinish+ lines[0]
        while alignment <=  prevDocFinish+ lines[2]:                             # while loop iteration
            logging.debug(alignments[alignment])
            
            doc_alignments[doc].append(alignments[alignment])
            alignment+=1
        prevDocFinish += lines[1]
        print doc_alignments[doc]
        print '</doc>'

    with open( output, 'w') as outputfile:
        outputfile.write('<srcset setid=\"LIG\" srclang=\"any\">\n')
        for doc,alignments in doc_alignments.items():
            print doc
            outputfile.write('<doc id='+str(doc)+'>\n')
            for alignment in alignments:
                outputfile.write(alignment)
            outputfile.write('</doc>\n')
            
    with open( output+'.doctext', 'w') as outputfile:

        for doc,alignments in doc_alignments.items():
            print doc
            outputfile.write('# doc id='+str(doc)+'\n')
            for alignment in alignments:
                outputfile.write(alignment)
            outputfile.write('\n')            

def extract_docs(file):
    
    """#total line count in concatenated non-marked up text"""
    docs = {}
    doc_id = -1;
    in_doc = False;
    doc_start = 0
    linesIn_doc = 0
    for line in file:
        
        if "<doc>" in line :
            #reset
            lines_in_doc = 0;
            doc_id+=1
            in_doc = True;   
            #store doc start as next line            
            doc_start = lines_in_doc+1;  
        elif "</doc>" in line:
            #lineCounter++
            in_doc = False;
            #store doc end as previous line
            doc_end = lines_in_doc;
            #logging.DEBUG('storing '+str(docId)+' -> '+str(docStart)+"-"+str(docEnd)+'-'+str(linesInDoc))
            #store doc lines against doc id
            
            docs[doc_id] = [doc_start,doc_end,lines_in_doc]
        elif in_doc:
            #logging.DEBUG('incrementing '+str(lines_in_doc)) 
            lines_in_doc+=1

    return docs            

def main(args):
    match_alignments_to_doc(extract_docs(open(args.input, 'r')),open(args.alignments, 'r'),args.output)
    
def argparser():
    """parse command line arguments"""
    
    parser = argparse.ArgumentParser(description='match with hter scores.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('input', nargs='?',
                        type=str, 
                        help='input file')
    parser.add_argument('--alignments', nargs='?',
                        type=str, 
                        help='alignments file')
    
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