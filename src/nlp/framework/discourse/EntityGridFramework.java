package nlp.framework.discourse;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.Set;

import edu.stanford.nlp.dcoref.CorefChain;
import edu.stanford.nlp.dcoref.CorefCoreAnnotations.CorefChainAnnotation;
import edu.stanford.nlp.ie.machinereading.structure.AnnotationUtils;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.ling.CoreAnnotations.NamedEntityTagAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.PartOfSpeechAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.SentencesAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TokensAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.ValueAnnotation;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.IndexedWord;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.semgraph.SemanticGraph;
import edu.stanford.nlp.semgraph.SemanticGraphCoreAnnotations.BasicDependenciesAnnotation;
import edu.stanford.nlp.semgraph.SemanticGraphCoreAnnotations.CollapsedCCProcessedDependenciesAnnotation;
import edu.stanford.nlp.semgraph.SemanticGraphEdge;
import edu.stanford.nlp.trees.GrammaticalRelation;
import edu.stanford.nlp.util.CoreMap;

/**
 * Constructs an entity grid from a given file. The file may be English, French or German.
 * The entity grid uses the Stanford Parser to identify all nouns in the input text.
 * For the English version it additionally determines the grammatical role played by that entity in each particular occurance. 
 * The various options are set on the commandline, to ensure correct parser is set.
 * 
 * @author Karin Sim
 *
 */
public class EntityGridFramework {

	protected static final char EMPTY = '-';
	protected static final char O = 'O';
	protected static final char S = 'S';
	protected static final char X = 'X';
	
	private static final String NNP = "NNP";
	private static final String NNS = "NNS";
	private static final String NP = "NP";
	private static final String NN = "NN";
	private static final String N = "N";
	private static final String NE = "NE";
	
	//private Set<String> POS_TAGS = new HashSet<String>(){NNP, NP, NNS, NN, N, NE};
	
	public static final String GERMAN_TAGGER = "C:\\SMT\\StanfordNLP\\stanford-postagger-full-2013-11-12\\stanford-postagger-full-2013-11-12\\models\\german-fast.tagger";
	public static final String FRENCH_TAGGER = "C:\\SMT\\StanfordNLP\\stanford-postagger-full-2013-11-12\\stanford-postagger-full-2013-11-12\\models\\french.tagger";
	private static final String FRENCH = "French";
	private static final String GERMAN = "German";
	private static final String ENGLISH = "English";
	//private static final int SALIENCE = 2;
	protected static final boolean DEBUG = true;
	protected static String debugFile = "debug";
	protected static StringBuffer buffer = new StringBuffer();
	
	protected StanfordCoreNLP pipeline;
	private char grid[][];
	private int sentences;
	
	
	/*public EntityGridFramework( boolean isTest) {
		Properties properties = new Properties();
		properties.put("annotators", "tokenize, ssplit, pos, lemma, ner, parse, dcoref");
		properties.put("-parseInside", "HEADLINE|P");
		
		this.pipeline = new StanfordCoreNLP (properties);
	}*/
	
	/*public EntityGridFramework() {
	
		Properties properties = new Properties();	
		properties.put("-parseInside", "HEADLINE|P"); 
		properties.put("annotators", "tokenize, ssplit, pos, lemma, parse");
		this.pipeline = new StanfordCoreNLP(properties);
	}*/
	
	/**
	 * Default grid is English-based
	 * @param language
	 */
	public EntityGridFramework() {
	
		/*if(GERMAN.equalsIgnoreCase(language)){
			//TODO: CHANGE FROM HARDCODED LOCATION!!
			props.put("pos.model", "C:\\SMT\\StanfordNLP\\stanford-postagger-full-2013-11-12\\stanford-postagger-full-2013-11-12\\models\\german-fast.tagger");		
			props.put("parse.flags", "");
			props.put("parse.model", "edu/stanford/nlp/models/lexparser/germanPCFG.ser.gz");
			//props.put("outputFormat", "typedDependencies"); 
		}
		else if(FRENCH.equalsIgnoreCase(language)){
			props.put("parse.flags", "");
			props.put("parse.model", "edu/stanford/nlp/models/lexparser/frenchFactored.ser.gz");
			//TODO: CHANGE FROM HARDCODED LOCATION!!
			props.put("pos.model", "C:\\SMT\\StanfordNLP\\stanford-postagger-full-2013-11-12\\stanford-postagger-full-2013-11-12\\models\\french.tagger");
		}*/
		Properties properties = new Properties();	
		properties.put("-parseInside", "HEADLINE|P");
		properties.put("annotators", "tokenize, ssplit, pos, lemma, parse");
		this.pipeline = new StanfordCoreNLP(properties);	
	}
	

