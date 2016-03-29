package nlp.framework.discourse;

import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PushbackInputStream;
import java.io.Reader;
import java.io.StringBufferInputStream;
import java.io.StringReader;
import java.nio.charset.CharsetDecoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.zip.GZIPInputStream;

import javax.xml.parsers.ParserConfigurationException;
import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;

import org.xml.sax.Attributes;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;
import org.xml.sax.helpers.DefaultHandler;

import edu.stanford.nlp.dcoref.Document;
import edu.stanford.nlp.io.IOUtils;
import edu.stanford.nlp.trees.PennTreeReader;
import edu.stanford.nlp.trees.Tree;

/**
 * Basic IO functionality methods
 * 
 * @author Karin Sim
 *
 */
public class CorpusReader {
	

	/**
	 * Reads in contents of a file and returns as list of strings
	 * @param filename name of the file to read from
	 * @return
	 */
	public static List<String> readData(String filename){
		try{
			
			List<String> contents = new ArrayList<String>();
			
			BufferedReader input =  new BufferedReader(new InputStreamReader(new FileInputStream(new File(filename))));
			
			for(String line = input.readLine(); line != null; line = input.readLine()) {
				contents.add(line);
			}
			input.close();
			return contents; 
		} catch(IOException e) {
			e.printStackTrace();
			System.exit(1);
			return null;
		}
	}
	/**
	 * Reads in contents of a file and returns as List of strings
	 * @param filename name of the file to read from
	 * @return
	 */
	//public Map<String, String> readDataAsDocs(String filename){
	//GZIPInputStream
	
	public boolean isCompressed(byte[] bytes) throws IOException
	{
		if ((bytes == null) || (bytes.length < 2))
		{
			return false;
		}else{
			return ((bytes[0] == (byte) (GZIPInputStream.GZIP_MAGIC)) && (bytes[1] == (byte) (GZIPInputStream.GZIP_MAGIC >> 8)));
		}
	}
	
	/**
	 * Check if stream is gzipped, and decompress if so. Returns wrapped stream.
	 * @param input
	 * @return
	 */
	public InputStream decompressStream(InputStream input) {
		
		PushbackInputStream pb = new PushbackInputStream( input, 2 ); 
		byte [] signature = new byte[2];
		try {
			//check if this is indeed gzipped..
			pb.read( signature );
			pb.unread( signature ); 
		
			if( signature[ 0 ] == (byte) 0x1f && signature[ 1 ] == (byte) 0x8b ){ //check if matches standard gzip signature
				return new GZIPInputStream( pb );
			}
			else{
				return pb;
			}
		}catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return pb;
	}
	

	/**
	 * Reads in contents of a file and returns as List of Trees
	 * @param filename name of the file to read from
	 * @return
	 */
	public Map<String, List<Tree>> readPtbDataAsDocs(String filename){
		String START = new String("#");
		String docId = null;
		Map<String, List<Tree>> docs = new LinkedHashMap<String, List<Tree>>();
		BufferedReader input =  null;
		try{
			//StringBuilder contents = new StringBuilder();
			List<Tree> docTrees = new ArrayList<Tree>();
			
			CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder();
			//input =  new BufferedReader(new InputStreamReader(new FileInputStream(new File(filename)), decoder));
			InputStream inputStream =  new FileInputStream(new File(filename));
			input = new BufferedReader(new InputStreamReader(decompressStream(inputStream)));//, decoder));
			//PennTreeReader treeReader = new PennTreeReader(new InputStreamReader(new FileInputStream(new File(filename))));//, factory);
//			PennTreeReader treeReader = new PennTreeReader(new InputStreamReader(new FileInputStream(file)));
			
			for(String line = input.readLine(); line != null; line = input.readLine()) {
				System.out.println(line);
				if(line.startsWith(START)){	
					docId = line;
					
				}else if(line.isEmpty()){//end of doc					
					docs.put(docId, docTrees);
					docTrees = new ArrayList<Tree>();
				}else{
					PennTreeReader treeReader = new PennTreeReader(new StringReader(line));
					Tree tree = treeReader.readTree();
					docTrees.add(tree);	
				}
			}docs.put(docId, docTrees);
			
			return docs;
		} catch(IOException e) {
			e.printStackTrace();
			System.exit(1);
			return null;
		}
		finally{
			try {  input.close();  }  catch (Exception e) { /* log it ?*/ }
		}
	}

