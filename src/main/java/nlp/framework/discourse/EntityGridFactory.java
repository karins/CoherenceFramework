package nlp.framework.discourse;

import java.io.File;

public class EntityGridFactory {

	//public static final String GERMAN_TAGGER = File.pathSeparator+"edu"+File.pathSeparator+"stanford"+File.pathSeparator+"nlp"+File.pathSeparator+"models"+File.pathSeparator+"pos-tagger"+File.pathSeparator+"german"+File.pathSeparator+"german-fast.tagger";
	//public static final String GERMAN_TAGGER = "/stanford-corenlp-3.5.2-models-german/stanford-corenlp-3.5.2-models-german/models/german-fast.tagger";
	//public static final String FRENCH_TAGGER = File.pathSeparator+"edu"+File.pathSeparator+"stanford"+File.pathSeparator+"nlp"+File.pathSeparator+"models"+File.pathSeparator+"pos-tagger"+File.pathSeparator+"french"+File.pathSeparator+"french.tagger";
	//public static final String FRENCH_TAGGER = "/pos-tagger/french.tagger";
	private static final String FRENCH = "French";
	private static final String GERMAN = "German";
	
	
	public EntityGridFramework getEntityGridFramework(String language, String url){
		switch(language){
			case GERMAN: return new GermanEntityGridFramework();
			case FRENCH: return new FrenchEntityGridFramework();
			default: return new EntityGridFramework();
		}
	}
}
