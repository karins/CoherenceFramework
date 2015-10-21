'''
Created on 21 Oct 2015

@author: Karin
'''

def match_alignments_to_doc(documents, file, path):
    docs = set()
    """ for each document in documents, get lines """
    
    alignments = file.readlines()
    prevDocFinish = -1
    for doc in documents:
        
        sumOfHter = 0
        lines = documents[doc]
        
        hter = prevDocFinish+ lines[0]
        #print ' hter start='+str(hter)
        while hter < prevDocFinish+ lines[2]:                             # while loop iteration
            #sumOfHter += float(hters[hter])
            hter += 1
            
            #print  str(sumOfHter/lines[2])+', '
            docs.add(doc )
            docIdPerHter[doc]= sumOfHter/lines[2]
        prevDocFinish += lines[1]


def extractDocs(file, docs):
    
    """#total line count in concatenated non-marked up text"""
    docId = -1;
    inDoc = False;
    docStart = 0
    linesInDoc = 0
    for line in file:
        
        if "<doc>" in line :
            #reset
            linesInDoc = 0;
            docId+=1
            inDoc = True;   
            #store doc start as next line            
            docStart = linesInDoc+1;  
        elif "</doc>" in line:
            #lineCounter++
            inDoc = False;
            #store doc end as previous line
            docEnd = linesInDoc;
            #print 'storing '+str(docId)+' -> '+str(docStart)+"-"+str(docEnd)+'-'+str(linesInDoc)
            #store doc lines against doc id
            #docScores[docId] = str(docStart)+"-"+str(docEnd) +'-'+str(linesInDoc)
            docScores[docId] = [docStart,docEnd,linesInDoc]
        elif inDoc:
            #print 'incrementing '+str(linesInDoc) 
            linesInDoc+=1

    return docScores            

if __name__ == '__main__':
    pass