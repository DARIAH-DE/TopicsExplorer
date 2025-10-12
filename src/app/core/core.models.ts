export interface TextDocument {
  name: string;
  text: string;
}

export interface LdaHyperparameters {
  numTopics: number;
  numIterations: number;
  alpha: number;
  beta: number;
}

export interface LdaResult {
  theta: number[][];
  phi: number[][];
  topics: Topic[];
  vocab: string[];
  stopwords: string[];
  totalTokens: number;
  logLikelihood: number;
  perplexity: number;
}

export interface WordProb {
  word: string;
  prob: number;
}

export interface Topic {
  topicIndex: number;
  topWords: WordProb[];
  dominanceScore: number;
}

export interface LdaProgress {
  iteration: number;
  logLikelihood: number;
  perplexity: number;
}
