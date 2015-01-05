package nlp.framework.discourse;


import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Properties;


import org.javatuples.Triplet;
import org.javatuples.Tuple;

import edu.stanford.nlp.ling.CoreAnnotations.SentencesAnnotation;
import edu.stanford.nlp.ling.Label;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.trees.CollinsHeadFinder;
import edu.stanford.nlp.trees.Constituent;
import edu.stanford.nlp.trees.PennTreeReader;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.TreeCoreAnnotations.TreeAnnotation;
import edu.stanford.nlp.util.CoreMap;
//import edu.stanford.nlp.util.Pair;

/**
 * Takes raw file and uses Stanford Parser to convert to relevant tree bank output.
 * Extracts grammatical sequences to given depth, or grammatical productions.
 * 
 * @author Karin
 *
 */
public class TreebankConverter {
	
	//TODO: remove and parameterize
	public static final String GERMAN_TAGGER = "C:\\SMT\\StanfordNLP\\stanford-postagger-full-2013-11-12\\stanford-postagger-full-2013-11-12\\models\\german-fast.tagger";
	public static final String FRENCH_TAGGER = "C:\\SMT\\StanfordNLP\\stanford-postagger-full-2013-11-12\\stanford-postagger-full-2013-11-12\\models\\french.tagger";
	public static final String ENGLISH = "English";
	public static final String FRENCH = "French";
	public static final String GERMAN = "German";
	private static final String [] PUNCTUATION = {",", ".", "?", "'", ";", ":", "!", "(", ")", "[", "]", "\"", "``"};
	public static final int PRODUCTIONS_TYPE = 0;
	public static final int SEQUENCES_TYPE = 1;
	
	protected StanfordCoreNLP pipeline;
	private Map<String, Integer> productionCounts = new HashMap<String, Integer>();
	
	private Map<String, Integer> unigramCounts = new HashMap<String, Integer>();
	
	private List <Triplet<String,String,Integer>> productions = new ArrayList<Triplet<String,String,Integer>>();
	private List <Triplet<String,String,Integer>> frequentProductions = new ArrayList<Triplet<String,String,Integer>>();

	private int type;
	
	public TreebankConverter() {
		// presume sequence type
		this.type = SEQUENCES_TYPE;
	}
	
	public TreebankConverter(int type) {
		this.type = type;
	}

	/**
	 * for training:
	 * "C:\\SMT\\datasets\\corpus-PE\\corpus\\PEofMT_2ndHalf.en" 
	 * "C:\\SMT\\datasets\\corpus-PE\\corpus\\output_graph\\PEofMT_2ndhalf.en.ptb.syntax_productions_annotated_rerun" 
	 * "English" "2" 
	 * "C:\\SMT\\datasets\\corpus-PE\\corpus\\output_graph\\PEofMT_2ndhalf.en.syntax_productions_frequent_annotated_rerun"
	 * 
	 * first half for testing:
	 * "C:\\SMT\\datasets\\corpus-PE\\corpus\\PEofMT_half.en" 
	 * "C:\\SMT\\datasets\\corpus-PE\\corpus\\output_graph\\PEofMT_half.en.ptb.syntax_productions_annotated" 
	 * "English" 
	 * "2" 
	 * "C:\\SMT\\datasets\\corpus-PE\\corpus\\output_graph\\PEofMT_half.en.syntax_productions_frequent_annotated"
	 * @param args
	 */
	public static void main(String [] args ) {
		String filename = args[0];
		String outputfileprefix = args[1];
		String language = args[2];
		String depth = args[3];
		String outputFileForSummary = args[4];
		//int type = Integer.getInteger(args[5]).intValue();
		TreebankConverter converter = new TreebankConverter(1);
		converter.parse(filename, outputfileprefix, language, Integer.parseInt(depth));
		
		////converter.outputProductionSequences(converter.computeFrequencies(), outputFile) ;
		FileOutputUtils.streamToFile(outputFileForSummary+"_bigrams", converter.getFrequencies());
		
		FileOutputUtils.streamToFile(outputFileForSummary, converter.computeFrequencies());
		FileOutputUtils.streamToFile(outputFileForSummary+"_counts", converter.getCollatedProductionCounts());
		
		////FileOutputUtils.streamToFile(outputFileForSummary, converter.getFrequencies());
	}
	

	
	public StringBuffer outputProductionPairs(){
		StringBuffer buffer = new StringBuffer();
		for(Triplet<String,String,Integer> triplet : productions){
			buffer.append(triplet.getValue0()+"\t ");
			buffer.append(triplet.getValue1()+"\t ");
			buffer.append(triplet.getValue2());
			buffer.append('\n');
		}
	
		return buffer;	
		
	}

