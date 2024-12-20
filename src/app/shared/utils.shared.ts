import { TextDocument, Token } from './interfaces.shared';
import { STOPWORDS } from './stopwords.shared';
import { BagOfWords } from './types.shared';

/**
 * Splits a text into tokens.
 */
export function tokenizeText(text: string): string[] {
  return text.match(/\p{L}+\p{P}?\p{L}+/ug) || [];
}

/**
 * Gets the tokens from a text.
 */
export function getTokens(text: string): Token[] {
  return tokenizeText(text.toLocaleLowerCase()).map((token) => ({ text: token }));
}


/**
 * Gets the most common words in a vocabulary.
 */
export function getMostCommonWords(counts: Map<string, number>, n: number = 10): Set<string> {
  return new Set(
    Array.from(counts.keys())
      .sort((a, b) => counts.get(b)! - counts.get(a)!)
      .slice(0, n),
  );
}

/**
 * Extracts the vocabulary (a map from token to ID) from a corpus of text documents.
 *
 * @note Also filters out stopwords, the 10 most common words, single character tokens and hapax legomena.
 */
export function getVocabulary(counts: Map<string, number>): string[] {
  const vocabulary = new Set<string>();
  const mostCommonWords = getMostCommonWords(counts);
  for (const [token, count] of counts.entries()) {
    // To be included in the vocabulary, a token must:
    // - occur more than once,
    // - have more than one character,
    // - not be a stopword, and
    // - not be one of the most common words
    if (count > 1 && token.length > 1 && !STOPWORDS.has(token) && !mostCommonWords.has(token)) {
      vocabulary.add(token);
    }
  }

  return Array.from(vocabulary);
}

export function getZeroVector(n: number): number[] {
  var x = new Array(n);
  for (var i = 0; i < n; i++) {
    x[i] = 0.0;
  }
  return x;
}

export function getEntropy(counts: number[]): number {
  counts = counts.filter(function (x) {
    return x > 0.0;
  });
  let sum = sumValues(counts);
  return Math.log(sum) - (1.0 / sum) * sumValues(counts.map((x) => x * Math.log(x)));
}

export function getSpecificity(word: string, wordTopicCounts: any, numTopics: any): number {
  if (wordTopicCounts[word] == undefined) {
    return 0;
  }
  return 1.0 - getEntropy(Object.values(wordTopicCounts[word])) / Math.log(numTopics);
}

export function sumValues(values: number[]): number {
  return values.reduce((sum, currentValue) => {
    return sum + currentValue;
  });
}
