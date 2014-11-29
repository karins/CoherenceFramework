package nlp.framework.discourse;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import org.javatuples.Triplet;

import edu.stanford.nlp.ling.Label;
import edu.stanford.nlp.trees.CollinsHeadFinder;
import edu.stanford.nlp.trees.PennTreeReader;
import edu.stanford.nlp.trees.Tree;

/**
 * Takes PTB files as input.
 * Extracts grammatical sequences to given depth, or grammatical productions.
 * 
 * @author Karin
 *
 */
public class SyntaxModel {
	
	private static final String [] PUNCTUATION = {",", ".", "?", "'", ";", ":", "!", "(", ")", "[", "]", "\"", "``", "`"};
	public static final int PRODUCTIONS_TYPE = 0;
	public static final int SEQUENCES_TYPE = 1;
	

	private Map<String, Integer> productionCounts = new HashMap<String, Integer>();	
	private Map<String, Integer> unigramCounts = new HashMap<String, Integer>();
	
	private List <Triplet<String,String,Integer>> productions = new ArrayList<Triplet<String,String,Integer>>();
	

	private int type;
	
	public  SyntaxModel () {
		// presume sequence type for now
		this.type = SEQUENCES_TYPE;
	}
	
	/**
	 * 
	 * Presumes that input files are all numbered, ending in consecutive numbers
	 * @param args filename of input file(s), number of files in set, outputfile 
	 */
	public static void main(String [] args ) {
		String filename = args[0];
		String noOfFiles = args[1];
		String outputFile = args[2];
					
		try {
			
			SyntaxModel model = new  SyntaxModel();
			model.extractSyntacticSequences(filename, Integer.parseInt(noOfFiles), 2, outputFile);
			
		} catch (IOException e) {
			System.out.println("Error encountered while extracting syntactic seqences from "+filename);
			e.printStackTrace();
		}
		
	}

	private void extractSyntacticSequences(String filename, int numberFiles, int depth,	String outputFile) 
																							throws IOException {
		for(int i = 0; i<numberFiles; i++){
			
			List<List<Label>> sequences = getSequencesFromParseTree(filename+i, depth);
			
			FileOutputUtils.streamToFile(outputFile+i, printSequences(sequences));
		}
	}
	
	private StringBuffer printSequences(List<List<Label>> sequences) {
		StringBuffer buffer = new StringBuffer();
		for(List<Label> sequence: sequences){
			System.out.print("\n sequence : ");
			for(Label label :sequence){
				System.out.print(label+" ");
				buffer.append(label);
				buffer.append(" ");	
			}buffer.append("\n");
		}
		return buffer;
	}
	
	
		
	private Tree[] getChildren(Tree root, int depth, List<Label> sequence) {
		
		depth--;
		
		while(depth > 0){
			//System.out.println( "Tree[] getChildren parent="+root.label());
			for(Tree child: root.children()){
				//System.out.println( " child="+child.label()+" no. children="+child.numChildren()+" d="+depth);
				
				return getChildren(child, depth, sequence);
			}
		}
		return root.children();
	}
	
	/**
	 * For each document:
	 * <li>		Read in source text and construct parse tree. 
	 * <li>		(Remove terminals, so that leaf nodes are POS tags.)
	 * <li>		Extract grammatical productions of form LHS -> RHS, to given depth 
	 *  @return List of POS labels for extracted sequence
	 * @param depth indicates the depth of the tree to be rendered NB CURRENTLY BUG AT DEPTHS GREATER THAN 2
	 * @throws IOException 
	 */
	public List<List<Label>> getSequencesFromParseTree(String filename, int depth) throws IOException{
		
		List<List<Label>> sequences = new ArrayList<List<Label>>();
		
		PennTreeReader treeReader = new PennTreeReader(new InputStreamReader(new FileInputStream(new File(filename))));
		Tree root = treeReader.readTree();
		
		while(root != null){
			
			List<Label> sequence = new ArrayList<Label>();
			Tree[] children = getChildren(root, depth, sequence);
			
			for(Tree child: children){
				System.out.println( "add label "+child.label() +"  for child tree "+child+ " dominates= "+child.dominates(child.getChild(0)));				
								
				//if not simply punctuation
				if(isPunctuation(child.label()) == false && child.getChild(0).isLeaf()==false){
					//annotate with leaf that they dominate
					//check for left-most leaf that the node dominates
					//TODO: THIS IS NOT DOING THAT				
					Label label = child.label(); 
					if(type==SEQUENCES_TYPE){
						StringBuffer annotatedLabel = new StringBuffer(label.toString()+"*"+child.getChild(0).label().toString().toLowerCase());
						label.setValue(annotatedLabel.toString());
						sequence.add(label);
					}else{//UNTESTED- grammatical productions
						StringBuffer annotatedLabel = new StringBuffer(label.toString()+"->");
						for(Tree gchild : child.children()){
							annotatedLabel.append(gchild.label()+" ");
						}
						label.setValue(annotatedLabel.toString().trim());
						sequence.add(label);
					}
				
				}else if(isPunctuation(child.label()) == false){//dont add punctuation
					sequence.add(child.label());
				}
				
			}System.out.println( "sequence: "+sequence);
			sequences.add(sequence);
			root = treeReader.readTree();
		}
			
		return sequences;
	}
	
	private boolean isPunctuation(Label label) {

		for(String punctuation: PUNCTUATION){
			if(punctuation.equalsIgnoreCase(label.toString())){
				return true;
			}
		}
		return false;
	}
	
}
