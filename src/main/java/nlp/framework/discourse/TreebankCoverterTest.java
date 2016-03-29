package nlp.framework.discourse;

import java.util.List;
import java.util.Map;

import junit.framework.TestCase;

import org.javatuples.Triplet;

public class TreebankCoverterTest extends TestCase {

	public static final String message = "Parse tree incorrectly constructed.";
	
	public static final String xml = "<refset setid=\"newsdev2009\"><doc docid=\"napi.hu/2007/12/12/0\" genre=\"news\"><hl><seg id=\"1\"> Food: Where European inflation slipped up. </seg>"+
			"</hl><p><seg id=\"2\"> The skyward zoom in food prices is the dominant force behind the speed up in eurozone inflation. </seg></p></doc></refset>";
	public static final String xml2 ="<refset setid=\"newsdev2009\"><doc docid=\"napi.hu/2007\"><hl><seg id=\"1\"> Government crisis coming, says Gallup. </seg></hl><p><seg id=\"2\">"+
			"Fidesz support shot up significantly in early December after a lengthy period of just holding its own. "+
			"This gives it the strongest support base it has seen since 2002, while Gallup reports support for the socialists at"+
			" an all-time low of 13 percent. </seg></p></doc>"+
			"<doc><p><seg id=\"15\"> In comparison, only 55 percent said it would definitely vote in parliamentary elections if they were to be held this Sunday while another 15 percent said it most likely would cast a ballot. "
			+"Given current determination to vote, the referendum is certain to be valid. </seg></p></doc></refset>";

	public static final String string2 = "Europe's Divided Racial House. A common feature of Europe's extreme right is its racism and use of the immigration issue as a political wedge. "+
			"The Lega Nord in Italy, the Vlaams Blok in the Netherlands, the supporters of Le Pen's National Front in France, are all examples of parties or movements formed on the "+
			"common theme of aversion to immigrants and promotion of simplistic policies to control them. ";
	
	public static final String string1 ="That's good news, Dr Leak said.";
	public static final String xmlFrench = "<refset setid=\"newsdev2009\"><doc docid=\"napi.hu/2007/12/12/0\" genre=\"news\"><hl><seg id=\"1\"> L'inflation, en Europe, a dérapé sur l'alimentation </seg>"+
			"</hl><p><seg id=\"2\">  L'inflation accélérée, mesurée dans la zone euro, est due principalement à l'augmentation rapide des prix de l'alimentation. </seg></p></doc></refset>";
	
	public static final String string3 ="Still, European governments typically complain about the lack of fiscal resources to support R&D (a far fetched argument given the miniscule share of research spending in the oversized European budgets) and, whenever the European Commission allows them, they subsidize innovative firms, or those that they think are more likely to invest in R&D.";
	public static final String string4 = "France and Italy, for example, demanded that the limits imposed by the budget deficits of euro zone members by the Stability and Growth Pact exclude public spending for research.";
	public static final String string5 = "However, if we distinguish between the industries that produce information and communications technologies (ICT) and those that are simply users of such technologies, we can see that the productivity growth gap stems almost entirely from the weakness of Europe's ICT producing sector.";
	public static final String string6 = "The coup de grâce was delivered by the government's decision (when the crisis came) to keep bank deposits fixed in dollars and to change debts owed to banks into pesos, thereby bankrupting the country's financial system with a single stroke of the pen.";
	public static final String string7 ="Yet during the boom years of 1993-1998, public spending outran taxes enough to push Argentina's debt-to-GDP ratio from 29 to 44%.";
	public static final String string8 ="When the dollar appreciated and recession came, politicians with too little statesmanship to balance the budget in good times turned out to have too little courage to balance the budget when times turned hard.";
	public static final String fourSentences = "The establishment view--say, in US Treasury Undersecretary John Taylor's office--is that Argentina's collapse is the fault of its politicians."+
								" I half-agree with this view. Argentine leaders were repeatedly warned that keeping the exchange rate constant and fixing the peso's value against the US dollar risked sending the economy into recession if the dollar gained value."+
								" Argentine politicians were also warned that their peso policy could not be sustained unless the ratio of national debt to GDP was falling.";

	public static final String testProductions1 = "The two concerns said they entered into a definitive merger agreement under which Ratners will begin a tender offer for all of Weisield's common shares for $57.50 each.";
	public static final String testProductions2 = "Commonwealth Edison said it is already appealing the underlying  commission order and is considering appealing Judge Curry's order.";
	public static final String testProductions3 = "'It has to be considered as an additional risk for the investor,' said Gary Smaby of Smaby Group Inc, Minneapolis.";
	