	/**
	 * The various options are set on the commandline, to ensure correct parser is set.
	 * In the following format and order:
	 * inputfile, outputfile, containsMultipleDocs , language, isXml
	 * eg. "C:\\SMT\\datasets\\corpus-PE\\corpus\\PEofMT_2ndHalf.mt" "C:\\SMT\\datasets\\corpus-PE\\newSyntax\\PEofMT_2ndHalf.mt.grid" "true" "English" "true"
	 * @param args
	 * @param containsMultipleDocs is a boolean reflecting whether the input file is marked up with <doc> tags, identifying the various documents
	 * @param language is one of English  French or German
	 * @param  isXml indicates whether input should be read as xml (contains markup, or is simply test string)
	 */
	public static void main(String[] args) {
		
		String filename = args[0];
		String outputfile = args[1];
		String multiple = args[2];
		String language = args[3]; 
		boolean isXML = new Boolean(args[4]);
		//"C:\\SMT\\StanfordNLP\\stanford-postagger-full-2013-11-12\\stanford-postagger-full-2013-11-12\\models\\german-fast.tagger"
		
		if(Boolean.valueOf(multiple) == Boolean.TRUE){
			
			EntityGridFramework gridframework = new EntityGridFactory().getEntityGridFramework(language, getTagger(language));
			//char grids [][][] = gridframework.identifyEntitiesAndConstructGrids();
			//FileOutputUtils.writeGridsToFile(outputfile, grids);
			List<String> docs = new CorpusReader().readXML(filename, true);
			int fileidx = 0;
			for(String docAsString: docs){
				//Annotation document = new Annotation(docAsString);
				//this.pipeline.annotate(document);
				//documents.add(document);
				buffer = new StringBuffer();
				if(DEBUG)debugFile = outputfile+fileidx+"_debug";
				char grid [][] = gridframework.identifyEntitiesAndConstructGrid(docAsString);
				FileOutputUtils.writeGridToFile(outputfile+fileidx, grid);
				if(DEBUG)FileOutputUtils.writeDebugToFile(debugFile, buffer.toString());
				fileidx++;
			}
		}else if(isXML){
			EntityGridFramework gridframework = new EntityGridFramework();
			List<String> docs = new CorpusReader().readXML(filename, false);
			//List<CoreMap> sentences = AnnotationUtils.readSentencesFromFile(filename);
			if(DEBUG)debugFile = outputfile+"_debug";
			char grid [][] = gridframework.identifyEntitiesAndConstructGrid(docs.get(0));
			FileOutputUtils.writeGridToFile(outputfile, grid);
			if(DEBUG)FileOutputUtils.writeDebugToFile(debugFile, buffer.toString());
		}		
		else{
			//String filename = "C:\\SMT\\datasets\\news-commentary-v8.fr-en.en";
			//String filename = "C:\\SMT\\datasets\\training-monolingual-nc-v8\\training\\news-commentary-v8.en";
			
			//works:String filename = "C:\\SMT\\datasets\\extract_news_commentary.txt";
			//String filename = "C:\\SMT\\datasets\\mini-test.txt";
			//String filename = "C:\\SMT\\datasets\\corpus.en";
			EntityGridFramework gridframework = new EntityGridFramework();
			String doc = CorpusReader.readDataAsString(filename);
			//Map<String, ArrayList<Map <Integer, String>>> entities = gridframework.identifyEntitiesAndConstructGrid(doc);
			char grid [][] = gridframework.identifyEntitiesAndConstructGrid(doc);
			//output to file:
			//CorpusReader.writeGridToFile("C:\\SMT\\grid-mini-test", grid);
			//CorpusReader.writeGridToFile("C:\\SMT\\news-commentary-grid", grid);
			//works:CorpusReader.writeGridToFile("C:\\SMT\\extract-news-commentary-grid", grid);
			//outputs single grid:
			FileOutputUtils.writeGridToFile(outputfile, grid);
		}
	} 
	
	
	private static String getTagger(String language) {
		switch(language){
			case FRENCH: return FRENCH_TAGGER;
			case GERMAN: return GERMAN_TAGGER;
		}
		return null;
	}

