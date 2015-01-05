package nlp.framework.discourse;

import java.util.ArrayList;
import java.util.List;

/**
 * Represents an entity in a text. This may be stemmed or a noun phrase.
 * It may also be part of a topic model. 
 * @author Karin Sim
 *
 */
public class Entity{
	
	private List<Integer> sentencesOccurredIn;
	private String entity;
	private int sentenceOccurredIn;
	
	public Entity( String entity, int sentenceOccurredIn) {		
		this.entity = entity;
		this.sentenceOccurredIn = sentenceOccurredIn;
		sentencesOccurredIn = new ArrayList<Integer>();
		sentencesOccurredIn.add( new Integer(sentenceOccurredIn));
	}
	 	
	public String getEntity() {
		return entity;
	}
	public void setEntity(String entity) {
		this.entity = entity;
	}
	public int getSentenceOccurredIn() {
		return sentenceOccurredIn;
	}
	public void setSentenceOccurredIn(int sentenceOccurredIn) {
		this.sentenceOccurredIn = sentenceOccurredIn;
	}
	
	public void addSentenceOccurredIn(int sentenceOccurredIn) {
		this.sentencesOccurredIn.add( new Integer(sentenceOccurredIn));
	}

		
	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + ((entity == null) ? 0 : entity.hashCode());
		result = prime * result + sentenceOccurredIn;
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		Entity other = (Entity) obj;
		if (entity == null) {
			if (other.entity != null)
				return false;
		} else if (!entity.equals(other.entity))
			return false;
		
		return true;
	}
	

}
