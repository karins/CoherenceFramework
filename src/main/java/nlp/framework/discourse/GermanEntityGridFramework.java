package nlp.framework.discourse;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Map;
import java.util.Properties;

import de.danielnaber.jwordsplitter.AbstractWordSplitter;
import de.danielnaber.jwordsplitter.GermanWordSplitter;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;

/**
 * Extends the parent class to add functionality pertinent to a model for the German language.
 * German tagset is based on negra-corpus. http://www.coli.uni-saarland.de/projects/sfb378/negra-corpus/stts.asc
 * @author Karin Sim
 *
 */
public class GermanEntityGridFramework extends EntityGridFramework {

	public static final String GERMAN_PARSER = "edu/stanford/nlp/models/lexparser/germanPCFG.ser.gz";
	public static final String GERMAN_TAGGER = "edu/stanford/nlp/models/pos-tagger/german/german.tagger";
	
	public GermanEntityGridFramework() {
		super();		
		Properties properties = new Properties();	
		properties.put("-parseInside", "HEADLINE|P");
		properties.put("annotators", "tokenize, ssplit, pos, lemma, parse");
		properties.put("pos.model", GERMAN_TAGGER);		
		//properties.put("parse.flags", "");
		//props.put("parse.model", url);
		properties.put("parse.model", GERMAN_PARSER);
		//properties.put("parse.originalDependencies", true);
		//properties.put("parse.model", GERMAN_PARSER);
		this.pipeline = new StanfordCoreNLP(properties);	
		System.out.println("GermanEntityGrid- PARSER= "+GERMAN_PARSER+ " POS TAGGER="+GERMAN_TAGGER);
	}
	/**
	 * In addition to the functionality of the base class, this method applies a compound splitter to the entities. This is because
	 * otherwise the  German compounds result in fewer occurrences in the table, which make a crosslingual comparison more difficult. 
	 * @param entities is Map for tracking occurrences in format : "word"->list of : sentence_number->grammatical_role
	 * @param  entity
	 * @param idx is the index of the sentence currently being examined
	 * @param grammaticalRole is the grammatical role played by this entity in this particular instance
	 */
	protected void trackEntity(String entity, int idx, char grammaticalRole, Map<String, ArrayList<Map<Integer, String>>> entities) {
		
		//track in Map for later
		//format : "word"->list of : sentence_number->grammatical_role
		System.out.println("German compound splitter for: "+entity+" => ");
		//for German we use a compound splitter  on the entity, and then run the code for all the constituents
		Collection<String> compounds  = invokeCompoundSplitter(entity);
		if(compounds != null){
			for(String word: compounds){
				System.out.println(word+", ");
				super.trackEntity(word, idx, grammaticalRole, entities);
			}
		}else{
			super.trackEntity(entity, idx, grammaticalRole, entities);
		}
	}
	
	/**
	 * jWordSplitter 3.5-dev (2012-xx-yy)
	 * Copyright 2004-2007 Sven Abels
	 * Copyright 2007-2013 Daniel Naber
	 * See LICENSE.txt for license information.
	 * Homepage: http://www.danielnaber.de/jwordsplitter
	 */
	public  Collection<String> invokeCompoundSplitter(String wordToSplit){
		AbstractWordSplitter splitter;
		 
		try {
			splitter = new GermanWordSplitter(true);
			splitter.setStrictMode(true);
			Collection<String> parts = splitter.splitWord(wordToSplit);
			System.out.println(parts); 
			return parts;
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return null;
	}



}