	/**
	 * Read in source text and invoke coreference resolve to identify entities.
	 */
	/*public char[][] identifyEntitiesAndConstructGrid(String docAsString){
		Annotation document = new Annotation(docAsString);
		this.pipeline.annotate(document);
		List<CoreMap> sentences = document.get(SentencesAnnotation.class);
		Map<String, ArrayList<Map <Integer, String>>> entities = identifyEntities(sentences);
		
		return constructGrid(entities);
	}*/
	
	
	/**
	 * Read in source text and invoke coreference resolve to identify entities.
	 */
	public Map<String, ArrayList<Map <Integer, String>>> identifyEntitiesForGraph(String docAsString){
		List<CoreMap> sentences = getAnnotatedDocument(docAsString);
		Map<String, ArrayList<Map <Integer, String>>> entities = identifyEntities(sentences);
		
		return entities;
	}
	
	/**
	 * Read in source text and invoke coreference resolve to identify entities.
	 */
	public char[][] identifyEntitiesAndConstructGrid(String docAsString){
		List<CoreMap> sentences = getAnnotatedDocument(docAsString);
		Map<String, ArrayList<Map <Integer, String>>> entities = identifyEntities(sentences);
		
		return constructGrid(entities);
	}
	/**
	 * Read in source text and invoke coreference resolve to identify entities.
	 */
	private List<CoreMap> getAnnotatedDocument(String docAsString){
		Annotation document = new Annotation(docAsString);
		this.pipeline.annotate(document);
		List<CoreMap> sentences = document.get(SentencesAnnotation.class);
		//Map<String, ArrayList<Map <Integer, String>>> entities = identifyEntities(sentences);
		
		return sentences;
	}
	
	
	/**
	 * Read in source text and invoke coreference resolve to identify entities.
	 */
	public char[][] getConstructedGrid(Map<String, ArrayList<Map <Integer, String>>> entities){
		
		return constructGrid(entities);
	}
	
	/**
	 * 
	 * @param sentences
	 * @return
	 */
	public Map<String, ArrayList<Map<Integer, String>>> identifyEntities(List<CoreMap> sentences ){
		
		Map<String, ArrayList<Map <Integer, String>>> entities = new HashMap<String, ArrayList<Map <Integer, String>>>();
		this.sentences = sentences.size();
		
		//FileOutputUtils.writeDebugToFile(debugFile, "doc= "+docAsString+"\n sentences: "+sentences);
		buffer.append("sentences: "+sentences.size());
		
		//Map<Integer, CorefChain> corefgraph = document.get(CorefChainAnnotation.class);		
		
		int idx = 0;
		for(CoreMap sentence: sentences) {
			//FileOutputUtils.writeDebugToFile(debugFile, "\n sentence: "+sentence);
			buffer.append( "\n "+idx+ " sentence: "+sentence);
			
			for (CoreLabel token: sentence.get(TokensAnnotation.class)) {
				String ner = token.ner();
				String entity = token.get(NamedEntityTagAnnotation.class);
				String POS = token.get(PartOfSpeechAnnotation.class);
				
				//Map<Integer, CorefChain> corefgraph = document.get(CorefChainAnnotation.class);
				//String coref = token.get(CorefChainAnnotation.class);
				System.out.println("POS "+POS+ " for "+token.lemma());
				
				if(POS.equalsIgnoreCase(NNP)|| POS.equalsIgnoreCase(NP)|| POS.equalsIgnoreCase(NNS)
						|| POS.equalsIgnoreCase(NN) || POS.equalsIgnoreCase(N)|| POS.equalsIgnoreCase(NE)){
					
					//get the Stanford dependency graph of the current sentence
					//SemanticGraph dependencies = sentence.get(CollapsedCCProcessedDependenciesAnnotation.class);
					
					/*SemanticGraph dependencies = sentence.get(SemanticGraphCoreAnnotations.CollapsedDependenciesAnnotation().getClass());
					for (SemanticGraphEdge edge : dependencies.edgeListSorted()){
						IndexedWord governor = edge.getGovernor();
						IndexedWord dependent = edge.getDependent();
						edge.getRelation();
						governor.
					}*/
					
					SemanticGraph dependencies = sentence.get(BasicDependenciesAnnotation.class);
					boolean isSubjOrObj = false;
					/*
					if(dependencies != null){
						for(SemanticGraphEdge edge: dependencies.edgeIterable()) {
							if(token.get(CoreAnnotations.ValueAnnotation.class).equals(edge.getTarget().get(CoreAnnotations.ValueAnnotation.class))){
								GrammaticalRelation relation = edge.getRelation();
								
								/**csubj,  csubjpass, {xsubj}: controlling subject}, subj,  nsubj (nominal subject), nsubjpass
									I should maybe also have tracked nsubjpass (passive nominal subject)
									and csubj (clausal subject).
									And instead of just  pobj (object of a preposition) 
									maybe also dobj ( direct object) and iobj ( indirect object )
									*/	 
								/*if(relation.equals(GrammaticalRelation.valueOf("pobj")) ||
										relation.equals(GrammaticalRelation.valueOf("dobj"))
												||relation.equals(GrammaticalRelation.valueOf("iobj"))){
									trackEntity(token.lemma(), idx, O, entities);
									//System.out.println("found: "+token.lemma()+"  as "+relation);
									isSubjOrObj = true;
								}else if(relation.equals(GrammaticalRelation.valueOf("subj"))
										||relation.equals(GrammaticalRelation.valueOf("xsubj"))
										||relation.equals(GrammaticalRelation.valueOf("csubj"))
										||relation.equals(GrammaticalRelation.valueOf("csubjpass"))
										||relation.equals(GrammaticalRelation.valueOf("nsubj"))
										||relation.equals(GrammaticalRelation.valueOf("nsubjpass"))){
									
									trackEntity(token.lemma(), idx, S, entities);
									//System.out.println("found: "+token.lemma()+"  as "+relation);
									isSubjOrObj = true;
								}System.out.println("found: "+token.lemma()+"  as "+relation);						
							}
						}
					}*/
					if(isSubjOrObj == false) {
						System.out.println("found: "+token.lemma());
						trackEntity(token.lemma(), idx, X, entities);
					}
				}
			}idx++;
		}
		return entities;
	}

