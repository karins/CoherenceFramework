package nlp.framework.discourse;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import junit.framework.TestCase;



public class EntityGridFrameworkTest extends TestCase {
	 
	//private EntityGridFramework gridframework;
	public static final String teststring1 = "I love Berlin. Berlin is a very cosmopolitan city in Germany. The city is just buzzing.";
	public static final String teststring2 = "The atom is a basic unit of matter, it consists of a dense central nucleus surrounded by a cloud of negatively charged electrons.";
	public static final String teststringA = "I am going to travel to Berlin.";
	public static final String teststringB = "Berlin is a very cosmopolitan city in Germany.";
	public static final String teststringC = "The city is just buzzing.";
	public static final String message = "Entity incorrectly extracted.";
	public static final String messageXml = "Wrong number of docs extracted from xml.";
	public static final String xml = "<refset setid=\"newsdev2009\"><doc docid=\"napi.hu/2007/12/12/0\" genre=\"news\"><hl><seg id=\"1\"> Food: Where European inflation slipped up </seg>"+
			"</hl><p><seg id=\"2\"> The skyward zoom in food prices is the dominant force behind the speed up in eurozone inflation. </seg></p></doc></refset>";
	public static final String xml2 ="<refset setid=\"newsdev2009\"><doc docid=\"napi.hu/2007\"><hl><seg id=\"1\"> Government crisis coming, says Gallup </seg></hl><p><seg id=\"2\">"+
			"Fidesz support shot up significantly in early December after a lengthy period of just holding its own. "+
			"This gives it the strongest support base it has seen since 2002, while Gallup reports support for the socialists at an all-time low of 13 percent. </seg></p></doc>"+
			"<doc><p><seg id=\"15\"> In comparison, only 55 percent said it would definitely vote in parliamentary elections if they were to be held this Sunday while another 15 percent said it most likely would cast a ballot. "
			+"Given current determination to vote, the referendum is certain to be valid. </seg></p></doc></refset>";
	
	public static final String xmlFrench = "<refset setid=\"newsdev2009\"><doc docid=\"napi.hu/2007/12/12/0\" genre=\"news\"><hl><seg id=\"1\"> L'inflation, en Europe, a dérapé sur l'alimentation </seg>"+
			"</hl><p><seg id=\"2\">  L'inflation accélérée, mesurée dans la zone euro, est due principalement à l'augmentation rapide des prix de l'alimentation. </seg></p></doc></refset>";
	
	public static final String xmlFrench2 ="<refset setid=\"newsdev2009\"><doc docid=\"napi.hu/2007\"><hl><seg id=\"1\">Gallup indique une crise du gouvernement </seg></hl><p><seg id=\"2\">"+
			"Après une longue stagnation, le nombre des partisans du Fidesz (Alliance des jeunes démocrates) a augmenté significativement début décembre. "+
			"Ainsi depuis 2002, il dispose actuellement du plus grand nombre de partisans, alors que Gallup (Institut de sondage) n'a jamais constaté auparavant un aussi faible soutien socialiste, à savoir 13 pour cent. </seg></p></doc>"+
			"<doc><p><seg id=\"15\"> Pour faire la comparaison, pour une élection législative organiser dimanche prochain, seulement 55 pour cent des sondés participeraient certainement et 15 pour cent complémentaires participeraient probablement. "
			+"Suivant les intentions actuelles, le résultat du référendum ne ferait aucun doute. </seg></p></doc></refset>";

	public static final List<String> sentences = new ArrayList<String>();
	static{
		sentences.add(teststringA);
		sentences.add(teststringB);
		sentences.add(teststringC);
	}
	
	@Override
	protected void setUp() throws Exception {		
		super.setUp();
		//gridframework = new EntityGridFramework( true);
	}
	
	
	/**
	 * Read in source text and invoke coreference resolve to identify entities.
	 * Test that entities are resolved
	 */
	/*public void testEntityResolver(){
		
		char grid [][] = gridframework.identifyEntities();
		assertEquals(message, '-',grid[0][4]);
		assertEquals(message, 'O',grid[0][6]);//Berlin
		assertEquals(message, 'S',grid[1][0]);//Berlin
		assertEquals(message, '-',grid[1][6]);
		assertEquals(message, 'X',grid[1][5]);//city
		assertEquals(message, 'O',grid[1][7]);//Germany
		assertEquals(message, 'S',grid[2][1]);//city
		assertEquals(message, '-',grid[2][4]);
	}*/
	
	
	public void testIdentifyEntities(){
		EntityGridFramework gridframework = getEntityGridFramework();
		Map<String, ArrayList<Map<Integer, String>>> entities = gridframework.identifyEntitiesFromSentences(teststring1);
		
		List<Map<Integer, String>> berlinOccurences = entities.get("Berlin");
		assertEquals(message, 2, berlinOccurences.size());
		Map<Integer, String> occurance = berlinOccurences.get(0);
		assertEquals(message, "O", occurance.get(0));
		Map<Integer, String> occurance1 = berlinOccurences.get(1);
		assertEquals(message, "S", occurance1.get(1));
		
		List<Map<Integer, String>> cityOccurences = entities.get("city");
		assertEquals(message, 2, cityOccurences.size());
		Map<Integer, String> occurance2 = cityOccurences.get(0);
		assertEquals(message, "X", occurance2.get(1));
		Map<Integer, String> occurance3 = cityOccurences.get(1);
		assertEquals(message, "S", occurance3.get(2));
	}