	/**
	 * Computes the frequencies of the productions over the corpus, to determine the coherence of a text.
	 * compute a list of all productions that occur more than 25?? times 
	 * ( A. Louis threshold for WSJ section 0 with 1727 sentence pairs over 99 docs).
	 * Ours is similar in length. 
	 * @return 
	 */
	public StringBuffer computeFrequencies() {
		
		StringBuffer buffer = new StringBuffer();
		buffer.append("\n frequent production pairs: \n");
		System.out.println( " computeFrequencies() : types of productions = "+productions.size());
		// get all productions where counts exceed 25:		<Production,Production,Integer>
		for(Triplet<String,String,Integer> triplet : productions){
		//for(Entry<Pair<String, String>,Integer> entry : entries){
			System.out.println( "checking "+triplet.getValue0()+" "+triplet.getValue1()+" "+triplet.getValue2());
			//if(triplet.getValue2().intValue() > 25){
			if(triplet.getValue2().intValue() > 5){
				System.out.println( "adding "+triplet.getValue0()+" "+triplet.getValue1()+" "+triplet.getValue2());
				frequentProductions.add(triplet);
				buffer.append(triplet.getValue0()+"\t ");
				buffer.append(triplet.getValue1()+"\t ");
				buffer.append(triplet.getValue2());
				buffer.append('\n');
			}
		}
		return buffer;
	}
	
	/**
	 * Collates the frequencies of the productions over the corpus, to determine the coherence of a text.
	 * compute a list of all productions  
	 *  
	 * @return 
	 */
	public StringBuffer getFrequencies() {
		
		StringBuffer buffer = new StringBuffer();
		System.out.println( " computeFrequencies() : types of productions = "+productions.size());
		buffer.append("\n Production pairs :\n"); 
		
		for(Triplet<String,String,Integer> triplet : productions){
			System.out.println( "adding "+triplet.getValue0()+" "+triplet.getValue1()+" "+triplet.getValue2());
			//frequentProductions.add(triplet);
			buffer.append(triplet.getValue0()+"\t ");
			buffer.append(triplet.getValue1()+"\t ");
			buffer.append(triplet.getValue2());
			buffer.append('\n');
		}
		return buffer;
	}

	public void parse(String filename, String outputfile, String language, int depth){
		Properties properties = new Properties();
		setProperties(language, properties);
		this.pipeline = new StanfordCoreNLP(properties);
		
		List<String> docs = new CorpusReader().readXML(filename);
		
		int fileidx = 0;
		for(String docAsString: docs){

			List<List<Label>> sequences = getTreebankAnnotation(docAsString, depth);
			extractSequences(sequences);			
			FileOutputUtils.streamToFile(outputfile+fileidx, printSequences(sequences, false));
			//if(DEBUG)FileOutputUtils.writeDebugToFile(debugFile, buffer.toString());
			fileidx++;
		}
	}

	private void setProperties(String language, Properties properties) {
		properties.put("-parseInside", "HEADLINE|P");
		properties.put("annotators", "tokenize, ssplit, pos, lemma, parse");
		if(language.equals(FRENCH)){
			properties.put("parse.flags", "");
			properties.put("parse.model", "edu/stanford/nlp/models/lexparser/frenchFactored.ser.gz");
			properties.put("pos.model", getTagger(language));
		}
		else if(language.equals(GERMAN)){
			properties.put("parse.flags", "");
			properties.put("parse.model", "edu/stanford/nlp/models/lexparser/germanPCFG.ser.gz");
			properties.put("pos.model", getTagger(language));
		}
	}
	
