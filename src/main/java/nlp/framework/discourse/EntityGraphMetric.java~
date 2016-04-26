package nlp.framework.discourse;

import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import edu.stanford.nlp.util.CoreMap;

/**
 * Class to implement the required methods for a feature model in Docent. These are as defined below. 
 * This particular wrapper encapsulates a single document instance- unlike EntityExperiments, which can be 
 * run batch-style. It also allows for isolated updates.
 * 
 * Documentation extracted from Docent, : 
 * 
 * A feature model class in Docent implements three methods. The initDocument method is called
 * once per document when decoding starts. It straightforwardly computes the model score for
 * the entire document from scratch. When a state is modified, the decoder first invokes the 
 * estimateScoreUpdate method. Rather than calculating the new score exactly, this method is only required
 * to return an upper bound that reflects the maximum score that could possibly be achieved by this
 * state. The search algorithm then checks this upper bound against the acceptance criterion. Only if the
 * upper bound meets the criterion does it call the updateScore method to calculate the exact score,
 * which is then checked against the acceptance criterion again.
 * 
 * @author karin 
 */
public class EntityGraphMetric {

	public static void main(String[] args) {
		String document = args[0];
		int projection = new Integer(args[1]);
		// generate one off score, output to screen with no return values 
		EntityGraphMetric graph = new EntityGraphMetric();
		System.out.println("Score for document under graph model: "+ graph.initDocument(document, projection));

	}

	/**
	 * called once per document when decoding starts. It straightforwardly computes the model score for
	 * 	the entire document from scratch **/
	public double initDocument(String document, int projection){
		double score = this.getGraph("",document, projection);
		System.out.println("Returning score: "+score);
		return score;
	}
	
	
	/** 
	 * Only if the upper bound meets the criterion does it call the updateScore method to calculate the exact score,
	 * which is then checked against the acceptance criterion again.
	 * */
	public double updateScore(){
		return 0.0;
	}
	/**
	 * When a state is modified, the decoder first invokes the 
	 * 	estimateScoreUpdate method. Rather than calculating the new score exactly, this method is only required
	 * to return an upper bound that reflects the maximum score that could possibly be achieved by this
	 * state. The search algorithm then checks this upper bound against the acceptance criterion.
	 * */
	public double estimateScoreUpdate(){
		return 0.0;
	}
	
//private void getGridAndGraph(String path, String filename, String language, int projection, boolean isXML){
	private double getGraph(String language, String document, int projection){
		
		//Map<String, List<String>> docs;
		Map<String, String> docs;
		/*if(isXML){
			Map<String, List<String>> docList = new CorpusReader().readXMLwithDocIds(path+File.separator+filename);
			docs = fitMap(new HashMap<String, String>(), docList);
		}else{*/
		//docs = new CorpusReader().readDataAsDocs(path+File.separator+filename);
		//}
		
		//StringBuffer stringbuffer = new StringBuffer();
		
		EntityGridFramework framework = new EntityGridFactory().getEntityGridFramework(language, "");		

		//char grid [][] = framework.identifyEntitiesAndConstructGrid(teststring1);
		
		List<CoreMap> sentences = framework.getAnnotatedDocument(document);
		Map<String, ArrayList<Map <Integer, String>>> entities = framework.identifyEntities(sentences);
		
		BipartiteGraph bipartitegraph = new BipartiteGraph(entities);			
		//BipartiteGraph bipartiteGraph  = graph.identifyEntitiesAndConstructGraph(teststring1);	 
			
		return bipartitegraph.getLocalCoherence( projection);
	}
}

