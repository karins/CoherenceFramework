package nlp.framework.discourse;

import java.util.ArrayList;
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

	//public final static int BIPARTITE_MODE = 1;
	//public final static int UNWEIGHTED_ONE_MODE = 2;
	//public final static int WEIGHTED_ONE_MODE = 3;
	//public final static int INCIDENCE_MATRIX = 4;
	//public final static int UNWEIGHTED_ADJACENCY_MATRIX = 5;
	//public final static int WEIGHTED_ADJACENCY_MATRIX = 6;
	
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
		//Annotation document = new Annotation(docAsString);
		//super.pipeline.annotate(document);
		//List<CoreMap> sentences = document.get(SentencesAnnotation.class);
		//EntityGridFramework gridframework = new EntityGridFactory().getEntityGridFramework(language, EntityGridFramework.ge);
		
		Map<String, ArrayList<Map <Integer, String>>> entities = entityGrid.identifyEntitiesForGraph(docAsString);
		
		return constructGraph(entities);
	}

	/**
	 * Constructs a graph from the list of noun occurances over all sentences.
	 * 
	 */
	/*private BipartiteGraph constructGraph(char[][] grid) {
		
		BipartiteGraph graph ;
		graph = new BipartiteGraph(char[][] grid);
		for(int i = 0; i< grid.length; i++) {//each sentence
			for(int j = 0; j< grid[i].length; j++) {//each char representing entity
				
				graph = new BipartiteGraph(char[][] grid);
				
				if(grid[i][j] 1= 0){
										
					graph.addEdge(grid[i][j]);
				}
			}output.write('\n');
		 }
		return graph;
	}*/

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
	 * "C:\\SMT\\datasets\\corpus-PE\\corpus\\PEofMT_Half.fr" "C:\\SMT\\datasets\\corpus -PE\\corpus\\output_graph\\PEofMT_half.fr.graph.weighted" "true" "French" "2"
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
		String multiple = args[2];
		String language = args[3];
		int projection = new Integer(args[4]); 
		String tagger = args[5];
		//boolean isXML = new Boolean(args[4]);
		 
		//StringBuffer output = new StringBuffer();
		
		if(Boolean.valueOf(multiple) == Boolean.TRUE){
			
			List<String> docs = new CorpusReader().readXML(filename, true);
			int fileidx = 0;
			StringBuffer stringbuffer = new StringBuffer();
			//if(DEBUG)debugFile = outputfile+fileidx+"_debug";
			EntityGraph graph = new EntityGraph(language, new EntityGridFactory().getEntityGridFramework(language, tagger));
			 
			
			for(String docAsString: docs){
				
				
				BipartiteGraph bipartitegraph = graph.identifyEntitiesAndConstructGraph(docAsString);
				bipartitegraph.setDocId(outputfile+fileidx+"_debug_");
				//double coherence = bipartitegraph.getLocalCoherence(docAsString, BipartiteGraph.UNWEIGHTED_PROJECTION);
				double coherence = bipartitegraph.getLocalCoherence(docAsString, projection);
				//FileOutputUtils.writeGraphCoherenceToFile(outputfile+fileidx,  bipartitegraph);
				//FileOutputUtils.writeGraphCoherenceToFile(outputfile, fileidx, bipartitegraph);
				//if(DEBUG)FileOutputUtils.writeDebugToFile(debugFile, output.toString());
				stringbuffer.append(fileidx);
				stringbuffer.append("\t");
				stringbuffer.append(coherence+", ");
				stringbuffer.append("\n");
				fileidx++;
			}
			System.out.println(stringbuffer.toString());
			FileOutputUtils.streamToFile(outputfile, stringbuffer);
			
			//FileOutputUtils.writeGraphCoherenceToFile(outputfile, fileidx, bipartitegraph);
		}else{
			//System.out.print("ONLY MULTIPLE FILE IMPLEMENTATION FOR GRAPH");
			List<String> docs = new CorpusReader().readXML(filename, true);
			EntityGraph graph = new EntityGraph(language,  new EntityGridFactory().getEntityGridFramework(language, tagger));
			BipartiteGraph bipartitegraph = graph.identifyEntitiesAndConstructGraph(docs.get(0));
			//FileOutputUtils.writeGraphCoherenceToFile(outputfile, 0, bipartitegraph.getLocalCoherence(docs.get(0), BipartiteGraph.UNWEIGHTED_PROJECTION));
		}
	}
}
