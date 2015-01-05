package nlp.framework.discourse;

import java.io.File;
import java.nio.CharBuffer;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * Creates Entity Grid and optionally also Entity Graph. 
 * Outputs grids and scores to file.
 * 
 * @author Karin Sim
 *
 */
public class EntityExperiments {

	/**
	 * Creates Entity Grid and Entity Graph. 
	 * Outputs grids and scores to file.
	 * @param args: 
	 * <li>directory(of input file)</li>
	 * <li>language (English/French/German) </li> 
	 * <li>isXML (true or false; either <doc> separated or # id=fileid</li>
	 * <li>gridAndGraph (true if both, false if just grid)</li>
	 * <li>projection (NB optional- only required if above is true)</li>
	 */
	public static void main(String[] args) {
			
		
		String directory = args[0];
		String language = args[1];
		boolean isXML = new Boolean(args[2]);
		boolean gridAndGraph = new Boolean(args[3]);
		
		
		EntityExperiments experiments = new EntityExperiments();
		System.out.println("dir = "+directory);
		File[] files = new File(directory).listFiles();
		for (File file : files) {
			if (file.isFile()){
				System.out.println("file = "+directory+"\\"+file.getName());
				
				if(gridAndGraph){
					int projection = new Integer(args[4]);
					experiments.getGridAndGraph(directory, file.getName(), language, projection, isXML);
				}else{
					experiments.getGrid(directory, file.getName(), language, isXML);					
				}
			}
		}
	}
	
	private void getGrid(String path, String filename, String language,  boolean isXML){
		Map<String,String> docs;
		if(isXML){
			docs = new CorpusReader().readXMLwithDocIds(path+"\\"+filename);
		}else{
			docs = new CorpusReader().readDataAsDocs(path+"\\"+filename);
		}
		EntityGridFramework framework = new EntityGridFactory().getEntityGridFramework(language, "");
		for(String docid : docs.keySet()){
			
			Map<String, ArrayList<Map <Integer, String>>> entities = framework.identifyEntitiesFromSentences(docs.get(docid));
			FileOutputUtils.writeGridToFile(getPath(filename, path), framework.constructGrid(entities), true, docid);
		}
	}
	
	/*public static void main(String[] args) {			
		
		String directory = args[0];
		String language = args[1];
		int projection = new Integer(args[2]); 
		boolean isXML = new Boolean(args[3]);
		
		EntityExperiments experiments = new EntityExperiments();
		System.out.println("dir = "+directory);
		File[] files = new File(directory).listFiles();
		for (File file : files) {
			if (file.isFile()){
				System.out.println("file = "+directory+"\\"+file.getName());
				
				experiments.getGridAndGraph(directory, file.getName(), language, projection, isXML);				
			}
		}
	}*/

	private void getGridAndGraph(String path, String filename, String language, int projection, boolean isXML){
		
		//List<List<String>> docs = new CorpusReader().readSGML(path+"\\"+filename);
		//List<String> docs;
		Map<String,String> docs;
		if(isXML){
			docs = new CorpusReader().readXMLwithDocIds(path+"\\"+filename);
		}else{
			docs = new CorpusReader().readDataAsDocs(path+"\\"+filename);
		}
		
		StringBuffer stringbuffer = new StringBuffer();
		
		EntityGridFramework framework = new EntityGridFactory().getEntityGridFramework(language, "");		
		
		StringBuffer graphdirectory = new StringBuffer(path);
		graphdirectory.append("\\output\\");
		graphdirectory.append("graph\\"); 
		graphdirectory.append(filename+"_graph_scores");
		
		for(int fileidx = 0; fileidx< docs.size(); fileidx++){
		
			//Map<String, ArrayList<Map <Integer, String>>> entities = framework.identifyEntitiesForGraph(docs.get(fileidx));		
			Map<String, ArrayList<Map <Integer, String>>> entities = framework.identifyEntitiesFromSentences(docs.get(fileidx));
			
			BipartiteGraph bipartitegraph = new BipartiteGraph(entities);			
			////bipartitegraph.setDocId(filename+fileidx+"_debug_");		
			//docs.get(fileidx),
			streamCoherenceScore(projection, fileidx, stringbuffer, 
					bipartitegraph.getLocalCoherence( projection), bipartitegraph);
			System.out.println("entities"+entities.size());
			FileOutputUtils.writeGridToFile(getPath(filename, path, fileidx), framework.constructGrid(entities));
		}
		
		FileOutputUtils.streamToFile(graphdirectory.toString(), stringbuffer);
	}

	private String getPath(String filename, String outputdirectory, int fileidx) {
		StringBuffer path = new StringBuffer();
		path.append(outputdirectory.toString());
		path.append("\\output\\");
		path.append("grid\\");
		path.append(filename+"_grid_"+fileidx);
		return path.toString();
	}
	
	private String getPath(String filename, String outputdirectory) {
		StringBuffer path = new StringBuffer();
		path.append(outputdirectory.toString());
		path.append("\\output\\");
		path.append("grid\\");
		path.append(filename+"_grids");
		return path.toString();
	}

	private static void streamCoherenceScore(int projection, int fileidx,
			StringBuffer stringbuffer, double coherence,
			BipartiteGraph bipartitegraph) {
		
		stringbuffer.append(fileidx);
		stringbuffer.append("\t");
		stringbuffer.append(coherence);
		stringbuffer.append("\n");
	}
}
