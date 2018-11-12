package nlp.framework.discourse;

import java.io.File;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;

import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.ling.CoreAnnotations.PartOfSpeechAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.SentencesAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TokensAnnotation;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.semgraph.SemanticGraph;
import edu.stanford.nlp.semgraph.SemanticGraphCoreAnnotations.BasicDependenciesAnnotation;
import edu.stanford.nlp.semgraph.SemanticGraphEdge;
import edu.stanford.nlp.trees.EnglishGrammaticalRelations;
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
	private static final String NC = "NC";
	private static final String NPP = "NPP";
	//Spanish tags:
	private static final String nc00000 = "nc00000";
	private static final String nc0n000 = "nc0n000";
	private static final String nc0p000 = "nc0p000";	
	private static final String nc0s000 = "nc0s000";
	private static final String np00000 = "np00000";
	
	
	//private Set<String> POS_TAGS = new HashSet<String>(){NNP, NP, NNS, NN, N, NE};
	public static final String ENGLISH_PARSER = "edu/stanford/nlp/models/parser/nndep/english_SD.gz";
	public static final String ENGLISH_TAGGER = "models/english-left3words-distsim.tagger";
	//public static final String GERMAN_TAGGER = "/stanford-corenlp-3.5.2-models-german/stanford-corenlp-3.5.2-models-german/models/german-fast.tagger";
	//public static final String FRENCH_TAGGER = "/pos-tagger/french.tagger";
	private static final String FRENCH = "French";
	private static final String GERMAN = "German";
	private static final String SPANISH = "Spanish";
	private static final String ENGLISH = "English";
	private static final int SALIENCE = 2;
	protected static final boolean DEBUG = true;
	protected static String debugFile = "debug";
	protected static StringBuffer buffer = new StringBuffer();
	
	protected StanfordCoreNLP pipeline;
	protected Properties properties;
	private char grid[][];
	//private int sentences; 
	
	
	/**
	 * Default grid is English-based
	 * @param language
	 */
	public EntityGridFramework() {
	
		properties = new Properties();	
		properties.put("-parseInside", "HEADLINE|P");
		properties.put("annotators", "tokenize, ssplit, pos, lemma, parse");
		properties.put("parse.originalDependencies", true);
		//properties.setProperty("tokenize.whitespace", "true");//for annotator tokenize
		//properties.setProperty("ssplit.eolonly", "true");//for annotator ssplit
		properties.put("ssplit.eolonly", "true");//for annotator ssplit

		this.pipeline = new StanfordCoreNLP(properties);	
	}

	/**
	 * Default grid is English-based
	 * @param language
	 */
	public EntityGridFramework(String urlForPOStagger, String urlForParseModel) {
	
		Properties properties = new Properties();	
		properties.put("-parseInside", "HEADLINE|P");
		properties.put("annotators", "tokenize, ssplit, pos, lemma, parse");
		// properties.setProperty("tokenize.whitespace", "true");//for annotator tokenize
		//properties.setProperty("ssplit.eolonly", "true");//for annotator ssplit
		//properties.put("parse.model", "edu/stanford/nlp/models/lexparser/frenchFactored.ser.gz");
		properties.put("parse.model",urlForParseModel);
		properties.put("pos.model",urlForPOStagger);
		properties.put("ssplit.eolonly", "true");//for annotator ssplit
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
		
		if(Boolean.valueOf(multiple) == Boolean.TRUE){
			
			EntityGridFramework gridframework = new EntityGridFactory().getEntityGridFramework(language);
			Map<String, String> docs = new CorpusReader().readXML(filename);
			int fileidx = 0;
			for(String docAsString: docs.values()){
				buffer = new StringBuffer();
				if(DEBUG)debugFile = outputfile+fileidx+"_debug";
				char grid [][] = gridframework.identifyEntitiesAndConstructGrid(docAsString);
				new FileOutputUtils().writeGridToFile(outputfile+fileidx, grid);
				if(DEBUG)FileOutputUtils.writeDebugToFile(debugFile, buffer.toString());
				fileidx++;
			}
		}
		else{
			
			EntityGridFramework gridframework = new EntityGridFramework();
			String doc = CorpusReader.readDataAsString(filename);
		
			char grid [][] = gridframework.identifyEntitiesAndConstructGrid(doc);
			new FileOutputUtils().writeGridToFile(outputfile, grid);
		}
	} 
	
	/*
	private static String getTagger(String language) {
		switch(language){
			case FRENCH: return FrenchEntityGridFramework.FRENCH_TAGGER;
			case GERMAN: return GermanEntityGridFramework.GERMAN_TAGGER;
			case SPANISH: return SpanishEntityGridFramework.SPANISH_TAGGER;
		}
		return null;
	}
	private static String getParser(String language) {
		switch(language){
			case FRENCH: return FrenchEntityGridFramework.FRENCH_PARSER;
			case GERMAN: return GermanEntityGridFramework.GERMAN_PARSER;
			case SPANISH: return SpanishEntityGridFramework.SPANISH_PARSER;
		}
		return null;
	}*/

	
	/**
	 * Read in source text and invoke coreference resolver to identify entities.
	 */
	public Map<String, ArrayList<Map <Integer, String>>> identifyEntitiesFromSentences(String docAsString){
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
		
		return constructGrid(entities, sentences.size());
	}
	/**
	 * Read in source text and invoke annotations.
	 * @param List of annotated sentences
	 */
	protected List<CoreMap> getAnnotatedDocument(String docAsString){
		Annotation document = new Annotation(docAsString);
		this.pipeline.annotate(document);
		List<CoreMap> sentences = document.get(CoreAnnotations.SentencesAnnotation.class);
 		//List<CoreMap> sentences = document.get(SentencesAnnotation.class);
		//Map<String, ArrayList<Map <Integer, String>>> entities = identifyEntities(sentences);
		
		return sentences;
	}
	
	
	
	/**
	 * Read in source text and invoke coreference resolve to identify entities.
	 */
	public char[][] getConstructedGrid(Map<String, ArrayList<Map <Integer, String>>> entities, int numberOfSentences){
		
		return constructGrid(entities, numberOfSentences);
	}
	
	/**
	 * 
	 * @param sentences
	 * @return
	 */
	public Map<String, ArrayList<Map<Integer, String>>> identifyEntities(List<CoreMap> sentences ){
		
		Map<String, ArrayList<Map <Integer, String>>> entities = new HashMap<String, ArrayList<Map <Integer, String>>>();
		
		//FileOutputUtils.writeDebugToFile(debugFile, "doc= "+docAsString+"\n sentences: "+sentences);
		buffer.append("sentences: "+sentences.size());
			
		int idx = 0;
		for(CoreMap sentence: sentences) {
						
			//FileOutputUtils.writeDebugToFile(debugFile, "\n sentence: "+sentence);
			buffer.append( "\n "+idx+ " sentence: "+sentence);
			
			for (CoreLabel token: sentence.get(TokensAnnotation.class)) {
			
				String ner = token.ner();
				String POS = token.get(PartOfSpeechAnnotation.class);
				System.out.println("POS "+POS+ " for "+token.lemma());

				//In French: "NC","NPP" = NOUN
				/*if(POS.equalsIgnoreCase(NNP)|| POS.equalsIgnoreCase(NP)|| POS.equalsIgnoreCase(NNS)
						|| POS.equalsIgnoreCase(NN) || POS.equalsIgnoreCase(N)|| POS.equalsIgnoreCase(NE)
						|| POS.equalsIgnoreCase(NC)|| POS.equalsIgnoreCase(NPP)){*/
				if(isNoun(POS)){
					
					//get the Stanford dependency graph of the current sentence
					SemanticGraph dependencies = sentence.get(BasicDependenciesAnnotation.class);
					boolean isSubjOrObj = false;
					
					if(dependencies != null){
						for(SemanticGraphEdge edge: dependencies.edgeIterable()) {
							if(token.get(CoreAnnotations.ValueAnnotation.class).equals(edge.getTarget().get(CoreAnnotations.ValueAnnotation.class))){
								GrammaticalRelation relation = edge.getRelation();
								
								isSubjOrObj = determineGrammaticalRelation(	entities, idx, token, relation);	
							}
						}
					}
					if(isSubjOrObj == false) {
						System.out.println("found: "+token.lemma());
						trackEntity(token.lemma(), idx, X, entities);
					}
				}
			}idx++;			
		}return entities;
	}

	private boolean isNoun(String POS_tag){
		
		if(POS_tag.equalsIgnoreCase(NNP)|| POS_tag.equalsIgnoreCase(NP)|| POS_tag.equalsIgnoreCase(NNS)
		|| POS_tag.equalsIgnoreCase(NN) || POS_tag.equalsIgnoreCase(N)|| POS_tag.equalsIgnoreCase(NE)
		|| POS_tag.equalsIgnoreCase(NC)|| POS_tag.equalsIgnoreCase(NPP)){
			return true;
		}else if(POS_tag.equalsIgnoreCase(nc00000) ||  POS_tag.equalsIgnoreCase(nc0n000)  || POS_tag.equalsIgnoreCase(nc0p000)
				|| POS_tag.equalsIgnoreCase(nc0s000) || POS_tag.equalsIgnoreCase(np00000)){
			/* Spanish noun tags:
			nc00000	Unknown common noun (neologism, loanword)	minidisc, hooligans, re-flotamiento
			nc0n000	Common noun (invariant number)	hipÃ³tesis, campus, golf
			nc0p000	Common noun (plural)	aÃ±os, elecciones
			nc0s000	Common noun (singular)	lista, hotel, partido
			np00000	Proper noun	MÃ¡laga, Parlamento, UFINSA */
			return true;
		}else if (POS_tag.equalsIgnoreCase("ADJ")){//TODO: sort this hack for French!!!
			return true;
		}
		
		return false;
	}

	private boolean determineGrammaticalRelation(
			Map<String, ArrayList<Map<Integer, String>>> entities, int idx,
			CoreLabel token, GrammaticalRelation relation) {
		/**csubj,  csubjpass, {xsubj}: controlling subject}, subj,  nsubj (nominal subject), nsubjpass
			I should maybe also have tracked nsubjpass (passive nominal subject)
			and csubj (clausal subject).
			And instead of just  pobj (object of a preposition) 
			maybe also dobj ( direct object) and iobj ( indirect object )
			*/	 
		boolean isSubjOrObj = false;
		if(	relation.getShortName() == EnglishGrammaticalRelations.PREPOSITIONAL_OBJECT.getShortName() 
			|| relation.getShortName() == EnglishGrammaticalRelations.OBJECT.getShortName()
			|| relation.getShortName() == EnglishGrammaticalRelations.DIRECT_OBJECT.getShortName()
			|| relation.getShortName() == EnglishGrammaticalRelations.INDIRECT_OBJECT.getShortName()
			//|| relation.getShortName() == UniversalGrammaticalRelations.NOMINAL_MODIFIER.getShortName()
			){//pobj: nmod pobj has changed to nmod in Stanford nlp 3.5.2
			trackEntity(token.lemma(), idx, O, entities);
			//System.out.println("found: "+token.lemma()+"  as "+relation);
			isSubjOrObj = true;
		}else if(relation.getShortName() == EnglishGrammaticalRelations.SUBJECT.getShortName()
				||relation.getShortName() == EnglishGrammaticalRelations.CLAUSAL_SUBJECT.getShortName()
				||relation.getShortName() == EnglishGrammaticalRelations.CLAUSAL_PASSIVE_SUBJECT.getShortName()
				||relation.getShortName() == EnglishGrammaticalRelations.NOMINAL_SUBJECT.getShortName()
				||relation.getShortName() == EnglishGrammaticalRelations.NOMINAL_PASSIVE_SUBJECT.getShortName()){
			
			trackEntity(token.lemma(), idx, S, entities);
			//System.out.println("found: "+token.lemma()+"  as "+relation);
			isSubjOrObj = true;
		}System.out.println("found: "+token.lemma()+"  as "+relation+" returning "+isSubjOrObj);
		return isSubjOrObj;
	}

	/**
	 * @param entities is Map for tracking occurances in format : "word"->list of : sentence_number->grammatical_role
	 * @param lemma is the entity
	 * @param idx is the index of the sentence currently being examined
	 * @param grammaticalRole is the grammatical role played by this entity in this particular instance 
	 */
	protected void trackEntity(String lemma, int idx, char grammaticalRole, Map<String, ArrayList<Map<Integer, String>>> entities) {
		
		//format : "word"->list of : sentence_number->grammatical_role
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
	public char[][] constructGrid(Map<String, ArrayList<Map <Integer, String>>> entities, int numberOfSentences) {
		this.grid = new char[numberOfSentences ][entities.size()];
		
		int entityIndex = 0;
		for(String entity : entities.keySet()){
			List <Map <Integer, String>> occurances = entities.get(entity);
			String lexicalInfo = "\n entity: "+entity+" at "+occurances;
			//FileOutputUtils.writeDebugToFile(debugFile, lexicalInfo);
			buffer.append( lexicalInfo);
			
			//only track salient entities: UPDATE: moved this to Python script, as then can derive from existing grids
			//if(occurances.size() >= SALIENCE){
				for(Map <Integer, String> occurance : occurances){
					Integer sentence = occurance.keySet().iterator().next();
					grid[sentence][entityIndex] = occurance.get(sentence).charAt(0);
				}
				entityIndex++;
			//}
		}			
		return grid;
	}
	
}
