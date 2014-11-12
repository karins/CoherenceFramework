package nlp.framework.discourse;

import java.util.Iterator;
import java.util.Map;
import java.util.Set;

import com.google.common.collect.Sets;
import com.google.common.collect.Sets.SetView;

//import edu.stanford.nlp.util.Sets;

/**
 * Simple, unweighted graph projection
 * @author Karin Sim
 */
public class GraphProjection implements Projection {

	protected BipartiteGraph graph; 
	protected static final boolean DEBUG = true;
	protected String debugFile;
	protected StringBuffer buffer ;
	
	public GraphProjection(BipartiteGraph graph) {
		this.graph = graph;
		debugFile = graph.getDocId();
	}

	/**
	 * create edges: and edge is created between 2 sentence nodes if they share any entities
	 */
	//private void createEdges() {
	public double getSumOfEdgeWeights(){
		buffer = new StringBuffer();
		//if(DEBUG)debugFile = PATH+"_debug";
		buffer.append("\n Starts : "+graph.getSentenceNodes().iterator().next().getSentence());
		
		double sumOfEdgeWeights = 0;
		
		//iterate through all sentence nodes determining edges
		//for(SentenceNode sentenceNode : graph.getSentenceNodes()){
		Iterator sentences = graph.getSentenceNodes().iterator();
		while(sentences.hasNext()){
			SentenceNode sentenceNode = (SentenceNode) sentences.next();
			System.out.println("$ sentence : "+sentenceNode.getId());
			
			//to ensure that the projection is only forwards, ie in text order..
			//for(SentenceNode nextSentence : graph.getSentenceNodes()){
			Iterator comparison = graph.getSentenceNodes().iterator();
			while(comparison.hasNext()){
				SentenceNode nextSentence = (SentenceNode) comparison.next();
				
				buffer.append("$$ sentence : "+sentenceNode.getId() +" comparing with "+nextSentence.getId());
				
				//create edges: and edge is created between 2 sentence nodes if they share any entities
				//if(sentenceNode != nextSentence && Sets.intersection(sentenceNode.getEntityNodes(), nextSentence.getEntityNodes()) != null){
				if(sentenceNode.getId() < nextSentence.getId()){
				//if(sentenceNode != nextSentence){
					SetView<String> intersectingSets = Sets.intersection(sentenceNode.getEntityNodes(), nextSentence.getEntityNodes());
					System.out.println("$$$ shared sets "+intersectingSets.size());
					if(intersectingSets.size() > 0){
						buffer.append("\n S"+sentenceNode.getId()+" n "+" S"+nextSentence.getId()+" = "+intersectingSets.size());
						sumOfEdgeWeights = calculateEdgeWeight(sumOfEdgeWeights, intersectingSets, sentenceNode.getAllEdges(), nextSentence.getAllEdges());
					}
				}
				
			}buffer.append("\n sumOfEdgeWeights for S"+sentenceNode.getId()+" = "+sumOfEdgeWeights);
			if(DEBUG)FileOutputUtils.writeDebugToFile(debugFile, buffer.toString());
		}return sumOfEdgeWeights;
	}
	
	
	protected double calculateEdgeWeight(double sumOfEdgeWeights, SetView<String> intersectingSets, Map<String, Integer> S1, Map<String, Integer> S2) {
		if(intersectingSets!= null){
			buffer.append("\n  $$$$ UNWEIGHTED: .. incrementing edge weights..");
			sumOfEdgeWeights++;
			//sumOfEdgeWeights+= (double)intersectingSets.size();
		}
		return sumOfEdgeWeights;
	}
	
	
	/**
	 * sum all the projections leaving each sentence node
	 */
	/*public double getSumOfEdgeWeights(){
		double sumOfEdgeWeights = 0;
		
		//for all sentences in projection
		
		//sum occurances, divide by weight
		for (SentenceNode sentence : graph.getSentenceNodes()){
			Map<String,Integer> edges = sentence.getAllEdges();
			sumOfEdgeWeights  += (double)edges.size();
			//TODO: FOR WEIGHTED PROJECTION: convert grammatical role to weight
			
		}
		
		return sumOfEdgeWeights;
	}*/
}
