package nlp.framework.discourse;

public class EntityGridFactory {

	private static final String FRENCH = "French";
	private static final String GERMAN = "German";
	
	
	public EntityGridFramework getEntityGridFramework(String language, String url){
		switch(language){
			case GERMAN: return new GermanEntityGridFramework(url);
			case FRENCH: return new FrenchEntityGridFramework(url);
			default: return new EntityGridFramework();
		}
	}
}
