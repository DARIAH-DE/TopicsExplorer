import { computed, Injectable, signal } from '@angular/core';
import { db } from '../database/storage.database';
import { Corpus, TextDocument } from '../shared/interfaces.shared';
import { Maybe } from '../shared/types.shared';

@Injectable({ providedIn: 'root' })
export class CorpusService {
  public readonly numDocuments = signal(0);
  public readonly vocabSize = signal(0);
  public readonly hasCorpus = computed(() => this.numDocuments() > 0);

  /**
   * Gets the text document with the given ID.
   */
  public async getTextDocument(id: string): Promise<Maybe<TextDocument>> {
    return await db.getTextDocument(id);
  }

  /**
   * Gets all text documents.
   */
  public async getTextDocuments(): Promise<Maybe<TextDocument[]>> {
    return await db.getTextDocuments();
  }

  /**
   * Saves the given text document and increments the number of documents.
   */
  public async saveTextDocument(textDocument: TextDocument): Promise<void> {
    this.numDocuments.update((numDocuments) => numDocuments + 1);
    await db.saveTextDocument(textDocument);
  }

  /**
   * Saves the given vocabulary and sets the vocabulary size.
   */
  public async saveVocabulary(vocabulary: string[]): Promise<void> {
    this.vocabSize.set(vocabulary.length);
    await db.saveVocabulary(vocabulary);
  }

  /**
   * Saves the given corpus.
   */
  public async saveCorpus(corpus: Corpus): Promise<void> {
    await Promise.all([db.saveTextDocuments(corpus.textDocuments), db.saveVocabulary(corpus.vocabulary)]);
  }

  /**
   * Clears the corpus.
   */
  public async clearCorpus(): Promise<void> {
    if (this.hasCorpus()) {
      this.numDocuments.set(0);
      this.vocabSize.set(0);
      await Promise.all([db.clearTextDocuments(), db.clearVocabulary()]);
    }
  }
}
