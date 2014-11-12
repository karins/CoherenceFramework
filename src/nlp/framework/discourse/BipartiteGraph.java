package nlp.framework.discourse;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;
import java.util.Comparator;



/**
 * Tracks all the sentence nodes via a LinkedHashSet, and provides utility methods for projecting it.
 * See below for Projection derivation.
 * 
 * @author Karin Sim
 *
 */
public class BipartiteGraph {

	public static final int UNWEIGHTED_PROJECTION = 0;//Weights are binary, and equal 1 for when 2 sentences have at least one entity in common
	public static final int WEIGHTED_PROJECTION = 1;//Edges are weighted according to the number of entities shared by 2 sentences 
	public static final int SYNTACTIC_PROJECTION = 2;// Weights are computed according to the syntactic roles of entity in each sentence
	
	public static final int SUBJECT = 3;
	public static final int OBJECT = 2;
	public static final int OTHER_GRAMMATICAL = 1;
	
	//private LinkedHashSet<SentenceNode> sentenceNodes;
	private TreeSet<SentenceNode> sentenceNodes;
	private Set <String> entities;
	private String fileidx;
	

	public BipartiteGraph(Map<String, ArrayList<Map <Integer, String>>> entityMappings) {
		sentenceNodes = new TreeSet<SentenceNode>(new SentenceComparator());
		entities = new HashSet<>();
		createGraph(entityMappings);		
	}


	private void createGraph(Map<String, ArrayList<Map<Integer, String>>> entities) {
	
		//format : "entity"->list of : sentence_number->grammatical_role
		//Map<String, ArrayList<Map<Integer, String>>> entities) {
		for(String entity : entities.keySet()){
			
			//format : "entity"->list of : sentence_number->grammatical_role
			List <Map <Integer, String>> occurances = entities.get(entity);
			//String lexicalInfo = "\n entity: "+entity+" at "+occurances;
			//FileOutputUtils.writeDebugToFile(debugFile, lexicalInfo);
			//buffer.append( lexicalInfo);
			
			//add to entities
			this.entities.add(entity);
			
			for(Map <Integer, String> occurance : occurances){
				Integer sentence = occurance.keySet().iterator().next();
				
				//add to sentence node: finds existing sentence node and adds this entity, 
				//creates new sentence node if none exists
				addToSentenceNode(sentence, entity,  occurance.get(sentence).charAt(0));
			}
			
		}
		
	}
	
	/**
	 * Add to sentence node: finds existing sentence node and adds this entity,
	 * creates new sentence node if none exists
	 * @param sentence
	 * @param entity
	 * @param charAt
	 */
	private void addToSentenceNode(Integer sentence, String entity, char weight) {
		
		SentenceNode sentenceNode = containsSentenceNode(sentence);
		if(sentenceNode == null){
			sentenceNode = new SentenceNode(sentence.intValue());
			sentenceNodes.add(sentenceNode);
		}
		sentenceNode.addEntity(entity, getSyntacticWeight(weight));
		//sentenceNode.addEdge(entity, getSyntacticWeight(weight));
		
	}

	private int getSyntacticWeight(char weight) {
		switch(weight){
			case 'S': return SUBJECT;
			case 'O': return OBJECT;
			case 'X': return OTHER_GRAMMATICAL;
		}
		return 1;
	}

	public SentenceNode containsSentenceNode(Integer sentence) {
		for(SentenceNode sentenceNode : sentenceNodes){
			if(sentenceNode.getId() == sentence.intValue()){
				return sentenceNode;
			}
		}
		return null;
	}
	
	

	public TreeSet<SentenceNode> getSentenceNodes(){
		return sentenceNodes;
	}
	
	/**
	 * for now an entity is represented as a String. 
	 * To be an Entity object in future, in order to encapsulate additional lexical   information
	 * @return
	 */
	public Set<String> getEntities(){
		return entities;
	}
	
	/**
	 * Checks whether an Entity of given type is contained in the set
	 *  @return
	 */
	public boolean containsEntityNode(String entity){
		return entities.contains(entity);
	}
	
	/** branching factor
	 *
	 * As per calculated as :
	 * LocalCoherence(T) = AvgOutDegree(P)
	 * =1\N i=1..N OutDegree(si) 
	 * @param projection
	 * @return
	 */
	private double getAverageOutDegree(Projection projection){
		double sumOfEdgeWeights = projection.getSumOfEdgeWeights();
		System.out.println( "sumOfEdgeWeights= "+sumOfEdgeWeights+" AverageOutDegree= "+1.0/sentenceNodes.size() * sumOfEdgeWeights);
		//return 1.0/new Double(sentenceNodes.size()).doubleValue() * sumOfEdgeWeights;
		return (1.0/new Double(sentenceNodes.size()).doubleValue()) * sumOfEdgeWeights;
	}
	
	
	/**
	 * Determines the Projection type for representing this graph. One of:
	 * <br/>UNWEIGHTED_PROJECTION: Weights are binary, and equal 1 for when 2 sentences have at least one entity in common
	 * <br/> WEIGHTED_PROJECTION : Edges are weighted according to the number of entities shared by 2 sentences
	 * <br/> SYNTACTIC_PROJECTION : Weights are computed according to the syntactic roles of entity in each sentence
	 * @param projectionType
	 * @return
	 */
	public Projection getProjection(int projectionType){
		System.out.println("Projection : "+projectionType);
		switch(projectionType){
		case UNWEIGHTED_PROJECTION: 
			return new GraphProjection(this);
		case WEIGHTED_PROJECTION: 
			return new WeightedGraphProjection(this);
		case SYNTACTIC_PROJECTION: 
			return new SyntacticGraphProjection(this);

		default: return new GraphProjection(this);
		}
		 
	}
	
	public double getLocalCoherence(String text, int type){
		
		return getAverageOutDegree(getProjection(type));		
	}
	
	class SentenceComparator implements Comparator<SentenceNode>{
		public int compare(SentenceNode one, SentenceNode two){
			if(one.getId() > two.getId()){
				return 1;
			}else if(one.getId() == two.getId()){
				return 0;
			}
			else{
				return -1;
			}
			
		}
	}

	public void setDocId(String debugFile) {
		this.fileidx = debugFile;
	}
	public String getDocId() {
		return this.fileidx;
	}
}
