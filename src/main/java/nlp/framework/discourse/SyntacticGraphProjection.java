package nlp.framework.discourse;

import java.util.Map;

import com.google.common.collect.Sets.SetView;

public class SyntacticGraphProjection extends GraphProjection {

	public SyntacticGraphProjection(BipartiteGraph graph) {
		super(graph);
	}

	/**
	 * sum all the projections leaving each sentence node
	 * For syntactic projection: convert grammatical role to weight
	 */
	/*public double getSumOfEdgeWeights(){
		double sumOfEdgeWeights = 0;
		
		//for all sentences in projection
		
		//sum grammatical weights
		for (SentenceNode sentence : graph.getSentenceNodes()){
			Map<String,Integer> edges = sentence.getAllEdges();
			
			//For syntactic projection: convert grammatical role to weight
			for(String edge: edges.keySet()){
				sumOfEdgeWeights  += edges.get(edge).doubleValue();
				System.out.println ("for sentence "+sentence.getId()+" edge:"+edge+" edge weight= "+edges.get(edge).doubleValue());
			}
		}
		
		return sumOfEdgeWeights;
	}*/
	
	protected double calculateEdgeWeight(double sumOfEdgeWeights, SetView<String> intersectingSets, Map<String, Integer> S1, Map<String, Integer> S2, double distance) {
		if(intersectingSets!= null){
			for(String entity: intersectingSets){
				
				//sumOfEdgeWeights+= S1.get(entity).doubleValue() * S2.get(entity).doubleValue();
				double sum = S1.get(entity).doubleValue() * S2.get(entity).doubleValue();
				sumOfEdgeWeights+=  (sum/distance);
				
				buffer.append("\n $ SYNTACTIC.. incrementing edge weights by "+
				S1.get(entity).doubleValue()+" * "+S2.get(entity).doubleValue() +" = " +
						S1.get(entity).doubleValue() * S2.get(entity).doubleValue()+" for "+entity);
			}
		}
		return sumOfEdgeWeights;
	}
}
