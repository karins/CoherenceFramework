package nlp.framework.discourse;

import java.util.Map;

import junit.framework.TestCase;

public class EntityTransitionExtractorTest extends TestCase {

	public static final String teststring = "The atom is a basic unit of matter, it consists of a dense central nucleus surrounded by a cloud of negatively charged electrons.";
	public static final String message = "Entity transition incorrectly calculated.";
	public static final String SO = "SO";
	public static final String OO = "OO";
	public static final String SNULL = "S-";
	public static final String XX = "XX";
	public static final String OS = "OS";
	public static final String OX = "OX";
	/**
	 * test mini-grid
	 */
	public void testExtractEntityTransitionsSize(){
		
		EntityGridFramework gridframework = new EntityGridFramework();
		char grid [][] = gridframework.identifyEntitiesAndConstructGrid(teststring);
		//CorpusReader.writeGridToFile(outputfile, grid);
		for(int i = 0; i< grid.length; i++) {//each sentence
			for(int j = 0; j< grid[i].length; j++) {//each char representing entity
				if(grid[i][j] == 0){
					grid[i][j]  = '-';
				}
			}
		}
		EntityTransitionExtractor transitionExtractor = new EntityTransitionExtractor(grid, 2, 2);
		Map transitions = transitionExtractor.extractTransitions();
		assertEquals(message, 5, transitions.size());
	}
	
	public void testExtractEntityTransitions(){
		
		EntityTransitionExtractor transitionExtractor = new EntityTransitionExtractor("C:\\SMT\\grid-mini-test", 2, 2);
		Map transitions = transitionExtractor.extractTransitions();
		//[O, -]
		assertEquals(message,7, transitions.get("[X, X]"));
		assertEquals(message, 3, transitions.get("[S, O]"));
		assertEquals(message, 2,  transitions.get("[S, S]"));
		assertEquals(message, 1401,  transitions.get("[-, -]"));
		assertEquals(message, 38,  transitions.get("[-, X]"));
		assertEquals(message, 25,  transitions.get("[-, O]"));
		assertEquals(message,18,  transitions.get("[-, S]"));
	}	
	
	public void testExtractEntityTransitions2(){
		
		EntityTransitionExtractor transitionExtractor = new EntityTransitionExtractor("C:\\SMT\\grid-mini-test", 2, 3);
		Map transitions = transitionExtractor.extractTransitions();
		//[O, -]
		assertEquals(message,35, transitions.get("[X, -, -]"));
		assertEquals(message, 1, transitions.get("[S, O, X]"));
		assertEquals(message, 1271, transitions.get("[-, -, -]"));
		assertEquals(message, 2, transitions.get("[X, X, X]"));
	}	

	public void testComputeProbabilities(){
		
		EntityTransitionExtractor transitionExtractor = new EntityTransitionExtractor("C:\\SMT\\grid-mini-test", 2, 2);
		Map transitions = transitionExtractor.extractTransitions();
		Map probabilities = transitionExtractor.computeProbabilities();
		assertEquals(message, 0.004419191919191919, probabilities.get("[X, X]"));
		assertEquals(message, 0.001893939393939394, probabilities.get("[S, O]"));
		assertEquals(message, 0.0012626262626262627, probabilities.get("[S, S]"));
		assertEquals(message, 0.884469696969697, probabilities.get("[-, -]"));
		assertEquals(message, 0.023989898989898988, probabilities.get("[-, X]"));
		assertEquals(message, 0.015782828282828284, probabilities.get("[-, O]"));
		assertEquals(message,0.011363636363636364,probabilities.get("[-, S]"));
	}	
	
	public void testComputeProbabilities2(){
		
		EntityTransitionExtractor transitionExtractor = new EntityTransitionExtractor("C:\\SMT\\grid-mini-test", 2, 3);
		Map transitions = transitionExtractor.extractTransitions();
		Map probabilities = transitionExtractor.computeProbabilities();
		assertEquals(message,0.0013175230566534915, probabilities.get("[X, X, X]"));
		assertEquals(message, 6.587615283267457E-4, probabilities.get("[S, O, X]"));
		assertEquals(message, 6.587615283267457E-4, probabilities.get("[S, S, X]"));
		assertEquals(message, 0.8318062827, probabilities.get("[-, -, -]"));
		assertEquals(message, 0.0013175231, probabilities.get("[O, X, X]"));
		assertEquals(message,0.0092226614, probabilities.get("[-, -, S]"));
	}	
}
