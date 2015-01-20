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
	
	public InputStream decompressStream(InputStream input) {
		PushbackInputStream pb = new PushbackInputStream( input, 2 ); //we need a pushbackstream to look ahead
		byte [] signature = new byte[2];
		try {
			pb.read( signature );
			pb.unread( signature ); //push back the signature to the stream
		 //read the signature
		
		if( signature[ 0 ] == (byte) 0x1f && signature[ 1 ] == (byte) 0x8b ) //check if matches standard gzip magic number
			return new GZIPInputStream( pb );
		else 
			return pb;
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return pb;
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
	public List<String> readXMLString(String xmlString){
		List<String> docs = new ArrayList<String>();
		try {
			SAXParserFactory spf = SAXParserFactory.newInstance();
			spf.setNamespaceAware(true);
			
			SAXParser saxParser = spf.newSAXParser();
			CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder();
			saxParser.parse(new StringBufferInputStream(xmlString), this.new DocumentSaxParser(docs));
			
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
		
		Map<String, String> docIds = new HashMap<String, String>();
		try {
			SAXParserFactory spf = SAXParserFactory.newInstance();
			spf.setNamespaceAware(true);
			
			SAXParser saxParser = spf.newSAXParser();
			
			CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder();
			
			Reader reader = new BufferedReader(new InputStreamReader(System.in));
			
			InputSource inputsource = new InputSource(reader);
			inputsource.setEncoding("UTF-8");
			
			saxParser.parse(inputsource, this.new DocumentSaxParser( docIds));
			
		} catch (SAXException | IOException | ParserConfigurationException e) {
			
			e.printStackTrace();
		}
		
		
		return docIds;
	}
	
	public Map<String, String> readXMLwithDocIds(String filename){
		
		Map<String, String> docs = new HashMap<String, String>();
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
	public List<String> readXML(String filename){
		
		List<String> docs = new ArrayList<String>();
		try {
			SAXParserFactory spf = SAXParserFactory.newInstance();
			spf.setNamespaceAware(true);
			
			SAXParser saxParser = spf.newSAXParser();
			
			CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder();
			Reader reader =  new BufferedReader(new InputStreamReader(new FileInputStream(new File(filename)), decoder));
			
			InputSource inputsource = new InputSource(reader);
			inputsource.setEncoding("UTF-8");
			
			//if(isMultipleDocs){
				saxParser.parse(inputsource, this.new DocumentSaxParser(docs));
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
	public List<List<String>> readSGML(String filename){
		
		//List<String> docs = new ArrayList<String>();
		List <List<String>> docs  = new ArrayList<List<String>>();
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
		
		private List <String> docs;
		private Map<String, String> docIds;
		private StringBuffer content;// = new StringBuffer();
		private boolean inElement;
		private String id;
		
		/**
		 * simply tracks doc content, no attributes
		 * @param docs
		 */
		public DocumentSaxParser(List<String> docs) {
			this.docs = docs;
		}
		
		/** 
		 * this constructor will track doc ids with relevant doc
		 * @param docIds
		 */
		public DocumentSaxParser(Map<String, String> docIds) {
			this.docIds = docIds;
		}
		
		public void startElement(String s, String s1, String elementName, Attributes attributes) throws SAXException {
			if (elementName.equalsIgnoreCase("doc")) { 
				content = new StringBuffer();
				inElement =  true;
				if(attributes != null){
					this.id = attributes.getValue(0);
				}
			}
		}
		public void characters (char characters[], int start, int length){
			if(content != null && inElement)content.append(characters, start, length);
		}
		
		public void endElement(String s, String s1, String element) throws SAXException {
			if (element.equalsIgnoreCase("doc")) {
				if(docs != null){
					docs.add(content.toString());
				}else if(docIds != null){
					docIds.put(id, content.toString());
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
		
		private List <List<String>> docs;
		private List <String> sentences;
		private StringBuffer content;// = new StringBuffer();
		private boolean inElement;
		private boolean inSentence;
		
		public SentenceSaxParser(List<List<String>> docs) {
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
					docs.add(sentences );
				}
				inElement = false;
			}
		}
	}
}
