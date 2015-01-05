package nlp.framework.discourse;

import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.tregex.TregexPattern;

/**
 * stores filename, line of tree, regex and both PE match with MT equivalent
 * @author Karin
 *
 */
public class SubtreeDerivation {
	private String filename;
	private int line;
	private TregexPattern regex;
	private Tree tree;
	private Tree equivalentTree;
	
	public SubtreeDerivation(String filename, int line, TregexPattern pattern, Tree tree ){
		this.filename = filename;
		this.line = line;
		this.regex = pattern;
		this.tree = tree;
		System.out.println("NEW: "+filename+" line: "+line+" pattern "+pattern+" in tree "+tree);
	}
	
	public int getLine(){
		return this.line;
	}
	/**
	 * returns the regex used to extract this subtree from main tree
	 * @return
	 */
	public TregexPattern getRegex(){
		return this.regex;
	}
	
	public Tree getMatchedTree(){
		return this.tree;
	}

	public void storeEquivalent(Tree equivalentTree, Tree match) {
		this.equivalentTree = equivalentTree;
		System.out.println("PE: "+tree);
		System.out.println("MT: "+equivalentTree);
		if(match != null) System.out.println("MATCHED: "+match);
	}
	
	
	
}
