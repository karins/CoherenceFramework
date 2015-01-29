package nlp.framework.discourse;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.StringReader;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.TaggedWord;
import edu.stanford.nlp.parser.lexparser.LexicalizedParser;
import edu.stanford.nlp.trees.EnglishGrammaticalRelations;
import edu.stanford.nlp.trees.EnglishGrammaticalStructure;
import edu.stanford.nlp.trees.GrammaticalRelation;
import edu.stanford.nlp.trees.GrammaticalStructure;
import edu.stanford.nlp.trees.GrammaticalStructureFactory;
import edu.stanford.nlp.trees.PennTreeReader;
import edu.stanford.nlp.trees.PennTreebankLanguagePack;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.TreebankLanguagePack;
import edu.stanford.nlp.trees.TypedDependency;
import edu.stanford.nlp.util.CoreMap;

/**
 * Extracts Entity Grids, similar to EntityGridFramework, but this class takes as input preconstructed
 * ptb trees instead of raw text input.
 *  
 * @author Karin Sim
 *
 */
public class EntityGridExtractor extends EntityGridFramework {
	
	static List<String> NOUNS = new ArrayList<String>();
	static{
		NOUNS.add("NNP");
		NOUNS.add("NP");
		NOUNS.add("NNS");
		NOUNS.add("NN");
		NOUNS.add("N");
		NOUNS.add("NE");
		};

	/** csubj,  
		csubjpass, {xsubj}: controlling subject}, 
		subj,  
		nsubj (nominal subject), 
		nsubjpass
	**/
	static List<GrammaticalRelation> SUBJECT = new ArrayList<GrammaticalRelation>();
	static {
		SUBJECT.add(EnglishGrammaticalRelations.NOMINAL_SUBJECT);
		SUBJECT.add(EnglishGrammaticalRelations.NOMINAL_PASSIVE_SUBJECT);
		SUBJECT.add(EnglishGrammaticalRelations.CLAUSAL_PASSIVE_SUBJECT);
		SUBJECT.add(EnglishGrammaticalRelations.CLAUSAL_SUBJECT);
		SUBJECT.add(EnglishGrammaticalRelations.SUBJECT);
		};	
	
	
	/** pobj (object of a preposition) 
		also dobj ( direct object) 
		and iobj ( indirect object )
	**/
	static List<GrammaticalRelation> OBJECT = new ArrayList<GrammaticalRelation>();
	static{ 
		OBJECT.add(EnglishGrammaticalRelations.OBJECT);
		OBJECT.add(EnglishGrammaticalRelations.DIRECT_OBJECT);
		OBJECT.add(EnglishGrammaticalRelations.INDIRECT_OBJECT);
		OBJECT.add(EnglishGrammaticalRelations.PREPOSITIONAL_OBJECT);
		}
	
	
	
	/**
	 * takes any files in given directory, presuming each contains documents comprised of ptb trees. 
	 * These will be new line separated, with docid immediately preceding each one, and starting with a '#'
	 * @param args
	 */
	public static void main(String args[]){
		String directory = args[0];
		String language = args[1];
		
		EntityGridExtractor gridExtractor = new EntityGridExtractor();
		System.out.println("dir = "+directory);
		try {
			gridExtractor.convertPtbsToGrids(directory);
		} catch (FileNotFoundException e) {
			System.out.println("No files in directory:"+directory);
			e.printStackTrace();
		} 
	}
	private void convertPtbsToGrids(String directory) throws FileNotFoundException {
				
		PennTreebankLanguagePack tlp = new PennTreebankLanguagePack();
		GrammaticalStructureFactory gsf = tlp.grammaticalStructureFactory();
		
		File[] files = new File(directory).listFiles();
		if(files == null)throw new FileNotFoundException();
		for (File file : files) {
			if (file.isFile()){
				System.out.println("file = "+directory+File.separator+file.getName());
				
				//get all docs from that file:	
				Map<String, List<Tree>> docs = new CorpusReader().readPtbDataAsDocs(directory+File.separator+file.getName());
				
				for(String docid : docs.keySet()){
					Map<String, ArrayList<Map <Integer, String>>> entities = new HashMap<String, ArrayList<Map <Integer, String>>>();
					System.out.println("doc="+docid);
					
					//read in ptb trees for each sub tree in each doc, 
					List<Tree> treesInDoc = docs.get(docid);
					int idx = 0;
					for(Tree tree: treesInDoc){System.out.println("tree in doc :"+tree);
						
						getDependenciesForNouns(tree, entities, idx, gsf);
						idx++;
					}
					//construct grid
					FileOutputUtils.writeGridToFile(EntityExperiments.getDirectory(directory),
												EntityExperiments.getFilenameWithoutExtensions(file.getName())+"_grids", 
												constructGrid(entities, treesInDoc.size()), true, docid, EntityExperiments.isCompressed(file.getName()));
				}
			}
		}
	}

	/**
	 * for test class purposes
	 * @param tree
	 * @return 
	 * @throws IOException 
	 * 
	 */
	public char[][] convertPtbsStringToGrids(String ptbtree)  {
		PennTreebankLanguagePack tlp = new PennTreebankLanguagePack();
		GrammaticalStructureFactory gsf = tlp.grammaticalStructureFactory();
		Map<String, ArrayList<Map <Integer, String>>> entities = new HashMap<String, ArrayList<Map <Integer, String>>>();
		PennTreeReader treeReader = new PennTreeReader(new StringReader(ptbtree));
		try{
			Tree tree = treeReader.readTree();
			getDependenciesForNouns(tree, entities, 0, gsf);
		}catch(IOException e) {
			e.printStackTrace();
			System.exit(1);
			return null;
		}
		finally{
			try {  treeReader.close();  }  catch (Exception e) { /* log it ?*/ }
		}
		
		return constructGrid(entities, 1);
	}

	
	
	private void getDependenciesForNouns(Tree tree, Map<String, ArrayList<Map <Integer, String>>> entities, int idx, GrammaticalStructureFactory gsf ) {
			
		//only get dependencies for the nouns..
		List <TaggedWord> words = tree.taggedYield();
		for(TaggedWord word: words){
			if(NOUNS.contains(word.tag())){
				
				//EnglishGrammaticalStructure gs = gsf.newGrammaticalStructure(tree);
				GrammaticalStructure gs = gsf.newGrammaticalStructure(tree);
				
				Collection <TypedDependency> tdl = gs.typedDependencies();
						
				for(TypedDependency dependency : tdl){
					
					//find the dependency for the noun in question
					if(word.value().equals(dependency.dep().nodeString())){
						
						if(SUBJECT.contains(dependency.reln())){
							
							System.out.println("tracking "+word.value()+" at "+idx+" as S");
							trackEntity(word.value(), idx, S, entities);
						}else if(OBJECT.contains(dependency.reln())){
							
							System.out.println("tracking "+word.value()+" at "+idx+" as O");
							trackEntity(word.value(), idx, O, entities);
						}else{System.out.println("tracking "+word.value()+" at "+idx+" as X");
						
							trackEntity(word.value(), idx, X, entities);
						}
						break;
					}
				}
			}
		}
	}

}
