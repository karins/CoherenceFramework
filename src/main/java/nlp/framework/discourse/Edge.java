package nlp.framework.discourse;

public class Edge {
	private char grammaticalRole;
	private int weight;
	private SentenceNode one;
	private SentenceNode another;
	
	public Edge(SentenceNode one, SentenceNode another){
		this.one = one;
		this.another = another;
	}
	
	public Edge(char grammaticalRole, int weight){
		this.grammaticalRole = grammaticalRole;
		this.weight = weight;
	}
	public char getGrammaticalRole() {
		return grammaticalRole;
	}
	public void setGrammaticalRole(char grammaticalRole) {
		this.grammaticalRole = grammaticalRole;
	}
	public int getWeight() {
		return weight;
	}
	public void setWeight(int weight) {
		this.weight = weight;
	}
}
