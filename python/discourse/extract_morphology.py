#-*-coding:utf-8-*-
'''
Created on 20 Apr 2015

@author: Karin
'''
import argparse, logging, os



def main(args):
    """
    Extracts nouns, their inflected forms and their cases from parsed files.
    Format is expected to be as follows, eg:
       lokakuuta    loka|kuu    loka|kuu    N    N    NUM_Sg|CASE_Par    NUM_Sg|CASE_Par    3    3    number    number    _    _
       kauppajärjestön    kauppa|järjestö    kauppa|järjestö    N    N    NUM_Sg|CASE_Gen    NUM_Sg|CASE_Gen    6    6    poss    poss    _    _
       ministerikokouksessa    ministeri|kokous    ministeri|kokous    N    N    NUM_Sg|CASE_Ine    NUM_Sg|CASE_Ine    9    9    nommod    nommod    _    _
       Maailman    maa|ilma    maa|ilma    N    N    NUM_Sg|CASE_Gen|CASECHANGE_Up    NUM_Sg|CASE_Gen|CASECHANGE_Up    16    16    poss    poss    _    _
    
    """
    #we won't track nominative case, as there is no need for a replacement in target 
    cases = ('CASE_Ela', 'CASE_Gen', 'CASE_Com', 'CASE_Ins', 'CASE_All', 'CASE_Ade', 'CASE_Ess', 'CASE_Ill', 'CASE_Abe', 'CASE_Par', 'CASE_Tra', 'CASE_Ine', 'CASE_Abl')
    nouns = {}
    files = [name for name in os.listdir(args.directory) if os.path.isfile(os.path.join(args.directory, name)) ]
    for filename in files:
        logging.info(filename)
        with open(os.path.join(args.directory, filename)) as fi:
            for line in fi:
                logging.debug('line= '+line)
                tuples =  line.split()
                if len(tuples) > 3 and 'N' == tuples[4]: 
                    logging.debug('noun: '+ tuples[1]+' -> '+ tuples[2])
                    if tuples[1] !=  tuples[2]:
                        if args.caseinformation and len(tuples) >7:
                            idx = tuples[7].find('CASE')
                            logging.debug('noun: '+ tuples[1]+' -> '+ tuples[2]+' '+tuples[7][idx:(idx+8)])
                            if tuples[7][idx:(idx+8)] in cases:
                                nouns[tuples[1]]= tuples[2]+' '+tuples[7][idx:(idx+8)]
                            else:
                                nouns[tuples[1]]= tuples[2]
                            #cases.add(tuples[7][idx:(idx+8)])
                        else:
                            nouns[tuples[1]]= tuples[2]
        #print nouns
        if nouns:
            if not os.path.exists(args.output):
                os.makedirs(args.output)
            with open(os.path.join(args.output, filename ), 'w') as output:
                for key,value in nouns.iteritems():
                    output.write(str(key))
                    output.write('\t')
                    if args.splitcompounds and '|' in value:
                        output.write(value.translate(None,'|') + '\n')
                    else:
                        output.write(value + '\n')

def parse_args():
    """parse command line arguments"""
    
    parser = argparse.ArgumentParser(description='extracts and combines system scores, each representing a document',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('directory', nargs='?',
                        type=str, 
                        help='input corpus')
    
    parser.add_argument('--output', nargs='?',
                        type=str, 
                        help='output file for combined extracts')
    
    parser.add_argument('--splitcompounds', dest='splitcompounds', default ='store_false',
                        action='store_true',
                        help='flag to indicate if compounds should be split. Defaults to false and leaves them with pipe character.')
    
    parser.add_argument('--caseinformation', dest='caseinformation', default ='store_false',
                        action='store_true',
                        help='flag to indicate whether case information should be stored. Defaults to false.')
  
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