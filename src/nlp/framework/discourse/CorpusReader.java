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
import java.io.Reader;
import java.io.StringBufferInputStream;
import java.nio.charset.CharsetDecoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

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
	public static List<String> readDataAsDocs(String filename){
		List <String> docs = new ArrayList<String>();
		
		BufferedReader input =  null;
		try{
			StringBuilder contents = new StringBuilder();
			
			CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder();
			input =  new BufferedReader(new InputStreamReader(new FileInputStream(new File(filename)), decoder));
			
			for(String line = input.readLine(); line != null; line = input.readLine()) {
				
				//new doc marked by uppercase word??
				//int endOfFirstWord = line.indexOf(' ', 0);
				//String firstWord = line.substring(0, endOfFirstWord);
				//if(firstWord.toUpperCase().equals(firstWord) && contents.length() != 0){//first word all uppercase, therefore new doc
					//add prev doc to list and start new one
					//docs.add(contents.toString());
					//contents = new StringBuilder();					
					contents.append(line);
					contents.append("\n");
				//}else{
				//	contents.append(line);
				//}
			 }
			docs.add(contents.toString());
			  
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
			
			//BufferedReader input = new BufferedReader(new FileReader(new File(filename)));
			//BufferedReader input =  new BufferedReader(new InputStreamReader(new FileInputStream(new File(filename)),  "UTF-8"));
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
	public List<String> readXML(String filename, boolean isMultipleDocs){
		//BufferedReader input =  null;
		//StringBuilder contents = new StringBuilder();
		List<String> docs = new ArrayList<String>();
		try {
			SAXParserFactory spf = SAXParserFactory.newInstance();
			spf.setNamespaceAware(true);
			
			SAXParser saxParser = spf.newSAXParser();
			
			CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder();
			Reader reader =  new BufferedReader(new InputStreamReader(new FileInputStream(new File(filename)), decoder));
			//new InputStreamReader(new FileInputStream(new File(filename)), decoder)			
			//InputStream is = new FileInputStream(new File(filename)),
			InputSource inputsource = new InputSource(reader);
			inputsource.setEncoding("UTF-8");
			
			if(isMultipleDocs){
				saxParser.parse(inputsource, this.new DocumentSaxParser(docs));
			}else {
				saxParser.parse(inputsource, this.new SentenceSaxParser(docs));
			}
			
			
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
		private StringBuffer content;// = new StringBuffer();
		private boolean inElement;
		
		public DocumentSaxParser(List<String> docs) {
			this.docs = docs;
		}
		public void startElement(String s, String s1, String elementName, Attributes attributes) throws SAXException {
			if (elementName.equalsIgnoreCase("doc")) {
				content = new StringBuffer();
				inElement =  true;
			}
		}
		public void characters (char characters[], int start, int length){
			if(content != null && inElement)content.append(characters, start, length);
		}
		
		public void endElement(String s, String s1, String element) throws SAXException {
			if (element.equalsIgnoreCase("doc")) {
				docs.add(content.toString());
				inElement = false;
			}
		}		

	}
	private class SentenceSaxParser extends DefaultHandler{
		
		private static final String FULLSTOP = ".";
		private static final String QUESTIONMARK = "?";
		private static final String EXCLAMATIONMARK = "!";
		private List <String> sentences;
		private StringBuffer content;// = new StringBuffer();
		private boolean inElement;
		private boolean inSentence;
		
		public SentenceSaxParser(List<String> sentences) {
			this.sentences = sentences;
		}
		public void startElement(String s, String s1, String elementName, Attributes attributes) throws SAXException {
			if (elementName.equalsIgnoreCase("doc")) {
				content = new StringBuffer();
				inElement =  true;
			}
			if (elementName.equalsIgnoreCase("s")) {
				//content = new StringBuffer();
				inSentence =  true;
			}
		}
		public void characters (char characters[], int start, int length){
			if(content != null && inSentence)content.append(characters, start, length);
		}
		
		public void endElement(String s, String s1, String element) throws SAXException {
			if (element.equals("s")) {
				//check that the sentence element ends with full stop
				int EOS = content.length();
				String lastCharacter = String.valueOf(content.charAt(EOS-2));
				if(FULLSTOP.equals(lastCharacter) == false && EXCLAMATIONMARK.equals(lastCharacter) == false && QUESTIONMARK .equals(lastCharacter) == false){
					//add one
					content.append(FULLSTOP);
				}
				//sentences.add(content.toString());
				inSentence = false;
			}
			if (element.equalsIgnoreCase("doc")) {
				sentences.add(content.toString());
				inElement = false;
			}
			
		}		

	}

}
