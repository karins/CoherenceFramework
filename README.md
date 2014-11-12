EntityFramework
===============

Entity-based coherence: code for entity grid experiment and entity graph experiment
Both are multilingual. 

Entity grids are constructed by identifying the discourse entities in the documents
under consideration, and constructing a 2D grids whereby each column corresponds to the entity,
i.e. noun, being tracked, and each row represents a particular sentence in the document. Once all occurrences of nouns 
and the syntactic roles they represent in each sentence (Subject (S), Object (O), or other (X)) are extracted, 
an entity transition is deﬁned as a consecutive occurrence of an entity, with given syntactic roles. These are computed 
by examining the grid vertically for each entity. 

Entity graphs project the entity grid into a graph format, using a bipartite graph. They
 capture the same entity transition information as the entity grid experiment, although they
only track the occurrance of entities, avoiding the nulls of the other, and additionally can track
cross-sentenial references. The graph tracks the presence of all entities, taking all nouns in the document as discourse
entities,and connections to the sentences they occur in. 
The coherence of a text in this model is measured by calculating the average outdegree
of a projection, summing the shared edges (ie of entities leaving a sentence) between 2 sentences.
