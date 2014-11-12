package nlp.framework.discourse;

import java.io.BufferedOutputStream;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.nio.charset.CharsetDecoder;
import java.nio.charset.StandardCharsets;
import java.util.Map;

public class FileOutputUtils {

	/**
	 * Prints the grid to the file of filename
	 * Replaces empty cells with '-'
	 * @param filename
	 * @param grid two dimensional array of chars
	 */
	public static void writeGridToFile(String filename, char grid [][]){
		OutputStream output = null;
		try{
			//StringBuilder contents = new StringBuilder();
			CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder();
			output = new BufferedOutputStream(new FileOutputStream(new File(filename)));
			
			for(int i = 0; i< grid.length; i++) {//each sentence
				for(int j = 0; j< grid[i].length; j++) {//each char representing entity
					if(grid[i][j] == 0){
						output.write('-');
					}else{
						output.write(grid[i][j]);
					}
				}output.write('\n');
			 }
		} catch(IOException e) {
			e.printStackTrace();
			System.exit(1);
			
		}
		finally{
			 try {  output.close();  }  catch (Exception e) { /* log it ?*/ }
		}
	}
	
	public static void writeDebugToFile(String filename, String debugstatement){
		//OutputStream output = null;
		BufferedWriter writer = null;
		try{
			//StringBuilder contents = new StringBuilder();
			//CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder();
			writer =  new BufferedWriter(new OutputStreamWriter(new FileOutputStream(new File(filename))));
			//output = new BufferedOutputStream(new FileOutputStream(new File(filename)));
			writer.write(debugstatement);		
			
		} catch(IOException e) {
			e.printStackTrace();
			System.exit(1);
			
		}
		finally{
			 try {  writer.close();  }  catch (Exception e) { /* log it ?*/ }
		}
		
			
	}
	public static void writeLexicalisedGridToFile(String filename, char grid [][]){
		
	
	}
	
	/**
	 * Prints the grids to files in path
	 * Replaces empty cells with '-'
	 * @param filename
	 * @param grid two dimensional array of chars
	 */
	public static void writeGridsToFile(String path, char[][][] grids){
		 
		for(int i = 0 ; i< grids.length; i++ ){
			writeGridToFile(path+"file"+i,  grids [i]);
		}
	}
	
	
	/**
	 * outputs given transition probablilities to file, in tablular format
	 * @param filename
	 * @param transitionProbabilities
	 */
	public static void writeEntityTransitionsToTable(String filename, Map <String, Double> transitionProbabilities ){
		//OutputStream output = null;
		BufferedWriter writer = null;
		try{
			//CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder();
			//output = new BufferedOutputStream(new FileOutputStream(new File(filename)));
			writer = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(new File(filename))));
			
			//for each transition, output the probability for this document
			for(String key : transitionProbabilities.keySet()){
				writer.write(key+ " : ");
				writer.write(transitionProbabilities.get(key).toString());
				writer.write(key+ "\n");
			}
		}catch(IOException e) {
			e.printStackTrace();
			System.exit(1);
			
		}
		finally{
			 try { writer.close();  }  catch (Exception e) { /* log it ?*/ }
		}
		
	}

	public static void writeGraphCoherenceToFile(String filename, int fileidx, BipartiteGraph bipartitegraph) {
		OutputStream output = null;
		try{
		
			CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder();
			output = new BufferedOutputStream(new FileOutputStream(new File(filename)));
		
			output.write(fileidx);
			output.write(' ');
			output.write((byte)bipartitegraph.getLocalCoherence(filename, 	BipartiteGraph.UNWEIGHTED_PROJECTION));
			output.write('\n');
			
		}catch(IOException e) {
			e.printStackTrace();
			System.exit(1);
			
		}
		finally{
			try {  output.close();  }  catch (Exception e) { /* log it ?*/ }
		}
		
	}

	public static void streamToFile(String outputfile,StringBuffer buffer) {
		OutputStream output = null;
		try{
		
			CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder();
			output = new BufferedOutputStream(new FileOutputStream(new File(outputfile)));
			System.out.print("streaming- "+buffer.toString());
			output.write(buffer.toString().getBytes());
			
			
		}catch(IOException e) {
			e.printStackTrace();
			System.exit(1);
			
		}
		finally{
			try {  output.close();  }  catch (Exception e) { /* log it ?*/ }
		}
	}
}