	protected EntityGridFramework getEntityGridFramework() {
		
		return new EntityGridFramework();
	}	
	public void testEntityResolver(){
		EntityGridFramework gridframework = getEntityGridFramework();
		char grid [][] = gridframework.identifyEntitiesAndConstructGrid(teststring1);	
		System.out.println("O and "+grid[0][1]);
		assertEquals(message, 'O',grid[0][1]);//sentence 1, Berlin
		assertEquals(message, 'S',grid[1][1]);//sentence 2, Berlin
		assertEquals(message, 'X',grid[1][0]);//sentence 2, city
		assertEquals(message, 'X',grid[1][2]);//sentence 2, Germany
		assertEquals(message, 'S',grid[2][0]);//sentence 3, city
		
	}
	
	
	/**
	 * Read in source text and invoke coreference resolve to identify entities.
	 * Test that entities are resolved
	 * 
	 */
	public void testEntityResolver2(){
		
		EntityGridFramework gridframework2 = getEntityGridFramework();
		char grid [][] = gridframework2.identifyEntitiesAndConstructGrid(teststring2 );
		
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
		assertEquals(message, 1, Ss);//atom
		assertEquals(message, 5, Xs);//unit
		//assertEquals(message, 4, Os);//matter,nucleaus,cloud,electrons
		//since 3.5.2 new Stanford dependencies..
		
	}
	
	/**
	 * check that a document is correctly extracted from an xml segment 
	 */
	public void testXmlExtractDocs1(){
		EntityGridFramework gridframework = getEntityGridFramework();
		Map<String, String> docs = new CorpusReader().readXMLString(xml);
		int fileidx = 0;
		for(String docAsString: docs.values()){
			
			char grid [][] = gridframework.identifyEntitiesAndConstructGrid(docAsString);
			//FileOutputUtils.writeGridToFile(outputfile+fileidx, grid);
			fileidx++;
		}
		assertEquals(messageXml, 1, fileidx);
	}
	
	/**
	 * check that a document is correctly extracted from an xml segment 
	 */
	public void testXmlExtractDocs2(){
		EntityGridFramework gridframework = getEntityGridFramework();
		Map<String, String> docs = new CorpusReader().readXMLString(xml2);
		int fileidx = 0;
		for(String docAsString: docs.values()){
			
			char grid [][] = gridframework.identifyEntitiesAndConstructGrid(docAsString);
			//FileOutputUtils.writeGridToFile(outputfile+fileidx, grid);
			fileidx++;
		}
		assertEquals(messageXml, 2, fileidx);
	}
	
	/**
	 * check that a document is correctly extracted from an xml segment 
	 */
	public void testFrenchXmlExtractDocs1(){
		//EntityGridFramework gridframework = getEntityGridFramework();
		Map<String, String> docs = new CorpusReader().readMultilingualXMLString(xmlFrench);
		EntityGridFramework gridframework = new EntityGridFactory().getEntityGridFramework( "French");
		int fileidx = 0;
		for(String docAsString: docs.values()){
			
			char grid [][] = gridframework.identifyEntitiesAndConstructGrid(docAsString);
			//FileOutputUtils.writeGridToFile(outputfile+fileidx, grid);
			fileidx++;
		}
		assertEquals(messageXml, 1, fileidx);
 	}
	
	/**
	 * check that a document is correctly extracted from an xml segment 
	 */
	public void testFrenchXmlExtractDocs2(){
		Map<String, String> docs = new CorpusReader().readMultilingualXMLString(xmlFrench2);
		 EntityGridFramework gridframework =  new EntityGridFactory().getEntityGridFramework( "French");
		int fileidx = 0;
		for(String docAsString: docs.values()){
			
			char grid [][] = gridframework.identifyEntitiesAndConstructGrid(docAsString);
			//FileOutputUtils.writeGridToFile(outputfile+fileidx, grid);
			fileidx++;
		}
		assertEquals(messageXml, 2, fileidx);
	}
	/**
	 * Test that entity transitions are correctly extracted, ie that vertical sequences are
	 * extracted from the grid
	 */
	public void testExtractingEntityTransitions(){
		//char grid [][] = gridframework.identifyEntities();
	
		//for(int col = 0; col< grid[row].length.[col]; col++) {//each column
		//	for(int row = 0; j< grid[i].length; row++) {//each char representing entity
			
	}

}