	/**
	 * @param entities is Map for tracking occurances in format : "word"->list of : sentence_number->grammatical_role
	 * @param lemma is the entity
	 * @param idx is the index of the sentence currently being examined
	 * @param grammaticalRole is the grammatical role played by this entity in this particular instance 
	 */
	protected void trackEntity(String lemma, int idx, char grammaticalRole, Map<String, ArrayList<Map<Integer, String>>> entities) {
		
		//track in Map for later
		//format : "word"->list of : sentence_number->grammatical_role
		
		//HashMap <String, HashMap <Integer, String>> entity = this.entities.get(lemma);
		
		//list of all the sentences in which the entity occurs
		ArrayList <Map <Integer, String>> entity = entities.get(lemma);
		
		if(entity == null){//create an entry
			entity = new  ArrayList<Map <Integer, String>> ();
			Map<Integer, String> occurances = new HashMap <Integer, String>();
			occurances.put(idx, String.valueOf(grammaticalRole));
			entity.add(occurances);
			
			entities.put(lemma, entity);
		}
		boolean found = false;
		//check all sentences where it occurs
		for(Map <Integer, String> occurance : entity){
			
			if(occurance.get(idx) != null){
				String role = occurance.get(idx);
				found = true;
				//check if should overwrite with higher grammatical ranking
				if(role.charAt(0) == X || role.charAt(0) == O && grammaticalRole == S){
					occurance.put(idx, String.valueOf(grammaticalRole));
				}
			}
		}
			
		//if hasnt occurred in this sentence yet, add it in
		if(!found){
			Map<Integer, String> occurances = new HashMap <Integer, String>();
			occurances.put(idx, String.valueOf(grammaticalRole));
			entity.add(occurances);
		}
	}

	/**
	 * Constructs a grid from the list of noun occurances over all sentences.
	 * The grid is a 2D array where entities are tracked on the vertical, and each sentence is a horizontal. 
	 * @param entities
	 * @return
	 */	
	public char[][] constructGrid(Map<String, ArrayList<Map <Integer, String>>> entities) {
		this.grid = new char[sentences][entities.size()];
		
		int entityIndex = 0;
		for(String entity : entities.keySet()){
			List <Map <Integer, String>> occurances = entities.get(entity);
			String lexicalInfo = "\n entity: "+entity+" at "+occurances;
			//FileOutputUtils.writeDebugToFile(debugFile, lexicalInfo);
			buffer.append( lexicalInfo);
			
			for(Map <Integer, String> occurance : occurances){
				Integer sentence = occurance.keySet().iterator().next();
				grid[sentence][entityIndex] = occurance.get(sentence).charAt(0);
			}
			entityIndex++;
		}	
		
		return grid;
	}
	
	
}