	/**
	 * Reads in contents of a file and returns as List of Trees
	 * @param filename name of the file to read from
	 * @return
	 */
	public List<Tree> outputDocAsPtbs(String filename){
		//String START = new String("#");
		//String docId = null;
		//Map<String, List<Tree>> docs = new LinkedHashMap<String, List<Tree>>();
		//List<Tree> docs = new ArrayList<Tree>();
		List<Tree> docTrees = new ArrayList<Tree>();
		BufferedReader input =  null;
		try{
			
			//List<Tree> docTrees = new ArrayList<Tree>();
			
			CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder();
			
			InputStream inputStream =  new FileInputStream(new File(filename));
			input = new BufferedReader(new InputStreamReader(decompressStream(inputStream)));//, decoder));
			//PennTreeReader treeReader = new PennTreeReader(new InputStreamReader(new FileInputStream(new File(filename))));//, factory);
//			PennTreeReader treeReader = new PennTreeReader(new InputStreamReader(new FileInputStream(file)));
			
			for(String line = input.readLine(); line != null; line = input.readLine()) {
				if(!line.isEmpty()){//end of doc					
					
					if(line.startsWith("<doc")){
						
					}else if(line.endsWith("</doc>")){
						
					}
					PennTreeReader treeReader = new PennTreeReader(new StringReader(line));
					Tree tree = treeReader.readTree();
					docTrees.add(tree);	
				}
			}//docs.put(docId, docTrees);
			
			return docTrees;
		} catch(IOException e) {
			e.printStackTrace();
			System.exit(1);
			return null;
		}
		finally{
			try {  input.close();  }  catch (Exception e) { /* log it ?*/ }
		}
	}
	
	/**
	 * Reads in contents of a file and returns as List of strings
	 * @param filename name of the file to read from
	 * @return
	 */
	public Map<String, String> readDataAsDocs(String filename){
		//List <String> docs = new ArrayList<String>();
		String START = new String("#");
		String docId = null;
		Map<String, String> docs = new LinkedHashMap<String, String>();
		BufferedReader input =  null;
		try{
			StringBuilder contents = new StringBuilder();
			
			CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder();
			//input =  new BufferedReader(new InputStreamReader(new FileInputStream(new File(filename)), decoder));
			InputStream inputStream =  new FileInputStream(new File(filename));
			input = new BufferedReader(new InputStreamReader(decompressStream(inputStream), decoder));
			
			for(String line = input.readLine(); line != null; line = input.readLine()) {
				
				if(line.startsWith(START)){
					
					docId = line;
					
				}else if(line.isEmpty()){//end of doc
					
					docs.put(docId,contents.toString());
					contents = new StringBuilder();	
					
				}else{
					contents.append(line);
					contents.append("\n");
				}
			}
			if(contents.length() >0){
				docs.put(docId,contents.toString());
				contents = new StringBuilder();
			}
			return docs;
		} catch(IOException e) {
			e.printStackTrace();
			System.exit(1);
			return null;
		}
		finally{
			try {  input.close();  }  catch (Exception e) { System.out.print(e.toString()); }
		}
	}
	
