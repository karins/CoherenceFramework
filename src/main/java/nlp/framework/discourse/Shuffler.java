package nlp.framework.discourse;

import java.io.File;
import java.io.StringReader;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.process.DocumentPreprocessor;

/**
 * Utility class to shuffle sentences within a document.
 * 
 * TODO: TO BE REVISITED FOR WHITESPACE ISSUE
 * 
 * @author Karin
 *
 */
public class Shuffler {

	public static void main(String[] args) {
		
		String directory = args[0];
		String output = args[1];
		Shuffler shuffler = new Shuffler();
		
		System.out.println("dir = "+directory);
		File[] files = new File(directory).listFiles();
		for (File file : files) {
			if (file.isFile()){
				System.out.println("shuffling "+ file.getName());
				String filename = file.getName();
				Map<String,String> docs = new CorpusReader().readDataAsDocs(directory+File.separator+file.getName());
				
				for(String docid : docs.keySet()){
					String asString = docs.get(docid);
					List sentences = new ArrayList<List<HasWord>>(); 
					
					//DocumentPreprocessor dp = new DocumentPreprocessor(new StringReader(asString));
					for (List<HasWord> sentence : new DocumentPreprocessor(new StringReader(asString))){
					//List<HasWord> sentences = new DocumentPreprocessor(new StringReader(asString));
						sentences.add(sentence);						
					}
					Collections.shuffle(sentences);
					//TODO: ISSUE WITH WHITESPACE, SINCE IT IS LOST WHEN READ IN, SO HAS TO BE *CORRECTLY* REINSERTED
					//currently inserts before commas and fullstops. more problematic for trees..
					FileOutputUtils.writeDocToFile(FileOutputUtils.getDirectory(directory, "shuffled"),
													FileOutputUtils.getFilenameWithoutExtensions(filename)+"_shuffled", 
													sentences , true, docid, 
													FileOutputUtils.isCompressed(filename));

				}
			}
		}
				
	}

}
