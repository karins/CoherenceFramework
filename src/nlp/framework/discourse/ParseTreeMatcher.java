package nlp.framework.discourse;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import edu.stanford.nlp.trees.tregex.TregexMatcher;
import edu.stanford.nlp.trees.tregex.TregexPattern;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.TreeReaderFactory;
import edu.stanford.nlp.trees.tregex.TregexPattern.TRegexTreeReaderFactory;
import edu.stanford.nlp.trees.PennTreeReader;

public class ParseTreeMatcher {
	
	static List<TregexPattern> patterns = new ArrayList<TregexPattern>();
	
	static{
		//
		//There is a pattern for an exact subtree: This disallows anything beyond the 4th NNP.
		//NP <... { DT ; NNP ; NNP ; NNP ; NNP }
		//If you want more general patterns, you can also do
		//NP <1 DT <2 NNP <3 NNP
		//You can also do
		//NP < (DT $+ (NNP $+ NNP)) to guarantee that there is another NNP nodes after the first.
		
		//NP < (DT $. NNP)

		//TregexPattern test_pattern = TregexPattern.compile("S < ( NP)");
		//patterns.add(test_pattern);
		
		//pe:		(ROOT (S (SBAR (IN As) (S (NP (NP (NNP Leszek) (NNP Balcerowicz)) (, ,) (NP (NP (NN governor)) (PP (IN of) (NP (NP (DT the) (NNP National) (NNP Bank)) (PP (IN of) (NP (NNP Poland))))))) (VP (VBD pointed) (PRT (RP out))))) (, ,) (NP (NP (DT the) (NN adoption)) (PP (IN of) (NP (NP (DT the) (NNP Euro)) (PP (IN by) (NP (DT the) (NN candidate) (NNS countries)))))) (VP (MD will) (ADVP (RB certainly)) (VP (VB benefit) (NP (PRP them)) (SBAR (IN while) (FRAG (, ,) (PP (IN in) (NP (DT the) (JJS worst) (NN case))) (, ,))) (S (VP (VBG having) (NP (NP (RB absolutely) (DT no) (NN effect)) (PP (IN on) (NP (DT the) (JJ current) (NNS members)))))))) (. .)))
		//mt: 		(ROOT (S (SBAR (IN As) (S (VP (VBN pointed) (PRT (RP out)) (NP (NNP Leszek) (NNP Balcerowicz))))) (, ,) (NP (NP (NN governor)) (PP (IN of) (NP (NP (DT the) (NNP National) (NNP Bank)) (PP (IN of) (NP (NNP Poland))) (, ,) (VP (VBG adopting) (NP (DT the) (NN euro)) (PP (IN by) (NP (DT the) (NNS candidates))))))) (VP (VBZ is) (ADVP (RB certainly)) (NP (NP (NNS profits)) (PP (IN for) (NP (NP (DT the) (NNS candidates)) (PP (IN while) (PRN (, ,) (PP (IN in) (NP (DT the) (JJS worst) (NN case))) (, ,)) (NP (NP (RB absolutely) (DT no) (NN effect)) (PP (IN for) (NP (DT the) (JJ current) (NNS members))))))))) (. .)))
		//TregexPattern SBAR_pattern = TregexPattern.compile("ROOT <1 S <2 SBAR <3 IN <4 S <5 NP <6 VP <7 VB"); 
		//TregexPattern SBAR_pattern = TregexPattern.compile("S < ( SBAR . IN . S . NP . VP )");
		//TregexPattern SBAR_pattern = TregexPattern.compile("S <... { SBAR ; IN ; S ; NP ; VP }");
		//S < (NP $++ VP) to match an S over an NP, where the NP has a VP as a right sister.
		//VP < (SBAR < (IN < that))
		TregexPattern SBAR_pattern = TregexPattern.compile("S <  (SBAR < (IN < As) < ( S < ( NP) < (VP ))) ");
		//TregexPattern SBAR_pattern = TregexPattern.compile("S <  (SBAR ) ");
		patterns.add(SBAR_pattern);
		//(ROOT (S (S (VP (VBG Adopting) (NP (DT the) (NNP Euro)))) (VP (MD would) (VP (VB give) 
		//TregexPattern VBG_pattern = TregexPattern.compile("NP < (ADJP <1 JJ <2 S <3 VP <4 TO <5 VP <6 VB)"); 
		//TregexPattern VBG_pattern = TregexPattern.compile("NP < (ADJP . JJ . S . VP . TO . VP . VB)");
		//works, but 0 TregexPattern VBG_pattern = TregexPattern.compile("S <(S < (VP < (VBG < (NP ))) < (VP < (MD)  < (VP  < (VB ))))");
		//TregexPattern VBG_pattern = TregexPattern.compile("S <(S < (VP < (VBG < (NP )))) < (VP )");
		//**TregexPattern VBG_pattern = TregexPattern.compile("S <(S < (VP < (VBG < (NP ))))");
		//TregexPattern VBG_pattern = TregexPattern.compile("S < (S < (VP < (VBG) . (NP < (DT ))))");
		//TregexPattern VBG_pattern = TregexPattern.compile("S < (S < (VP < (VBG) < (NP < (DT ) (NNP )))");
		//works 
		TregexPattern VBG_pattern = TregexPattern.compile("S < (S < (VP < (VBG) ))");
		patterns.add(VBG_pattern);
		//PE: (ROOT (S (NP (DT The) (NN euro) (NN adoption) (, ,)) (VP
		//where MT (ROOT (S (NP (DT The) (NN euro) (NN adoption)) (, ,) (NP (PRP they)) (VP (MD would) (VP 
		
		
		//pe (ADJP (JJ able) (S (VP (TO to) (VP (VB accomplish))))))))))))))))))))))))))) (. .)))
		//	mt (ADJP (JJ able) (PP (TO to) (NP (PRP$ their) (NNS policies)))))))))))) (. .)))
		//NP <... { DT 
		//TregexPattern JJ_VB_pattern = TregexPattern.compile("ADJP < (( JJ < Able) < (S <(VP <(TO to) <(VP))))}");
		//works:TregexPattern JJ_VB_pattern = TregexPattern.compile("ADJP < ( JJ < able)");
		//TregexPattern JJ_VB_pattern = TregexPattern.compile("ADJP < (JJ . S . VP . TO . VP . VB)");
		TregexPattern JJ_VB_pattern = TregexPattern.compile("ADJP < ( JJ < able) < (S <(VP <( TO < to)  <(VP) ))");
		//patterns.add(JJ_VB_pattern);
		//TregexPattern JJ_VB_pattern = TregexPattern.compile("ADJP <1 JJ <2 S <3 VP <4 TO <5 VP <6 VB");
		
		//(ADJP (JJ able) (PP (TO to) (NP (PRP$ their)
		//ensure 'able to' is followed by verb..
				
		//TregexPattern JJ_VB_pattern = TregexPattern.compile("ADJP <1 JJ <2 S <3 VP <4 TO <5 VP <6 VB");
		//TregexPattern POS_pattern = TregexPattern.compile("");
		
		//add: doc53
		//(ROOT (S (SBAR (IN If) (S (NP (DT the) (NNP Bush) (NN administration)) (VP (VBD sought) (NP (NP (DT the) (NNS sources)) (PP (IN of) (NP (NP (NN supply) (NN tanker)) (ADJP (JJ stable) (, ,) (JJ secure) (, ,) (JJ diversified) (CC and) (JJ cheap)))))))) (, ,) (NP (PRP it)) (VP (VBD was) (ADJP (RB enough) (S (VP (TO to) (VP (VP (VB lift) (NP (NP (DT the) (NN embargo)) (VP (VBN imposed) (PP (IN on) (NP (NNP Libya) (, ,) (NNP Iran) (, ,) (NNP Iraq) (CC and) (NNP Sudan)))))) (CC and) (VP (VB leave) (NP (DT the) (NN oil)))))))) (. .)))
		//(ROOT (S (SBAR (IN If) (S (NP (DT the) (NNP Bush) (NN administration)) (VP (VBD was) (VP (VBG seeking) (NP (NP (ADJP (JJ stable) (, ,) (JJ secure) (, ,) (JJ diversified) (CC and) (JJ inexpensive)) (NNS sources)) (PP (IN of) (NP (NN petroleum)))))))) (, ,) (NP (PRP they)) (VP (MD would) (ADVP (RB only)) (VP (VB have) (VP (VBN had) (S (VP (TO to) (VP (VP (VB lift) (NP (NP (DT the) (NN embargo)) (VP (VBN imposed) (PP (IN on) (NP (NNP Libya) (, ,) (NNP Iran) (, ,) (NNP Iraq) (CC and) (NNP Sudan)))))) (CC and) (VP (VB let) (NP (DT the) (NN oil) (NN flow))))))))) (. .)))
		
		//add
		
		//(NP (NP (DT a) (NN test)) (ADJP (ADJP (JJ difficult)
	}
	