	public TreebankConverter converter ;
	@Override
	protected void setUp() throws Exception {		
		super.setUp();
		converter = new TreebankConverter(TreebankConverter.SEQUENCES_TYPE);
	}

		
	public void testTreebankExtraction1(){
	
		//TreebankConverter converter = new TreebankConverter();
		
		Map<String, String> docs = new CorpusReader().readXMLString(xml);
		StringBuffer buffer = converter.parseString(docs.get(0),  TreebankConverter.ENGLISH, 2);
		//tree: (ROOT (X (NP (NNP Food)) (: :) (FRAG (SBAR (WHADVP (WRB Where)) (S (NP (JJ European) (NN inflation)) (VP (VBD slipped) (PRT (RP up)))))) (. .)))
		//label :  NP : FRAG .
		//FRAG -> SBAR , 
		
		 //label :  DT RB VB SBAR .
		//tree: (ROOT (S (NP (DT The)) (ADVP (RB skyward)) (VP (VB zoom) (SBAR (IN in) (S (NP (NN food) (NNS prices)) (VP (VBZ is) (NP (NP (DT the) (JJ dominant) (NN force)) (PP (IN behind) (NP (NP (DT the) (NN speed) (PRT (RP up))) (PP (IN in) (NP (NN eurozone) (NN inflation)))))))))) (. .)))
		//NP 
		//tree: (ROOT (S (NP (DT The)) (ADVP (RB skyward)) (VP (VB zoom) (SBAR (IN in) (S (NP (NN food) (NNS prices)) (VP (VBZ is) (NP (NP (DT the) (JJ dominant) (NN force)) (PP (IN behind) (NP (NP (DT the) (NN speed) (PRT (RP up))) (PP (IN in) (NP (NN eurozone) (NN inflation)))))))))) (. .)))
		
		//"NP:nnp : FRAG:sbar . NP:dt ADVP:rb VP:vb ."
		
		assertEquals(message,"NP*nnp : FRAG*sbar . NP*dt ADVP*rb VP*vb .", buffer.toString().trim());
		//assertEquals(message, "NP : FRAG . NP ADVP VP .", buffer.toString().trim());
	}
	
	public void testTreebankExtraction2(){
		
		//TreebankConverter converter = new TreebankConverter();
		
		
		StringBuffer buffer = converter.parseString(string1,  TreebankConverter.ENGLISH, 2);
		//tree: (ROOT (S (S (NP (DT That)) (VP (VBZ 's) (NP (JJ good) (NN news)))) (, ,) (NP (NN Dr) (NN Leak)) (VP (VBD said)) (. .)))
		// label : S , NP VP , 
		//NP VP , NN NN VBD .
		assertEquals(message, "S , NP VP .", buffer.toString().trim());
		
		buffer = converter.parseString(string1,  TreebankConverter.ENGLISH, 3);
		assertEquals(message, "NP VP , NN NN VBD .", buffer.toString().trim());
	}

	public void testTreebankExtraction3(){
		
		//TreebankConverter converter = new TreebankConverter();
		
		//tree: (ROOT (NP (NP (NP (NNP Europe) (POS 's)) (NNP Divided)) (NP (NP (JJ Racial)) (NP (NNP House))) (. .)))
		//tree: (ROOT (S (NP (NP (DT A) (JJ common) (NN feature)) (PP (IN of) (NP (NP (NNP Europe) (POS 's)) (JJ extreme) (NN right)))) (VP (VBZ is) (NP (NP (PRP$ its) (NN racism) (CC and) (NN use)) (PP (IN of) (NP (NP (DT the) (NN immigration) (NN issue)) (PP (IN as) (NP (DT a) (JJ political) (NN wedge))))))) (. .)))
		//tree: (ROOT (S (NP (NP (DT The) (NNP Lega) (NNP Nord)) (PP (IN in) (NP (NNP Italy))) (, ,) (NP (NP (DT the) (NNP Vlaams) (NNP Blok)) (PP (IN in) (NP (DT the) (NNP Netherlands)))) (, ,) (NP (NP (DT the) (NNS supporters)) (PP (IN of) (NP (NP (NNP Le) (NNP Pen) (POS 's)) (NNP National) (NN Front))) (PP (IN in) (NP (NNP France)))) (, ,)) (VP (VBP are) (NP (NP (DT all) (NNS examples)) (PP (IN of) (NP (NP (NNS parties) (CC or) (NNS movements)) (VP (VBN formed) (PP (IN on) (NP (NP (DT the) (JJ common) (NN theme)) (PP (IN of) (NP (NN aversion))))) (PP (TO to) (NP (NP (NNS immigrants) (CC and) (NN promotion)) (PP (IN of) (NP (JJ simplistic) (NNS policies))))) (S (VP (TO to) (VP (VB control) (NP (PRP them)))))))))) (. .)))
		//depth 2: NP NP. NP VP. NP VP.
		
		//depth 3: NP NNP NP NP . NP PP VP VBZ
		StringBuffer buffer = converter.parseString(string2,  TreebankConverter.ENGLISH, 2);
		//NP*np NP*np . NP*np VP*vbz . NP*np VP*vbp .
		assertEquals(message, "NP*np NP*np . NP*np VP*vbz . NP*np VP*vbp .", buffer.toString().trim());
		//assertEquals(message, "NP NP . NP VP . NP VP .", buffer.toString().trim());
	}
	