	/**
	 * Reads in contents of a file and returns as List of strings
	 * @param filename name of the file to read from
	 * @return
	 */
	public Map<String, List<String>> readDataAsDocsToList(String filename){
		
		String START = new String("#");
		String docId = null;
		Map<String, List<String>> docs = new LinkedHashMap<String, List<String>>();
		BufferedReader input =  null;
		try{
			
			List <String> contents = new ArrayList<String>();
			CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder();
			//input =  new BufferedReader(new InputStreamReader(new FileInputStream(new File(filename)), decoder));
			InputStream inputStream =  new FileInputStream(new File(filename));
			input = new BufferedReader(new InputStreamReader(decompressStream(inputStream), decoder));
			
			for(String line = input.readLine(); line != null; line = input.readLine()) {
				
				if(line.startsWith(START)){					
					docId = line;					
				}else if(line.isEmpty()){//end of doc
					
					docs.put(docId,contents);
					contents = new ArrayList<String>();	
					
				}else{
					contents.add(line);
					//contents.append("\n");
				}
			}
			
			return docs;
		} catch(IOException e) {
			e.printStackTrace();
			System.exit(1);
			return null;
		}
		finally{
			try {  input.close();  }  catch (Exception e) { /* log it ?*/ }
		}
	}

	
	/**
	 * Reads in contents of a file and returns as string
	 * @param filename name of the file to read from
	 * @return
	 */
	public static String readDataAsString(String filename){
		BufferedReader input =  null;
		try{
			StringBuilder contents = new StringBuilder();
			
			CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder();
			input =  new BufferedReader(new InputStreamReader(new FileInputStream(new File(filename)), decoder));
			
			for(String line = input.readLine(); line != null; line = input.readLine()) {
			 
				contents.append(line);
				contents.append("\n");
			}
			return contents.toString(); 
		} catch(IOException e) {
			e.printStackTrace();
			System.exit(1);
			return null;
		}
		finally{
			try {  input.close();  }  catch (Exception e) { /* log it ?*/ }
		}
	}
	

	
	
	public static List<String> segmentWords(String s) {
		List<String> ret = new ArrayList<String>();
		boolean fullstop = false;
		for(String word:  s.split("\\s")) {
			if(word.length() > 0) {
				if(word.endsWith(".")){
					word = word.substring(0, word.length()-1);
					fullstop = true;
				}
				ret.add(word);
				if(fullstop){
					ret.add(".");
				}
			}
		}
		return ret;
	}
	
	public static String[] segmentWordsAsArray(String input) {

		String[] splitArray = input.split("\\s+");

		return splitArray;
	}

	public static char[][] readGridFromFile(String gridFile) {
		
		List <String> data =  readData(gridFile);
		
		char grid [][] = new char[data.size()][data.get(0).length()];
		for(int i = 0; i< grid.length; i++) {//each sentence
			//for(int j = 0; j< grid[i].length; j++) {//each char representing entity
				grid[i] = data.get(i).toCharArray();
			//}
		}
		return grid;
	}
	
