/**
 * Text document.
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
}

/**
 * Corpus.
 */
export interface Corpus {
  /**
   * Text documents of the corpus.
   */
  textDocuments: TextDocument[];

  /**
   * Vocabulary of the corpus
   */
  vocabulary: string[];
}







































import { TopicModel } from "./topic-model.shared";
import { Maybe } from "./types.shared";

/**
 * Represents a token extracted from a text document.
 */
export interface Token {
  /**
   * The text of the token.
   */
  text: string;

  /**
   * Indicates whether the token is a stopword (and should be ignored).
   */
  isStopword?: boolean;
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

  /**
   * Dirichlet parameter for the document-topic distribution.
   */
  alpha: number;

  /**
   * Dirichlet parameter for the topic-word distribution.
   */
  beta: number;
}

/**
 * Represents a topic.
 */
export interface Topic {
  /**
   * UUID of the topic.
   */
  id: string;

  /**
   * Words and their weights of the topic.
   */
  words: TopicWord[];

  /**
   * Overall presence/dominance of the topic in the corpus.
   */
  presence: number;
}

/**
 * Represents a word in a topic.
 */
export interface TopicWord extends Token {
  /**
   * The weight of the word in the topic.
   */
  weight: number;
}
