/**
 * Represents a text document.
 */
export interface TextDocument {
  /**
   * Name of the document.
   */
  name: string;

  /**
   * Text content of the document.
   */
  text: string;

  /**
   * List of tokens extracted from the document.
   */
  tokens: string[];
}

/**
 * Represents the features extracted from a corpus of text documents.
 */
export interface Features {
  /**
   * Ordered list of unique words in the corpus.
   */
  vocabulary: string[];

  /**
   * Mapping of document names to word counts.
   */
  documents: Map<string, Map<number, number>>;
}