	/**
	 * Reads xml and extracts the documents, identified by <doc> tag.
	 * @param xmlString
	 * @return
	 */
	public Map<String, String> readMultilingualXMLString(String xmlString){
		Map<String, String> docs = new HashMap<String, String>();
		try {
			SAXParserFactory spf = SAXParserFactory.newInstance();
			spf.setNamespaceAware(true);
			
			SAXParser saxParser = spf.newSAXParser();
			//CharsetDecoder decoder = StandardCharsets.ISO_8859_1.newDecoder();
			
			Reader isr = new java.io.StringReader(xmlString);
			InputSource is = new InputSource();
			is.setCharacterStream(isr);
			saxParser.parse(is, this.new DocumentSaxParser(docs,false));
			//InputStream is = org.apache.commons.io.IOUtils.toInputStream(xmlString, StandardCharsets.ISO_8859_1);
			
			//saxParser.parse(new StringBufferInputStream(xmlString), this.new DocumentSaxParser(docs,false));
			
			//saxParser.parse(new InputSource(new java.io.StringReader(xmlString, decoder)), this.new DocumentSaxParser(docs,false));
			//s/axParser.parse(new InputStream(xmlString, decoder)), this.new DocumentSaxParser(docs,false));
			
		} catch (SAXException | IOException | ParserConfigurationException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		return docs;
	}
	/**
	 * Reads xml and extracts the documents, identified by <doc> tag.
	 * @param xmlString
	 * @return
	 */
	public Map<String, String> readXMLString(String xmlString){
		Map<String, String> docs = new HashMap<String, String>();
		try {
			SAXParserFactory spf = SAXParserFactory.newInstance();
			spf.setNamespaceAware(true);		
			SAXParser saxParser = spf.newSAXParser();
			
			//CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder();
			//saxParser.parse(new StringBufferInputStream(xmlString), this.new DocumentSaxParser(docs,false));
			
			
			Reader isr = new java.io.StringReader(xmlString);
			InputSource is = new InputSource();
			is.setCharacterStream(isr);
			saxParser.parse(is, this.new DocumentSaxParser(docs,false));
			
		} catch (SAXException | IOException | ParserConfigurationException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		return docs;
	}
	
	/**
	 * Reads xml and extracts the documents, identified by <doc> tag.
	 * @param xmlString
	 * @return
	 */
	public Map<String, String> readXMLfromConsole(){
		
		//Map<String, List<String>> docIds = new LinkedHashMap<String,List<String>>();
		Map<String, String> docIds = new LinkedHashMap<String, String>();
		try {
			SAXParserFactory spf = SAXParserFactory.newInstance();
			spf.setNamespaceAware(true);
			
			SAXParser saxParser = spf.newSAXParser();
			
			CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder();
			
			Reader reader = new BufferedReader(new InputStreamReader(System.in));
			
			InputSource inputsource = new InputSource(reader);
			inputsource.setEncoding("UTF-8");
			
			saxParser.parse(inputsource, this.new DocumentSaxParser( docIds, true));
			
		} catch (SAXException | IOException | ParserConfigurationException e) {
			
			e.printStackTrace();
		}
		
		
		return docIds;
	}
	
	public Map<String, List<String>> readXMLwithDocIds(String filename){
		
		Map<String, List<String>> docs = new LinkedHashMap<String, List<String>>();
		try {
			SAXParserFactory spf = SAXParserFactory.newInstance();
			spf.setNamespaceAware(true);
			
			SAXParser saxParser = spf.newSAXParser();
			
			CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder();
			Reader reader =  new BufferedReader(new InputStreamReader(new FileInputStream(new File(filename)), decoder));
			
			InputSource inputsource = new InputSource(reader);
			inputsource.setEncoding("UTF-8");
			saxParser.parse(inputsource, this.new DocumentSaxParser(docs));
		}catch (SAXException | IOException | ParserConfigurationException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		return docs;
	}
		
	/**
	 * Reads xml and extracts the documents, identified by <doc> tag.
	 * @param xmlString
	 * @return
	 */
	public Map<String,String> readXML(String filename){
		
		Map<String, String> docs = new HashMap<String,String>();
		try {
			SAXParserFactory spf = SAXParserFactory.newInstance();
			spf.setNamespaceAware(true);
			
			SAXParser saxParser = spf.newSAXParser();
			
			CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder();
			Reader reader =  new BufferedReader(new InputStreamReader(new FileInputStream(new File(filename)), decoder));
			
			InputSource inputsource = new InputSource(reader);
			inputsource.setEncoding("UTF-8");
			
			//if(isMultipleDocs){
			saxParser.parse(inputsource, this.new DocumentSaxParser(docs, true));
			//}else {
				//saxParser.parse(inputsource, this.new SentenceSaxParser(docs));
			//}
			
			
		} catch (SAXException | IOException | ParserConfigurationException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		return docs;
	}
	
	/**
	 * Reads xml and extracts the documents, identified by <doc> tag with <seg> tags for sentences.
	 * @param xmlString
	 * @return
	 */
	//public List<List<String>> readSGML(String filename){
	public List <String> readSGML(String filename){
		
		List<String> docs = new ArrayList<String>();
		//List <List<String>> docs  = new ArrayList<List<String>>();
		try {
			SAXParserFactory spf = SAXParserFactory.newInstance();
			spf.setNamespaceAware(true);
			
			SAXParser saxParser = spf.newSAXParser();
			
			CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder();
			Reader reader =  new BufferedReader(new InputStreamReader(new FileInputStream(new File(filename)), decoder));
			
			InputSource inputsource = new InputSource(reader);
			inputsource.setEncoding("UTF-8");
			
			saxParser.parse(inputsource, this.new SentenceSaxParser(docs));
			
			
		} catch (SAXException | IOException | ParserConfigurationException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		return docs;
	}
	
	/**
	 * For text marked up with <doc> tags, reflecting document breaks. 
	 * @author Karin
	 *
	 */
	private class DocumentSaxParser extends DefaultHandler{
		private Map<String, String> docs;
		//private List <String> sentences;
		//private List <String> docAsString;
		private Map<String, List<String>> docSentences;
		private StringBuffer content;// = new StringBuffer();
		private List<String> contents;
		private boolean inElement;
		private String id;
		private int dummy_id = 0;
		
		/**
		 * simply tracks doc content, no attributes
		 * @param docs
		 */
		/*public DocumentSaxParser(List<String> sentences) {
			this.docAsString = sentences;
		}*/
		public DocumentSaxParser(Map<String, String> docs, boolean multiple) {
			this.docs= docs;
		}
		
		/** 
		 * this constructor will track doc ids with relevant doc
		 * @param docIds
		 */
		public DocumentSaxParser(Map<String, List<String>> docSentences) {
			this.docSentences = docSentences;
		}
		
		public void startElement(String s, String s1, String elementName, Attributes attributes) throws SAXException {
			if (elementName.equalsIgnoreCase("doc")) { 
				content = new StringBuffer();
				contents = new ArrayList<String>();
				inElement =  true;
				if(attributes != null){
					//this.id = attributes.getValue(1);
					//this.id = attributes.getValue("docid");
					if(attributes.getValue("docid") != null){
						this.id = attributes.getValue("docid");
					}else{
						this.id = attributes.getValue("id");
					}
				}
			}dummy_id++;
		}
		public void characters (char characters[], int start, int length){
			if(content != null && inElement){
				content.append(characters, start, length);
				contents.add(String.valueOf(characters));
			}
		}
		
		public void endElement(String s, String s1, String element) throws SAXException {
			if (element.equalsIgnoreCase("doc")) {
				if(docSentences != null){
					if (id != null){
						docSentences.put(id, contents);
						//sentences.add(contents);
						//String.join(";", contents)
						//docAsString.add(content.toString());
					}else{
						docSentences.put(String.valueOf(dummy_id),contents);
					}
				}else if(docs != null){
					//docIds.put(id, content.toString());
					if (id != null){
						docs.put(id, content.toString());
					}else{
						docs.put(String.valueOf(dummy_id), content.toString());
					}
				}
				
				inElement = false;
			}
		}
	}
	
	/**
	 * For text marked up with <seg> tags inside <doc> tags, reflecting sentence breaks, within document. 
	 * @author Karin
	 *
	 */
	private class SentenceSaxParser extends DefaultHandler{
		
		//private List <List<String>> docs;
		private List <String> docs;
		private List <String> sentences;
		private StringBuffer content;// = new StringBuffer();
		private boolean inElement;
		private boolean inSentence;
		
		
		public SentenceSaxParser(List<String> docs) {
		//	this.docs = docs;
		//}
		//public SentenceSaxParser(List<List<String>> docs) {
			//this.sentences = sentences;
			this.docs = docs;
			sentences = new ArrayList<String>();
		}
		public void startElement(String s, String s1, String elementName, Attributes attributes) throws SAXException {
			if (elementName.equalsIgnoreCase("doc")) {
				//content = new StringBuffer();
				inElement =  true;
			}
			if (elementName.equalsIgnoreCase("seg")) {
				content = new StringBuffer();
				inSentence =  true;
			}
		}
		public void characters (char characters[], int start, int length){
			if(content != null && inSentence)content.append(characters, start, length);
		}
		
		public void endElement(String s, String s1, String element) throws SAXException {
			if (element.equals("seg")) {
				sentences.add(content.toString());
				inSentence = false;
			}
			if (element.equalsIgnoreCase("doc")) {
				
				if(docs != null){
					docs.addAll(sentences );
				}
				inElement = false;
			}
		}
	}
}