	public void testTreebankExtraction4(){
		
		//TreebankConverter converter = new TreebankConverter();
		
		Map<String, String> docs = new CorpusReader().readXMLString(xml2);
		StringBuffer buffer = converter.parseString(docs.get(0),  TreebankConverter.ENGLISH, 2);
		//NP*np , VP*vbz . NP*nnp VP*vbd . NP*dt VP*vbz .;
		assertEquals(message, "NP , VP . NP VP . NP VP .", buffer.toString().trim());
		//assertEquals(message, "NP , VP . NP VP . NP VP .", buffer.toString().trim());
	}
	
	public void testTreebankExtraction5(){
		//NP , PP , VP .  
		StringBuffer buffer = converter.parseString(string4,  TreebankConverter.ENGLISH, 2);
		assertEquals(message, "NP , PP , VP .", buffer.toString().trim());
	}
	
	public void testTreebankExtraction6(){
		//ADVP , SBAR , NP VP . 
		//Head for (S (ADVP (RB However)) (, ,) (SBAR (IN if) (S (NP (PRP we)) (VP (VBP distinguish) (PP (IN between) (NP (NP (NP (DT the) (NNS industries)) (SBAR (WHNP (WDT that)) (S (VP (VBP produce) (NP (NN information) (CC and) (NNS communications) (NNS technologies))))) (PRN (-LRB- -LRB-) (NP (NN ICT)) (-RRB- -RRB-))) (CC and) (NP (NP (DT those)) (SBAR (WHNP (WDT that)) (S (VP (VBP are) (ADVP (RB simply)) (NP (NP (NNS users)) (PP (IN of) (NP (JJ such) (NNS technologies))))))))))))) (, ,) (NP (PRP we)) (VP (MD can) (VP (VB see) (SBAR (IN that) (S (NP (DT the) (NN productivity) (NN growth) (NN gap)) (VP (VBZ stems) (ADVP (RB almost) (RB entirely)) (PP (IN from) (S (NP (NP (DT the) (NN weakness)) (PP (IN of) (NP (NP (NNP Europe) (POS 's)) (NNP ICT)))) (VP (VBG producing) (NP (NN sector)))))))))) (. .)) 
		//is (VP (MD can) (VP (VB see) (SBAR (IN that) (S (NP (DT the) (NN productivity) (NN growth) (NN gap)) (VP (VBZ stems) (ADVP (RB almost) (RB entirely)) (PP (IN from) (S (NP (NP (DT the) (NN weakness)) (PP (IN of) (NP (NP (NNP Europe) (POS 's)) (NNP ICT)))) (VP (VBG producing) (NP (NN sector))))))))))
		StringBuffer buffer = converter.parseString(string5,  TreebankConverter.ENGLISH, 2);
		assertEquals(message, "ADVP , SBAR , NP VP .", buffer.toString().trim());
	}
	
	public void testTreebankExtraction7(){
		//RB PP , NP VP . 
		StringBuffer buffer = converter.parseString(string7,  TreebankConverter.ENGLISH, 2);
		assertEquals(message, "RB PP , NP VP .", buffer.toString().trim());
	}
	
	public void testTreebankExtraction8(){
		//SBAR , NP VP . 
		StringBuffer buffer = converter.parseString(string6,  TreebankConverter.ENGLISH, 2);
		assertEquals(message, "SBAR , NP VP .", buffer.toString().trim());
	}
	
	/**
	 * Tests whether the sentence pairs are being correctly totalled.
	 */
	public void testPairs(){
		
		List<Triplet<String, String, Integer>> pairs = converter.parseStringAndExtractProductions(string2,  TreebankConverter.ENGLISH, 2);
		//assertEquals(message, " NP NP . NP VP . NP VP .", buffer.toString());
		
		//map contents: [(VP,.)=1, ( ,NP)=1, (NP,NP)=1, (NP,.)=1, (NP,VP)=1]
		String production1 = new String("NP VP .");
		String production2 = new String("NP VP .");
		//List<Production> productions = new ArrayList<Production>();
		//productions.add(production1);
		//productions.add(production2);
		Triplet<String, String, Integer> t = new Triplet<String, String, Integer>(production1, production2, new Integer(2));
		
 		assertNotNull(message, pairs.contains(t));
		
		
		//assertNotNull(message, pairs.get(new Production("NP NP .", "NP VP .")));
	}
	
