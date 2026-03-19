import { computed, Injectable, signal } from '@angular/core';
import { TextDocument } from '../core/core.models';

export interface CorpusStatistics {
  totalDocuments: number;
  totalWords: number;
  totalCharacters: number;
  uniqueWords: number;
  avgWordsPerDocument: number;
  minWordsInDocument: number;
  maxWordsInDocument: number;
}

@Injectable({ providedIn: 'root' })
export class CorpusService {
  public readonly textDocuments = signal<TextDocument[]>([]);
  public readonly numDocuments = computed(() => this.textDocuments().length);
  public readonly hasDocuments = computed(() => this.numDocuments() > 0);

  public readonly statistics = computed<CorpusStatistics | null>(() => {
    const docs = this.textDocuments();
    if (docs.length === 0) return null;

    const wordCounts = docs.map((doc) => this.countWords(doc.text));
    const totalWords = wordCounts.reduce((sum, count) => sum + count, 0);
    const totalCharacters = docs.reduce((sum, doc) => sum + doc.text.length, 0);

    // Get unique words
    const allWords = new Set<string>();
    docs.forEach((doc) => {
      const words = doc.text.toLowerCase().match(/\b[a-z]+\b/g) || [];
      words.forEach((word) => allWords.add(word));
    });

    return {
      totalDocuments: docs.length,
      totalWords,
      totalCharacters,
      uniqueWords: allWords.size,
      avgWordsPerDocument: Math.round(totalWords / docs.length),
      minWordsInDocument: Math.min(...wordCounts),
      maxWordsInDocument: Math.max(...wordCounts),
    };
  });

  /**
   * Loads the text content of the provided files and stores them.
   */
  public async loadFiles(fileList: FileList): Promise<void> {
    const files = [...fileList];

    const texts = await Promise.all(files.map((file) => file.text()));
    const textDocuments = files.map((file, index) => ({ name: file.name, text: texts[index] }));

    this.textDocuments.set(textDocuments);
  }

  /**
   * Gets the name of the document at the specified index.
   */
  public getDocumentName(index: number): string {
    const { name } = this.textDocuments()[index];

    // Remove file extension for better readability
    const lastDotIndex = name.lastIndexOf('.');
    return lastDotIndex !== -1 ? name.slice(0, lastDotIndex) : name;
  }

  /**
   * Counts the number of words in a text.
   */
  private countWords(text: string): number {
    return text.split(/\s+/).filter((w) => w.length > 0).length;
  }
}
