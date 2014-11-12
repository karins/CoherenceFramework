package nlp.framework.discourse;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;


/**
 * Takes an entity grid and extracts entity transitions of set length and salience.
 *  
 * @author Karin Sim
 *
 */
public class EntityTransitionExtractor {

	private char [][] grid;
	private int salience;
	private int transitionLength;
	private int totalTransitions;
	private Map <String, Double> transitionProbabilities = new HashMap<String, Double>();
	private Map <String, Integer> transitions = new HashMap<String, Integer>();
	
	public EntityTransitionExtractor(String gridFile, int salience,
			int transitionLength) {
		super();
		this.grid = CorpusReader.readGridFromFile(gridFile);
		this.salience = salience;
		this.transitionLength = transitionLength;
	}
	
	public EntityTransitionExtractor(char[][] grid, int salience,
			int transitionLength) {
		super();
		this.grid = grid;
		this.salience = salience;
		this.transitionLength = transitionLength;
	}
	 
	/**
	 * Extract transitions of length @param transitionLength and compute the probabilities
	 */
	public Map extractTransitions(){
		
		
		//calculate the transitions of defined length and divide by total number of transitions
		for(int i = 0; i< grid[0].length; i++) {//each entity
			for(int j = 0; j<= grid.length-transitionLength; j++) {//each sentence
		//for(int i = 0; i< grid.length; i++) {//each entity
		//		for(int j = 0; j<= grid[i].length-transitionLength; j++) {//each sentence
				
				//track entity transitions, length determined by transitionLength 
				
				char transition[] = new char[transitionLength];
				//char transition[] =  { grid[i][j], grid[i][j+1], grid[i][j+2]};
				//transition = Arrays.copyOfRange(grid[i][j], grid[i][j], grid[i][j+transitionLength]);
				for(int k = 0; k< transitionLength; k++){
					transition[k] = grid[k+j][i];
				}
				
				//store in Map, of entity transition String mapped to number of occurances
				String key = Arrays.toString(transition);
				if(transitions.containsKey(key)){
					int count = transitions.get(key).intValue();
					count++;
					transitions.put(key, count);
				}else{
					transitions.put(key, 1);
				}
				totalTransitions++;
			}
		}
		
		
		
		return transitions;
	}
	
	/**
	 * compute transition as ratio of frequency divided by total number of transitions of same length
	 * @return
	 */
	public Map<String, Double> computeProbabilities(){
		
		//compute transition as ratio of frequency divided by total number of transitions of same length
		for(String transition :transitions.keySet()){
			
			Integer occuranceOfTransition = transitions.get(transition);
			System.out.println("occurance: "+occuranceOfTransition.doubleValue()+" / "+totalTransitions);
			double transitionProbability = occuranceOfTransition.doubleValue()/new Double(totalTransitions).doubleValue();
			
			//track salient entitities determined by salience variable
			//if(occuranceOfTransition >= salience){
				transitionProbabilities.put(transition, transitionProbability);
			//}
		}
		
		
		
		return transitionProbabilities;
	}
	
	/**
	 * command line arguments:
	 * format : "C:\\SMT\\datasets\\corpus-PE\\PEofMT_half_noSyntax.mt.grid" "C:\\SMT\\datasets\\corpus-PE\\PEofMT_half_noSyntax.mt.probabilities" 241  2 2
	 * where <li>filename of grid to use </li>
	 * 		<li>filename  to be given to output file which prints probabilities</li>
	 * 		<li>no. of files to be processed</li>
	 * 		<li>transition length, ie how many transitions to include (eg SOX is 3, SO 2)</li>
	 * 		<li>salience, ie threshold for including the entity</li>
	 * @param args
	 */
	public static void main(String args[]){
		String inputgrid = args[0];
		String outputfile = args[1];
		int fileidx = Integer.parseInt(args[2]);
		int transitionLength = Integer.parseInt(args[3]);
		int salience = Integer.parseInt(args[4]);
		
		if(fileidx == 1){
			EntityTransitionExtractor transitionExtractor = new EntityTransitionExtractor(inputgrid, salience, transitionLength);
			Map transitions = transitionExtractor.extractTransitions();
			FileOutputUtils.writeEntityTransitionsToTable(outputfile, transitionExtractor.computeProbabilities());
	
		}
		else{
			
		
			for(int i = 0; i<= fileidx; i++){
				
				EntityTransitionExtractor transitionExtractor = new EntityTransitionExtractor(inputgrid+i, salience, transitionLength);
				Map transitions = transitionExtractor.extractTransitions();
				FileOutputUtils.writeEntityTransitionsToTable(outputfile+i, transitionExtractor.computeProbabilities());
			}
		}
		
	}
	
}