	/**
	 * Tests whether the frequencies of sentence pairs are being correctly computed.
	 */
	public void testFrequencyCounts(){
		List<Triplet<String, String, Integer>> pairs = converter.parseStringAndExtractProductions(string2,  TreebankConverter.ENGLISH, 2);
		//assertEquals(message, " NP NP . NP VP . NP VP .", buffer.toString());
		//Production production1 = new Production("NP", "NP", " .");
		//Production production2 = new Production("NP"," VP"," .");
		//Triplet<Production, Production, Integer> t = new Triplet<Production, Production, Integer>(production1, production2, new Integer(1));
		//Triplet<Production, Production, Integer> t2 = new Triplet<Production, Production, Integer>(production2, production2, new Integer(1));
		Map<String, Integer> frequencies = converter.getProductionCounts();
		
		assertEquals(message, 1, frequencies.get("NP NP .").intValue());
		assertEquals(message, 2, frequencies.get("NP VP .").intValue());
	}
	/**
	 * Tests whether the frequencies of sentence pairs are being correctly computed.
	 */
	public void testProductionCounts(){
		List<Triplet<String, String, Integer>> pairs = converter.parseStringAndExtractProductions(string2,  TreebankConverter.ENGLISH, 2);
		//assertEquals(message, " NP NP . NP VP . NP VP .", buffer.toString());
		String production1 = new String("NP NP .");
		String production2 = new String("NP VP .");
		//Triplet<Production, Production, Integer> t = new Triplet<Production, Production, Integer>(production1, production2, new Integer(1));
		//Triplet<Production, Production, Integer> t2 = new Triplet<Production, Production, Integer>(production2, production2, new Integer(1));
		int firstTest = 0;
		int secondTest = 0;
		for(Triplet<String, String, Integer> production: pairs){
			if(production.getValue0().equals(production2) && production.getValue1().equals(production2)){
				
				firstTest =production.getValue2().intValue();
			}
			if(production.getValue0().equals(production1) && production.getValue1().equals(production2)){
				secondTest = production.getValue2().intValue();
			}
		}
		
		assertEquals(message, 1, firstTest );
		assertEquals(message, 1, secondTest);
	}

	/**
	 * Tests whether the frequencies of sentence pairs are being correctly computed.
	 */
	public void testProductionCounts2(){
		List<Triplet<String, String, Integer>> pairs = converter.parseStringAndExtractProductions(fourSentences,  TreebankConverter.ENGLISH, 2);
		Map< String, Integer> counts = converter.getProductionCounts();
		//String production1 = new String("NP NP .");
		String production = new String("NP VP .");
		//{NP*np VP*vbz=1, NP*prp VP*vbp=1, NP*jj VP*vbd=2}
		assertEquals(message, 4, counts.get(production).intValue());
 		
	}
	
	/**
	 * Tests whether the frequencies of sentence pairs are being correctly computed.
	 */
	public void testProductionPairs(){
		List<Triplet<String, String, Integer>> pairs = converter.parseStringAndExtractProductions(fourSentences,  TreebankConverter.ENGLISH, 2);
		//Map< String, Integer> counts = converter.getProductionFrequencies();
		String production1 = new String("");
		String production2 = new String("NP VP .");
		
		int firstTest = 0;
		int secondTest = 0;
		for(Triplet<String, String, Integer> production: pairs){
			if(production.getValue0().equals(production2) && production.getValue1().equals(production2)){
				
				firstTest =production.getValue2().intValue();
			}
			if(production.getValue0().equals(production1) && production.getValue1().equals(production2)){
				secondTest = production.getValue2().intValue();
			}
		}
		
		
		assertEquals(message, 3, firstTest);
		assertEquals(message, 1, secondTest);
		
		assertNotNull(message, converter.computeFrequencies());
	}
	
	public void testProductions1(){
		converter = new TreebankConverter(TreebankConverter.PRODUCTIONS_TYPE);
		List<Triplet<String, String, Integer>> pairs = converter.parseStringAndExtractProductions(testProductions1,  TreebankConverter.ENGLISH, 2);
		String production1 = new String("NP->DT CD NNS VP->VBD SBAR .");
		//String production3 = new String("NP-> NP NP-ADV");
		Map< String, Integer> counts = converter.getProductionCounts();
		assertEquals(message, 1, counts.get(production1).intValue());
	}

	public void testProductions2(){
		converter = new TreebankConverter(TreebankConverter.PRODUCTIONS_TYPE);
		List<Triplet<String, String, Integer>> pairs = converter.parseStringAndExtractProductions(testProductions2,  TreebankConverter.ENGLISH, 2);
		String production1 = new String("NP->NNP NNP VP->VP CC VP .");
		//String production3 = new String("NP-> NP NP-ADV");
		Map< String, Integer> counts = converter.getProductionCounts();
		assertEquals(message, 1, counts.get(production1).intValue());
	}

}
