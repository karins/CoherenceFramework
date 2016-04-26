package nlp.framework.discourse;

public class LanguageConfiguration {

	private static final String FRENCH = "French";
	private static final String GERMAN = "German";
	private static final String SPANISH = "Spanish";
	private static final String ENGLISH = "English";
	
	public static String getTagger(String language) {
		switch(language){
			case FRENCH: return FrenchEntityGridFramework.FRENCH_TAGGER;
			case GERMAN: return GermanEntityGridFramework.GERMAN_TAGGER;
			case SPANISH: return SpanishEntityGridFramework.SPANISH_TAGGER;
		}
		return null;
	}
	public static String getParser(String language) {
		switch(language){
			case FRENCH: return FrenchEntityGridFramework.FRENCH_PARSER;
			case GERMAN: return GermanEntityGridFramework.GERMAN_PARSER;
			case SPANISH: return SpanishEntityGridFramework.SPANISH_PARSER;
		}
		return null;
	}
	
}
