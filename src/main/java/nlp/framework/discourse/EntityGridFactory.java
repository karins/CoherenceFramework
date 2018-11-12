package nlp.framework.discourse;



public class EntityGridFactory {

	private static final String FRENCH = "French";
	private static final String GERMAN = "German";
	private static final String SPANISH = "Spanish";
	
	
	public EntityGridFramework getEntityGridFramework(String language){
		switch(language){
			case GERMAN: return new GermanEntityGridFramework();
			case FRENCH: return new FrenchEntityGridFramework();
			case SPANISH: return new SpanishEntityGridFramework();
			default: return new EntityGridFramework();
		}
	}
}
