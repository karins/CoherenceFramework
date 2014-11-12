package nlp.framework.discourse;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * Represents a sentence in a given document.
 * Tracks all the entities it contains.
 * @author Karin
 *
 */
public class SentenceNode {
	
	private int sentenceId;
	private Set <String> entityNodes;
	private Map < String, Integer> entityOccurances;
	//private Map < String, Integer> entityProjectionEdges;
	
	public SentenceNode(int sentenceId) {
		System.out.println("CREATING sentence "+sentenceId);
		this.sentenceId = sentenceId;
		entityNodes= new HashSet<String>();
		//entityProjectionEdges = new HashMap< String, Integer>();
		entityOccurances = new HashMap< String, Integer>();
	}
	
	
	public int getId(){
		return this.sentenceId;
	}
	
	/**
	 * Stores an entity linked to this sentence.
	 * Also stores the weight associated with it.
	 * @param entity
	 * @param role
	 */
	/*public void addEdge(String entity, int role ){
		entityNodes.add(entity);
		entityOccurances.put(entity, new Integer(role));
	}*/
	
	/**
	 * Stores an entity linked to this sentence.
	 * Also stores the weight associated with it.
	 * @param entity
	 * @param role
	 */
	/*public void addProjectionEdge(String entity, int role ){
		
		entityProjectionEdges.put(entity, new Integer(role));
	}*/
	
	/**
	 * Retrieves all edges between a sentence node and an entity node. 
	 * So for any non null cells in the entity grid where the is a 
	 * @return
	 */
	public  Map < String, Integer> getAllEdges(){
		return entityOccurances;
	}
	
	/**
	 * Retrieves all entity nodes in a sentence node. 
	 *  
	 * @return
	 */
	public Set<String> getEntityNodes(){
		return entityNodes;
	}
	
	public boolean hasEntityNode(String entity){
		return entityNodes.contains(entity);
	}
	
	public void addEntity(String entity, int role){
		if (! hasEntityNode(entity)){
			entityNodes.add(entity);
			entityOccurances.put(entity, new Integer(role));
		}
		//TODO: IF TRACK MULTIPLE OCCURANCES, THEN STORE THEM HERE
		//.put(entity, new Integer(role));
	}

	public boolean hasEdge(String entity, Integer weight) {
		
		return entityOccurances.containsKey(entity) && 
				 entityOccurances.get(entity).equals(weight);
	}
	
	public String getSentence(){
		StringBuffer buffer = new StringBuffer();
		for(String entity: entityNodes){
			buffer.append(entity);
			buffer.append(" ");
		}
		return buffer.toString();
	}
}
