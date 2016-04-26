# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 12:57:19 2016

@author: karin
"""

'''

Takes as input a document with <doc> tags and outputs mteval-xml format.

Created on 23 Feb 2016

@author: Karin
'''
import argparse, logging



def main(args):
    
    xml_header = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE mteval SYSTEM \"ftp://jaguar.ncsl.nist.gov/mt/resources/mteval-xml-v1.6.dtd\">\n<mteval>\n"
    
    #logging.debug('file %s'%args.input)
    print('file %s'%args.input)
    idx = 0
    with open(args.output+'.mteval.xml', 'w') as outputfile:
        outputfile.write(xml_header)
        line_no = 0
        for line in open(args.input, 'r'):
            logging.debug(line)        
            if "<doc" in line :
                line_no = 0
                if not "id" in line or "docid" in line:
                    outputfile.write('<doc src=\"LIG\" id=\"'+str(idx)+'\">\n')
                    idx+=1
                else:
                    outputfile.write(line)
            elif "<srcset" in line or "</srcset>" in line or "</doc>" in line:
                outputfile.write(line)
            else:
                outputfile.write("<seg id=\"%d\">%s</seg>\n" %(line_no, line.rstrip()))
                line_no+=1
        outputfile.write("</mteval>\n")
                        

def argparser():
    """parse command line arguments"""
    
    parser = argparse.ArgumentParser(description='Remove the leading alphanumeric from each line.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('input', nargs='?',
                        type=str, 
                        help='input file')
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