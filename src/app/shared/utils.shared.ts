import { TextDocument } from './interfaces.shared';
import { STOPWORDS } from './stopwords.shared';
import { BagOfWords } from './types.shared';

/**
 * Splits a text into tokens.
 */
export function tokenizeText(text: string): string[] {
  return text.match(/\b\w\w+\b/g) || [];
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
 * @note Also filters out stopwords, single character tokens and hapax legomena.
 */
export function extractVocabulary(corpus: TextDocument[]): Map<string, number> {
  const counts = new Map<string, number>();

  for (const document of corpus) {
    for (const token of document.tokens.filter((token) => token.length > 1 && !STOPWORDS.has(token))) {
      counts.set(token, (counts.get(token) || 0) + 1);
    }
  }

  const mostCommonWords = getMostCommonWords(counts);
  const vocabulary = new Map<string, number>();
  for (const [token, count] of counts.entries()) {
    if (count > 1 && !mostCommonWords.has(token)) {
      vocabulary.set(token, vocabulary.size);
    }
  }

  return vocabulary;
}

/**
 * Gets the bag-of-words representation of a corpus of text documents.
 */
export function getBagOfWords(corpus: TextDocument[], vocabulary: Map<string, number>): BagOfWords[] {
  const bagOfWords: BagOfWords[] = [];

  for (const document of corpus) {
    const counts = new Map<number, number>();
    for (const token of document.tokens) {
      const tokenId = vocabulary.get(token);
      if (tokenId) {
        counts.set(tokenId, (counts.get(tokenId) || 0) + 1);
      }
    }
    bagOfWords.push({ name: document.name, counts });
  }

  return bagOfWords;
}

/**
 * Gets a zero matrix of size m x n.
 */
export function getZeroMatrix(m: number, n: number): Uint32Array[] {
  return Array.from({ length: m }, () => getZeroVector(n));
}

/**
 * Gets a zero vector of size n.
 */
export function getZeroVector(n: number): Uint32Array {
  return new Uint32Array(n);
}
