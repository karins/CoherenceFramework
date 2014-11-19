package nlp.framework.discourse;

import java.util.List;
import java.util.Map;
import java.util.Properties;

import edu.stanford.nlp.ling.CoreAnnotations.SentencesAnnotation;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.TreeCoreAnnotations.TreeAnnotation;
import edu.stanford.nlp.util.CoreMap;


/** 
 * Converts text with document markup into parse trees, using Stanford CoreNLP.
 *  
 * @author Karin
 *
 */
public class ParseTreeConverter {

	//private static final String XML_START = "<?xml version="1.0" encoding="UTF-8"?><srcset  srclang=\"any\">";
	private static final String XML_START = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><docs>";
	//private static final String XML_END = "</srcset>";
	private static final String XML_END = "</docs>";
	private static final String DOC_TAG_START = "\n<doc>\n";
	private static final String DOC_TAG_END = "</doc>";
	protected StanfordCoreNLP pipeline;
	
	/**
	 * 
	 * @param args filename of file to be parsed. this contains documents with doc tag boundaries
	 * @param args filename of output file for parse trees to be written to. 
	 * This will write to one outputfile with parse trees for each document seperated by doc tags 
	 */
	public static void main(String [] args){
		//String filename = args[0];
		//String outputfile = args[1];
		
		ParseTreeConverter converter = new ParseTreeConverter(); 
		//converter.parse(filename, outputfile);
		converter.parse();
	}
	
	/**
	 * Parses documents into parse trees.
	 * Input and output from console
	 */
	public void parse(){
		
		this.pipeline = new StanfordCoreNLP(new Properties());
		//Map<String, List<String>> docsAndIds = new CorpusReader().readXMLfromConsole(true);
		Map<String, String> docAndIds = new CorpusReader().readXMLfromConsole();
		
		//List<String> docs =  docsAndIds.get("docs");
		//List<String> ids =  docsAndIds.get("ids");
		
		System.out.println(XML_START);
		//for (int i = 0; i<docs.size(); i++){
		//for(String docAsString: docs){
		for(String id : docAndIds.keySet()){
			
			printParseTree(docAndIds.get(id), id);
			
		}
		System.out.println(XML_END);
		
	}
	
	/**
	 * For each document:
	 * <li>		Read in source text and construct parse tree. 
	 * <li>		 
	 * @param id 
	 *  @return parse tree
	 * @param 
	 */
	public void printParseTree(String docAsString, String id){
		
		
		Annotation document = new Annotation(docAsString);
		this.pipeline.annotate(document);
		List<CoreMap> sentences = document.get(SentencesAnnotation.class);		
		
		
		printStartTag(id);
		for(CoreMap sentence: sentences) {
			
			// this is the parse tree of the current sentence
			Tree root = sentence.get(TreeAnnotation.class);
			
			System.out.println(root);
			
		}
		System.out.println(DOC_TAG_END);
	}

	
	private void printStartTag(String id) {
		// TODO Auto-generated method stub
		//System.out.println(DOC_TAG_START);
		System.out.println("\n<doc id=\""+id+"\">\n");
		
	}

	/**
	 * Parses documents into parse trees.
	 * @param filename of file to be parsed. this contains documents with doc tag boundaries
	 * @param  outputfile, filename of output file for parse trees to be written to. 
	 * This will write to one outputfile with parse trees for each document separated by doc tags 
	 */
	public void parse(String filename, String outputfile){
		
		this.pipeline = new StanfordCoreNLP(new Properties());
		
		List<String> docs = new CorpusReader().readXML(filename, true);
		
		StringBuffer trees = new StringBuffer();
		trees.append(XML_START);
		boolean first = true;
		for(String docAsString: docs){
			
			getParseTree(docAsString, trees);
			if(first)System.out.println("returning tree "+trees.toString());
			first = false;
		}
		trees.append(XML_END);
		FileOutputUtils.streamToFile(outputfile, trees);
	}
	
	/**
	 * For each document:
	 * <li>		Read in source text and construct parse tree. 
	 * <li>		 
	 *  @return parse tree
	 * @param 
	 */
	public StringBuffer getParseTree(String docAsString, StringBuffer trees){
		
		Annotation document = new Annotation(docAsString);
		this.pipeline.annotate(document);
		List<CoreMap> sentences = document.get(SentencesAnnotation.class);		
		
		trees.append(DOC_TAG_START);
		for(CoreMap sentence: sentences) {
			
			// this is the parse tree of the current sentence
			Tree root = sentence.get(TreeAnnotation.class);
			
			trees.append(root);
			trees.append('\n');
			
		}
		trees.append(DOC_TAG_END);
		
		return trees;
	}


}