	/**
	 * Primarily for purposes of unit tests
	 * 
	 * @param contents to parse
	 * @param language
	 * @return 
	 * @return String of output
	 */
	public StringBuffer parseString(String contents, String language, int depth){
		Properties properties = new Properties();
		setProperties(language, properties);
		this.pipeline = new StanfordCoreNLP(properties);
		List<List<Label>> sequences = getTreebankAnnotation(contents, depth);
		return printSequences(sequences, true);
	}
	
	/**
	 * Primarily for purposes of unit tests
	 * 
	 * @param contents to parse
	 * @param language
	 * @return 
	 * @return String of output
	 */
	public List<Triplet<String, String, Integer>> parseStringAndExtractProductions(String contents, String language, int depth){

		Properties properties = new Properties();
		setProperties(language, properties);
		this.pipeline = new StanfordCoreNLP(properties);
		List<List<Label>> sequences = getTreebankAnnotation(contents, depth);
		printSequences(sequences, true);

		return extractSequences(sequences);

	}
	
	
	
	
	/**
	 * For each document:
	 * <li>		Read in source text and construct parse tree. 
	 * <li>		(Remove terminals, so that leaf nodes are POS tags.)
	 * <li>		Extract grammatical productions of form LHS -> RHS, to given depth 
	 *  @return List of POS labels for extracted sequence
	 * @param depth indicates the depth of the tree to be rendered
	 */
	public List<List<Label>> getTreebankAnnotation(String docAsString, int depth){
//		//(ROOT (S (PP (IN In) (NP (NN fact))) (, ,) (NP (DT the) (NN debate) (NN today)) (VP (VBZ is) (PP (ADVP (RB no) (RB longer)) (PP (IN on) (NP (DT the) (NNS measures))) (, ,) (CC but) (PP (IN on) (NP (NP (DT the) (NN quantity)) (PP (IN of) (NP (NNS measures)))))) (S (VP (TO to) (VP (VP (VB take)) (CC and) (VP (NP (WRB how)) (ADVP (RB quickly))))))) (. .)))
  		//(ROOT (S (S (ADVP (RB Indeed)) (, ,) (NP (DT the) (NN debate)) (ADVP (RB nowadays)) (VP (VBZ is) (RB not) (ADJP (IN about)) (SBAR (SBAR (WHNP (WP what)) (S (VP (TO to) (VP (VB do))))) (, ,) (CC but) (SBAR (WHNP (WRB how) (JJ much)) (S (VP (TO to) (VP (VB do)))))))) (, ,) (CC and) (FRAG (WHADVP (WRB how)) (ADJP (JJ fast))) (. .)))
	
		StringBuffer markup = new StringBuffer();
		
		//TODO: DONT CALL THIS EACH TIME !!! 
		List<CoreMap> sentences = getAnnotatedDocument(docAsString);
		
		//TEST: SHUFFLE
		//Collections.shuffle(sentences);
		
		List<List<Label>> sequences = new ArrayList<List<Label>>();
		//parse(new DocumentPreprocessor(PTBTokenizerFactory.newWordTokenizerFactory("americanize=false")).getWordsFromString(str));
		List<Label> previousSequence = null;
		
		for(CoreMap sentence: sentences) {
			
			//FileOutputUtils.writeDebugToFile(debugFile, "\n sentence: "+sentence);
			System.out.println( " sentence: "+sentence);
			
			
			// this is the parse tree of the current sentence
			Tree root = sentence.get(TreeAnnotation.class);
			//int d = root.depth();
			//System.out.println( "FLATTENED: "+root.flatten());
			System.out.println( " depth: "+root.depth());
			System.out.println( " no. children: "+root.numChildren());
			
		
			//CollinsHeadFinder headFinder = new CollinsHeadFinder();
			//root.percolateHeads(headFinder);
			//Tree head = headFinder.determineHead(root);
			//getHead(head, root, headFinder);
			
			
			List<Label> sequence = new ArrayList<Label>();
			//to given depth, d
			
			//for(int d = 0; d<depth; d++){
				Tree[] children = getChildren(root, depth, sequence);
				for(Tree child: children){
					//System.out.println( "CHILD flattened="+child.flatten());
					System.out.println( "add label "+child.label() +"  for child tree "+child);
					//annotate with left most leaf that they dominate
					System.out.println( "dominates= "+child.dominates(child.getChild(0)));
					if(type==SEQUENCES_TYPE){
						System.out.println( "add suffix "+child.getChild(0).label()+" for leftmost= "+child.getChild(0));
					}else{
						System.out.print( "PRODUCTION: "+child.label()+"->");
						for(Tree gchild : child.children()){
							System.out.print(gchild.label()+" ");
						}System.out.print("\n");
					}
					
					//if not simply punctuation
					if(isPunctuation(child.label()) == false && child.getChild(0).isLeaf()==false){
						
						//check for left-most leaf that the node dominates
						//if(child.getChild(0).isLeaf())
						
						Label label = child.label(); 
						if(type==SEQUENCES_TYPE){
							StringBuffer annotatedLabel = new StringBuffer(label.toString()+"*"+child.getChild(0).label().toString().toLowerCase());
							label.setValue(annotatedLabel.toString());
							sequence.add(label);
						}else{
							StringBuffer annotatedLabel = new StringBuffer(label.toString()+"->");
							for(Tree gchild : child.children()){
								annotatedLabel.append(gchild.label()+" ");
							}
							label.setValue(annotatedLabel.toString().trim());
							sequence.add(label);
						}
					//}else{
					}else if(isPunctuation(child.label()) == false){//dont add punctuation
						sequence.add(child.label());
					}
					
				}
			sequences.add(sequence);
			//System.out.println( "tree: "+tree.pennString());
			System.out.println( "tree: "+root);
			
			//tree.pennPrint();
			markup.append('\n');
			markup.append(root);
			
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

	
	private void incrementUnigramCounts(List<Label> sequence){
		System.out.println( "incrementUnigramCounts(): "+sequence);
		for(Label label: sequence){
			addToMap(unigramCounts, label.toString());
		}
	}

	/**
	 * Store consecutive pairs of productions in Map. Increment counts of existing ones.
	 * @param sequences containing previously extracted productions
	 */
	private void addToProductionCounts(List<Label> sequence) {
		System.out.println( "addToProductionCounts(): "+sequence);
		
		String production = getProductionString(sequence);
		
		addToMap(productionCounts,production);
	}

	/**
	 * Store consecutive pairs of productions in Map. Increment counts of existing ones.
	 * @param sequences containing previously extracted productions
	 */
	private void addToMap(Map<String, Integer> map, String production) {
		System.out.println( "map="+map.size());
		if(map.containsKey(production)){
			int frequency =map.get(production);
			frequency ++;
			map.put(production, frequency);
		}else{
			map.put(production, 1);
		}
	}

	private String getProductionString(List<Label> sequence) {
		StringBuffer buffer = new StringBuffer();
		for(Label label : sequence){
			buffer.append(label);
			buffer.append(" ");
		}
		String production = buffer.toString().trim();
		return production;
	}

	
	private StringBuffer printSequences(List<List<Label>> sequences, boolean test) {
		StringBuffer buffer = new StringBuffer();
		for(List<Label> sequence: sequences){
			System.out.print("\n sequence : ");
			for(Label label :sequence){
				System.out.print(label+" ");
				buffer.append(label);
				buffer.append(" ");	
			}
			if(!test)buffer.append("\n");
		}
		return buffer;
	}
	
	/** Computes the frequencies of the productions over the corpus, to determine the coherence of a text.
	 * compute a list of all productions that occur more than 25?? times 
	 * ( A. Louis threshold for WSJ section 0 with 1727 sentence pairs over 99 docs).
	 * Ours is similar in length. 
	 */
	public Map<String, Integer> countFrequentProductions() {
		Map<String, Integer> over25 = new HashMap<String, Integer>(); 
		//get all sequences of this type , and log count
	
		for(Entry<String, Integer> entry:	productionCounts.entrySet()){
			System.out.print("countFrequentProductions() : "+entry.getKey()+" count="+ entry.getValue());
			if(entry.getValue() > 25){
				over25.put(entry.getKey(), entry.getValue());
			}
		}
		return over25;
	}
	
	
	/**
	 * provided for unit testing
	 * @return
	 */
	public Map<String, Integer> getProductionCounts() {
		return this.productionCounts;
	}
	
	/**
	 * provided for unit testing
	 * @return
	 */
	public StringBuffer getCollatedProductionCounts() {
		StringBuffer buffer = new StringBuffer();
		buffer.append("\n Production counts \n");
		for(Entry<String, Integer> production : this.productionCounts.entrySet()){
			buffer.append(production.getKey()+" \t "+production.getValue()+" \n");
		}
		
		buffer.append("\n Unigram counts \n");
		for(Entry<String, Integer> production : this.unigramCounts .entrySet()){
			buffer.append(production.getKey()+" \t "+production.getValue()+" \n");
		}
		
		return buffer;
	}
	
	/**
	 * Extract consecutive productions, and store new ones in Map. Increment counts of existing ones.
	 * @param sequences containing previously extracted productions
	 * @return 
	 */
	public List<Triplet<String, String, Integer>> extractSequences(List<List<Label>> sequences) {
		
		//List<Label> firstSequence = " ";
		String firstProduction = "";
		List<Label> previousSequence = null;
		for(List<Label> sequence: sequences){
			 
			//System.out.print("sequence : ");
			String secondProduction = getProductionString(sequence);
			addToPairsList(firstProduction, secondProduction);
			firstProduction = secondProduction;
			
			//keep count of productions
			addToProductionCounts(sequence);
			
			incrementUnigramCounts(sequence);
			
			
			previousSequence = sequence;
		}
		return this.productions;
	}

	
	

	/**
	 * Track list of pairs of productions. 
	 * @param firstProduction
	 * @param secondProduction
	 */
	private void addToPairsList(String firstProduction, String secondProduction) {
		
		boolean found = false;
		System.out.println("addToList() : "+firstProduction.toString()+" AND "+secondProduction.toString());
		
		// check if this pair exists
		for(Triplet<String, String, Integer> t : this.productions){
			System.out.println("checking equality: "+t.getValue0()+" and "+t.getValue1());
			//TODO ???????????????
			if(t.getValue0().equals(firstProduction) && t.getValue1().equals(secondProduction)){	
				//check if second is same
				//if(t.getValue1().equals(secondProduction)){
					//increment
					int temp = t.getValue2().intValue();
					temp++;
					Triplet<String, String, Integer> updatedTuple = t.setAt2(new Integer(temp));
					System.out.println("addToList :FOUND- count now "+updatedTuple.getValue2());
					this.productions.remove(t);
					this.productions.add(updatedTuple);
					found = true;
					break;
				//}else{
					
				//}
			}
		}		
		if(!found){System.out.println("addToList() : not found..adding it");
			//add if not
			this.productions.add(new Triplet<String,String,Integer>(firstProduction, secondProduction, new Integer(1)));
		}
		
	}

	
	
	private Tree[] getChildren(Tree root, int depth, List<Label> sequence) {
		
		depth--;
		//Tree[] children = root.children();
		
		CollinsHeadFinder headFinder = new CollinsHeadFinder();
		Tree head = headFinder.determineHead(root);
		System.out.println( "Head for "+root+"\n is "+head);
		
		while(depth > 0){
			System.out.println( "Tree[] getChildren parent="+root.label());
			for(Tree child: root.children()){
				System.out.println( " child="+child.label()+" no. children="+child.numChildren()+" d="+depth);
				/*if(depth==0){
					System.out.println( "*add label "+child.label());
					sequence.add(child.label());
				}*/
				return getChildren(child, depth, sequence);
			}
		}
		//return getChild(child, depth);
		
		return root.children();
	}
				
	/**
	 * Read in source text and invoke coreference resolve to identify entities.
	 */
	private List<CoreMap> getAnnotatedDocument(String docAsString){
		Annotation document = new Annotation(docAsString);
		this.pipeline.annotate(document);
		List<CoreMap> sentences = document.get(SentencesAnnotation.class);		
		
		return sentences;
	}
	private static String getTagger(String language) {
		switch(language){
			case FRENCH: return FRENCH_TAGGER;
			case GERMAN: return GERMAN_TAGGER;
		}
		return null;
	}
}