	//stores filename, line of tree, regex and both PE match with MT equivalent: stores as mapping from filename -> SubtreeDerivation object
	//private List<SubtreeDerivation> derivations = new ArrayList<SubtreeDerivation>();
	private Map<String,List<SubtreeDerivation>> derivations = new HashMap<String, List<SubtreeDerivation>>();
	
	public static void main (String [] args){
		String PE_filename = args[0];
		int fileidx = Integer.parseInt(args[1]);
		String MT_filename = args[2];
		ParseTreeMatcher treeMatcher = new ParseTreeMatcher();
		try {
			treeMatcher.identifyMatches(PE_filename, fileidx);
			
			//read in MT file and find equivalent trees..
			treeMatcher.findEquivalentTree(PE_filename,MT_filename, fileidx);
			
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	private void findEquivalentTree(String PE_filename, String MT_filename, int fileidx) throws IOException {
		//for each doc
		for(int i = 0; i<= fileidx; i++){
			System.out.println("Starting in file:"+PE_filename+i);
			List<SubtreeDerivation> matcherTrees =  derivations.get(PE_filename+i);
			if(matcherTrees != null){
				for(SubtreeDerivation subtree : matcherTrees){
					int line = subtree.getLine();
				
					//TreeReaderFactory factory = TregexPattern.TRegexTreeReaderFactory();
					PennTreeReader treeReader = new PennTreeReader(new InputStreamReader(new FileInputStream(new File(MT_filename+i))));//, factory);
					//for each sub tree in doc
					Tree tree = treeReader.readTree();
					Tree current = tree;
					//tree.printLocalTree();
					int treeIdx = 1;
					while(tree != null && treeIdx != line){
						treeIdx++;
						//System.out.println("Check file "+MT_filename+i+" line "+treeIdx+" for line "+line);
						current = tree;
						tree = treeReader.readTree();
					}
					if(treeIdx == line){
						TregexMatcher pattern_matcher = subtree.getRegex().matcher(current );
						Tree match = pattern_matcher.getMatch();
						
						subtree.storeEquivalent(current, match);
					}
				}
			}
		}
	}

	public void identifyMatches(String filename, int fileidx) throws IOException{
		
		//for each doc
		for(int i = 0; i<= fileidx; i++){
			//System.out.println("Starting in file:"+filename+i);
			//TreeReaderFactory factory = TregexPattern.TRegexTreeReaderFactory();
			PennTreeReader treeReader = new PennTreeReader(new InputStreamReader(new FileInputStream(new File(filename+i))));//, factory);
			//for each sub tree in doc
			Tree tree = treeReader.readTree();
			//tree.printLocalTree();
			int treeIdx = 1;
			while(tree != null){
				treeIdx++;
				
				//TregexPattern pattern = TregexPattern.compile(loadPattern());
				for(TregexPattern pattern : patterns){
					int counter = 0;
					TregexMatcher pattern_matcher = pattern.matcher(tree);
				
				
					//1. Match MT and PE trees, and try to log differences in structure:first track construct in PE and get equivalent chunk in MT
						
					while(pattern_matcher.findNextMatchingNode()){
						Tree match = pattern_matcher.getMatch();
						//log incidences
						
						//System.out.println("Found: "+match.flatten());
						//System.out.println("line: "+treeIdx+" Tree: ");
						match.printLocalTree();
						counter++;
						//switch(){
						//case 
						//}
						SubtreeDerivation derivation = new SubtreeDerivation(filename+i, treeIdx, pattern, match.flatten());
						//derivations.add(derivation);
						addToMap(filename+i, derivation);
					}if(counter !=0)System.out.println("Found "+counter+" of pattern "+pattern.pattern()+" in tree "+tree.nodeString());
					//if(counter ==0)System.out.println("$$$UNMATCHED$$$"+pattern.pattern());
					
					//2. Search for particular structures in HT and how they are rendered in MT
							//(NP (NP (NP (NN accession) (NNS countries) (POS ')) (NN adoption)) (PP (IN of) (NP (DT the) (NNP Euro))))))))))))
							
					//3. Search for constructs in Fr rendered
				}
				tree = treeReader.readTree();
			}
		}System.out.println("Created "+derivations.size());
	}

	private void addToMap(String filename, SubtreeDerivation derivation) {
		List<SubtreeDerivation> lines = derivations.get(filename);
		if(lines == null){
			lines = new ArrayList<SubtreeDerivation>();
			derivations.put(filename, lines);
		}
		lines.add(derivation);
		
	}
}
