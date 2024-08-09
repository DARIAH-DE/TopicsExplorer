/**
 * Represents a token extracted from a text document.
 */
export interface Token {
  /**
   * The text of the token.
   */
  text: string;

  /**
   * Maybe the assigned topic of the token.
   */
  topic?: number;
}

/**
 * Represents a text document.
 */
export interface TextDocument {
  /**
   * UUID of the text document.
   */
  id: string;

  /**
   * Name of the text document.
   */
  name: string;

  /**
   * Content of the text document.
   */
  text: string;

  /**
   * List of tokens extracted from the document.
   */
  tokens: Token[];

  /**
   * Maybe topic counts for the document.
   */
  topicCounts?: number[];
}

/**
 * Text corpus containing a list of text documents and the vocabulary size.
 */
export interface TextCorpus {
  /**
   * List of text documents.
   */
  textDocuments: TextDocument[];

  /**
   * Number of unique tokens in the corpus.
   */
  vocabSize: number;
}

/**
 * Parameters for the topic model.
 */
export interface TopicModelOptions {
  /**
   * Number of topics.
   */
  numTopics: number;

  /**
   * Number of iterations to run the Gibbs sampler.
   */
  numIterations: number;
}

export interface Topic {
  id: number;
  words: string[];
  weights: number[];
}