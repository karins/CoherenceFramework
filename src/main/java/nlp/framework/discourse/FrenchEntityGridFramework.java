package nlp.framework.discourse;

import java.io.File;
import java.util.Properties;

import edu.stanford.nlp.pipeline.StanfordCoreNLP;


/**
 * Extends the parent class to add functionality pertinent to a model for the French language.
 * @author Karin Sim
 *
 */
public class FrenchEntityGridFramework  extends EntityGridFramework {

	public static final String FRENCH_PARSER = "edu/stanford/nlp/models/lexparser/frenchFactored.ser.gz";
	public static final String FRENCH_TAGGER = "edu/stanford/nlp/models/pos-tagger/french/french.tagger";
	protected Properties properties;
	
	public FrenchEntityGridFramework() {
		super();
		properties = new Properties();	
		properties.put("-parseInside", "HEADLINE|P");
		properties.put("annotators", "tokenize, ssplit, pos, lemma, parse");
		properties.put("parse.flags", "");
		properties.put("parse.model", FRENCH_PARSER);
		properties.put("pos.model", FRENCH_TAGGER);
		//properties.put("parse.originalDependencies", true);
		//properties.put("pos.model","models/french.tagger");	
		 
		this.pipeline = new StanfordCoreNLP(properties);
		System.out.println("USING PARSER= "+FRENCH_PARSER+" TAGGER= "+FRENCH_TAGGER);
		System.out.println("USING PARSER= "+properties.get("parse.model")+" TAGGER= "+properties.get("pos.model"));
	}
}
