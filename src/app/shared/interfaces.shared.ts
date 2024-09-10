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
   * ID of the topic.
   */
  id: number;

  /**
   * Words and their weights of the topic.
   */
  words: TopicWord[];
}

/**
 * Represents a word in a topic.
 */
export interface TopicWord {
  /**
   * The word.
   */
  text: string;

  /**
   * The weight of the word in the topic.
   */
  weight: number;
}

/**
 * Represents a message sent from the Web Worker.
 */
export interface WorkerMessage {
  /**
   * The current iteration of the Gibbs sampler.
   */
  currentIteration: number;

  /**
   * Maybe the topic model.
   */
  model: Maybe<TopicModel>;

  /**
   * Current topics.
   */
  topics: Topic[];
}
