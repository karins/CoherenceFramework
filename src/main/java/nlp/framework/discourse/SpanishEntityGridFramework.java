package nlp.framework.discourse;

import java.util.Properties;

import edu.stanford.nlp.pipeline.StanfordCoreNLP;

/**
 * Extends the parent class to add functionality pertinent to a model for the Spanish language.
 * @author Karin Sim
 *
 */
public class SpanishEntityGridFramework extends FrenchEntityGridFramework {
	public static final String SPANISH_PARSER = "edu/stanford/nlp/models/lexparser/spanishPCFG.ser.gz";
	public static final String SPANISH_TAGGER = "edu/stanford/nlp/models/pos-tagger/spanish/spanish-distsim.tagger";//spanish.tagger";
	
	public SpanishEntityGridFramework() {
		super();
		this.properties.put("parse.model", SPANISH_PARSER);
		this.properties.put("pos.model", SPANISH_TAGGER);
		//properties.put("parse.originalDependencies", true);
		//properties.put("pos.model","models/french.tagger");	
		 
		this.pipeline = new StanfordCoreNLP(this.properties);
		System.out.println("USING PARSER= "+SPANISH_PARSER+" TAGGER= "+SPANISH_TAGGER);
	}
}
