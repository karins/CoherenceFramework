package nlp.framework.discourse;

import java.util.HashMap;
import java.util.Map;

import junit.framework.TestCase;

public class EntityGridExtractorTest extends TestCase {

	public static String message = "Problem creating grid from ptb";
	public static String testString1 = "(ROOT (NP (NP (NP (NNP Herbert) (NNP Hoover)) (CC and) (NP (DT the) (NN stability) (NN pact))) (. .)))";
	
	public static String ptb1 = "(ROOT (S (S (NP (DT The) (NNP Pact)) (VP (VBZ is) (ADVP (RB already)) (VP (VBG knocking) (NP (NNP Germany)) (PP (IN into) (NP (NN recession)))))) (, ,) (CC and) (S (NP (NP (NNP Italy) (POS 's)) (NN government)) (VP (VBZ is) (VP (VBG struggling) (S (VP (TO to) (VP (VB revise) (NP (PRP$ its) (NN growth) (NNS forecasts)) (ADVP (RB fast) (RB enough) (S (VP (TO to) (VP (VB keep) (PRT (RP up)) (PP (IN with) (NP (VBG falling) (NN output))))))))))))) (. .)))";
	//The Pact is already knocking Germany into recession, and Italy's government is struggling to revise its growth forecasts fast enough to keep up with falling output.
	//--------------S----O-----------------------------------------O----------X-------------------O------------------------O-----S---X
	//(test against output from grid working with raw text)
	//char grid [][]= {{'-','-','-','-','-','-','-','-','-','-','-','-','-','-','S','-','-','-','-','O','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','O','-','-','-','-','-','-','-','-','-','-','X','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','O','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','O','-','-','-','-','-','S','-','-','-','X'}};
	
	 public static String ptb2 ="(ROOT (S (SBAR (IN As) (S (NP (NNP Herbert) (NNP Hoover)) (VP (MD could) (VP (VB attest))))) (, ,) (SBAR (WHADVP (WRB when)) (S (NP (PRP we)) (VP (VBP see) (NP (NP (RB only) (DT the) (JJ economic) (NN policy) (NNS problems)) (PP (IN of) (ADVP (NP (DT a) (NN generation)) (RB ago))))))) (, ,) (NP (PRP we)) (VP (VBP risk) (S (VP (VBG missing) (NP (NP (DT the) (NNS hazards)) (SBAR (WHNP (WDT that)) (S (VP (VBP lie) (ADVP (RB directly)) (PP (IN in) (NP (NP (NN front)) (PP (IN of) (NP (PRP$ our) (NNS eyes)))))))))))) (. .)))";
	//---------------X--------X--------S-------------------OO------------------------O-----------X---------------------------O--------
	//-----------------------X-------------------O--O----S-----X---------------------------------------X-----O-----------------------------O---
	
	public static String ptb3 = "(ROOT (S (PP (IN On) (NP (DT the) (JJ other) (NN hand))) (, ,) (NP (NNP GM)) (VP (VBZ is) (VP (VBG making) (ADJP (JJ sure)) (SBAR (IN that) (S (NP (NP (DT a) (NN decision)) (PP (VBG regarding) (NP (NP (DT the) (NN sale)) (PP (IN of) (NP (NNP Saab)))))) (VP (MD should) (VP (VB be) (VP (VBN made) (PP (IN in) (NP (DT the) (JJ next) (JJ few) (NNS days)))))))))) (. .)))";
	//from git: original from raw data:
	//-------------S--O------X-----------------O-------S-O
	//docid=359 from ptb:
	//---O--------------S----O---SO-----------------------------
	
	
	public static String ptb4 = "(ROOT (S (PP (VBG According) (PP (TO to) (NP (DT an) (NNP EU) (NN study)))) (, ,) (SBAR (IN if) (S (NP (DT all) (NNS cars)) (VP (VBD were) (VP (VBN equipped) (PP (IN with) (NP (DT this) (NN feature))))))) (, ,) (NP (NP (CD 1,100) (JJ fatal) (NNS accidents)) (VP (VBG involving) (NP (NNS pedestrians)))) (VP (MD could) (VP (VB be) (VP (VBN avoided) (NP (DT a) (NN year))))) (. .)))";
	//from raw data:---O------OX------X---------SS------O---------------
	//from pbt: 	--X-----------SXS------------O---------O-------------O----
	
	@Override
	protected void setUp() throws Exception {		
		super.setUp();
	}
	
	/**
	 * override to ensure that correct object returned. in this case we want 
	 * EntityGridExtractor, to extract grid from ptbs. 
	 */
	protected EntityGridExtractor getEntityGridExtractor() {
		
		return new EntityGridExtractor();
	}
	
	/**
	 * Test that entities are correctly tracked
	 * 
	 */
	public void testEntityResolver1(){
		
		EntityGridExtractor extractor = getEntityGridExtractor();
		char grid [][] = extractor.convertPtbsStringToGrids(ptb1);
		
		int Os = 0; 
		int Ss = 0;
		int Xs = 0; 
		//since order is non-deterministic, need to simply count grammatical occurances:
		for(int i = 0; i<grid[0].length; i++){
			switch(grid[0][i]){
			case 'O': Os++;
				break;			
			case 'X': Xs++;
				break;
			case 'S': Ss++;
				break;
			}
		}
		assertEquals(message, 2, Ss);
		assertEquals(message, 2, Xs);
		assertEquals(message, 4, Os);
		
	}

	/**
	 * Test that entities are correctly tracked
	 * 
	 */
	public void testEntityResolver2(){
		Map results = getGridResults(ptb2);
		assertEquals(message, 1, results.get("S"));
		assertEquals(message, 3, results.get("X")); 
		assertEquals(message, 4, results.get("O"));
	}
	
	/** Test that entities are correctly tracked
	 * 
	 */
	public void testEntityResolver3(){
		Map results = getGridResults(ptb3);
		assertEquals(message, 2, results.get("S"));
		assertEquals(message, 1, results.get("X")); 
		assertEquals(message, 3, results.get("O"));
	}
	
	/**
	 * Test that entities are correctly tracked
	 * 
	 */
	public void testEntityResolver4(){
		Map results = getGridResults(ptb4);
		assertEquals(message, 2, results.get("S"));
		assertEquals(message, 2, results.get("X")); 
		assertEquals(message, 3, results.get("O"));
	}
	/**
	 * Test that entities are correctly tracked
	 * 
	 */
	public Map getGridResults(String ptb){
		
		EntityGridExtractor extractor = getEntityGridExtractor();
		char grid [][] = extractor.convertPtbsStringToGrids(ptb);
		
		int Os = 0; 
		int Ss = 0;
		int Xs = 0; 
		//since order is non-deterministic, need to simply count grammatical occurances:
		for(int i = 0; i<grid[0].length; i++){
			switch(grid[0][i]){
			case 'O': Os++;
				break;			
			case 'X': Xs++;
				break;
			case 'S': Ss++;
				break;
			}
		}
		Map<String, Integer> roles = new HashMap<String, Integer>();
		roles.put("S", Ss);
		roles.put("X", Xs);
		roles.put("O", Os);
		
		return roles;
		
	}
}
