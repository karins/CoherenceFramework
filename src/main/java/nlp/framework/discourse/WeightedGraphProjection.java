package nlp.framework.discourse;

import java.util.Map;

import com.google.common.collect.Sets.SetView;

public class WeightedGraphProjection extends GraphProjection {

	public WeightedGraphProjection(BipartiteGraph graph) {
		super(graph);
	}
	
	/**
	 * sum all the projections leaving each sentence node
	 * For weighted projection: count the number of 
	 */
	/*public double getSumOfEdgeWeights(){
		double sumOfEdgeWeights = 0;
		
		//for all sentences in projection
		SentenceNode previousSentence = null;
		//sum occurances, divide by weight
		for (SentenceNode sentence : graph.getSentenceNodes()){
			Map<String,Integer> edges = sentence.getAllEdges();
			
			//For weighted projection: calculate shared entities between adjacent nodes
			for(String edge: edges.keySet()){
				sumOfEdgeWeights  += edges.get(edge).doubleValue();
				System.out.println ("for sentence "+sentence.getId()+" edge:"+edge+" edge weight= "+edges.get(edge).doubleValue());
			}
			previousSentence = sentence;  
		}
		
		return sumOfEdgeWeights;
	}*/
	
	/**
	 * sum all the projections leaving each sentence node
	 * For weighted projection: count the number of shared entities.
	 */
	protected double calculateEdgeWeight(double sumOfEdgeWeights, SetView<String> intersectingSets, Map<String, Integer> S1, Map<String, Integer> S2, double distance) {
		if(intersectingSets!= null){
			
			//sumOfEdgeWeights+= (double)intersectingSets.size();
			double sum = (double)intersectingSets.size();
			sumOfEdgeWeights+= (sum/distance);
			buffer.append("\n $ WEIGHTED.. incrementing edge weights by "+(double)intersectingSets.size()+" for ");
			for(String entity : intersectingSets){
				buffer.append(entity+" ");
			}
		}
		return sumOfEdgeWeights;
	}

}
