package nlp.framework.discourse;

import java.util.ArrayList;
import java.util.List;

import edu.stanford.nlp.ling.Label;
import edu.stanford.nlp.ling.StringLabel;

/**
 * Encapsulates a grammatical production, which consists of POS tags and optional punctuation.
 * These are represented as a List<Label> sequence, where <Label> is the label of the tree node.
 * @author Karin
 *
 */
public class Production {
	List<Label> sequence;

	public Production(List<Label> sequence) {
		this.sequence = sequence;
	}
	
	/**
	 * essentially for an empty Production in the pair, for beginning and end of document.
	 */
	public Production(){
		this.sequence = new ArrayList<Label>();
		this.sequence.add(new StringLabel(" "));
	}

	/**
	 * for test classes only
	 * @param string
	 * @param string2
	 */
	public Production(String string, String string2, String string3) {
		this.sequence = new ArrayList<Label>();
		this.sequence.add(new StringLabel(string));
		this.sequence.add(new StringLabel(string2));
		this.sequence.add(new StringLabel(string3));
	}

	
	/*public int hashCode() {
		return new HashCodeBuilder(3, 17).append(this.toString()).toHashCode();
	}*/

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		Production other = (Production) obj;
		if (sequence == null) {
			if (other.sequence != null)
				return false;
		} else if (!sequence.equals(other.sequence))
			return false;
		if(areProductionsEqual(this.sequence, other.getSequence())){
			return true;
		}
		return false;
	}

	private boolean areProductionsEqual(List<Label> sequence,
			List<Label> sequenceToCompare) {
		boolean same = false;
		for(int i = 0; i< sequence.size(); i++){
			
			if(!sequence.get(i).equals(sequenceToCompare.get(i))){
				break;
			}else{
				same = true;
			}			
		}
		return same;
	}

	private List<Label>  getSequence() {
		// TODO Auto-generated method stub
		return this.sequence;
	}
	
	public String toString(){
		StringBuffer sb = new StringBuffer();
		for(Label label : this.sequence){
			sb.append(label);
			sb.append(" ");
		}System.out.println("Production ="+sb.toString());
		return sb.toString();
	}
}
