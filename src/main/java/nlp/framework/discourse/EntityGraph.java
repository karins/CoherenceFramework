package nlp.framework.discourse;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import edu.stanford.nlp.ling.CoreAnnotations.SentencesAnnotation;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.util.CoreMap;

/**
 * Creates a graph based model for assessing local coherence.
 * Represents an implementation of the Guinaudeau  and Strube graph experiment, (http://anthology.aclweb.org//P/P13/P13-1010.pdf).
 * This implementation makes use of the groundwork done by EntityGridFramework class, and projects the data onto a graph representation. 
 * 
 * @author Karin Sim
 *
 */
public class EntityGraph{ 

	private String language;
	private EntityGridFramework entityGrid;
	/*public EntityGraph(boolean test){
		super(test);
	}*/
	public EntityGraph(String language, EntityGridFramework entityGridFramework) {
		this.language = language;
		this.entityGrid = entityGridFramework;
	}
	
	
	/**
	 * Calls on the encapsulated entity grid to identify the entities and their occurances, and then
	 * constructs the graph with them.
	 * @param docAsString
	 * @return a  BipartiteGraph 
	 */
	public BipartiteGraph identifyEntitiesAndConstructGraph(String docAsString){
			
		Map<String, ArrayList<Map <Integer, String>>> entities = entityGrid.identifyEntitiesFromSentences(docAsString);
		
		return constructGraph(entities);
	}
	
	
	
	/**
	 * Constructs a graph from the list of noun occurances over all sentences.
	 * The graph can be projected in various ways:
	 * @param mode
	 * @param entities
	 * @return
	 */
	private BipartiteGraph constructGraph(Map<String, ArrayList<Map <Integer, String>>> entities){
		
		BipartiteGraph graph = new BipartiteGraph(entities);		
		
		return graph;
	}
	/**
	 * The various options are set on the commandline, to ensure correct parser is set.
	 * In the following format and order:
	 * inputfile, outputfile, containsMultipleDocs , language, type of projection
	 * "C:\\SMT\\datasets\\corpus-PE\\corpus\\PEofMT_Half.fr" 
	 * "C:\\SMT\\datasets\\corpus -PE\\corpus\\output_graph\\PEofMT_half.fr.graph.weighted" 
	 * "true" "French" "1"
	 * 
	 * @param input file
	 * @param output file, to log coherence scores per document
	 * @param language is one of English  French or German
	 * @param projection is one of:
	 * 		<li> UNWEIGHTED_PROJECTION = 0; //Weights are binary, and equal 1 for when 2 sentences have at least one entity in common
	 * 		<li>WEIGHTED_PROJECTION = 1; //Edges are weighted according to the number of entities shared by 2 sentences
	 * 		<li>SYNTACTIC_PROJECTION = 2; // edges are weighted according to syntax, with subject being awarded more weight than object, 
	 * 									which in turn is higher than any other grammatical position
	 * 
	 */
	public static void main(String[] args) {
		
		String filename = args[0];
		String outputfile = args[1];
		String rawtext = args[2];
		String language = args[3];
		int projection = new Integer(args[4]); 
		String tagger = args[5];
		
			
		Map<String, String> docs = new CorpusReader().readXML(filename);
		
		StringBuffer stringbuffer = new StringBuffer();
		
		if(Boolean.valueOf(rawtext) == Boolean.TRUE){
			
			EntityGraph graph = new EntityGraph(language, new EntityGridFactory().getEntityGridFramework(language));			
			
			for(int fileidx = 0; fileidx< docs.size(); fileidx++){
			
				BipartiteGraph bipartitegraph = graph.identifyEntitiesAndConstructGraph(docs.get(fileidx));
				bipartitegraph.setDocId(outputfile+fileidx+"_debug_");
				
				streamCoherenceScore(projection, fileidx, stringbuffer, 
						bipartitegraph.getLocalCoherence( projection), bipartitegraph);
			}
		}
		System.out.println(stringbuffer.toString());
		FileOutputUtils.streamToFile(outputfile, stringbuffer);
	}

	private static void streamCoherenceScore(int projection, int fileidx,
			StringBuffer stringbuffer, double coherence,
			BipartiteGraph bipartitegraph) {
		
		
		stringbuffer.append(fileidx);
		stringbuffer.append("\t");
		stringbuffer.append(coherence+", ");
		stringbuffer.append("\n");
	}
}
