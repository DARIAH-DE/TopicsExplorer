import Dexie, { Table } from 'dexie';
import { TextDocument, TopicModelOptions } from '../shared/interfaces.shared';
import { TopicModel } from '../shared/topic-model.shared';
import { Maybe } from '../shared/types.shared';

export class Storage extends Dexie {
  textDocuments!: Table<TextDocument, TextDocument['id']>;
  vocabulary!: Table<string>;
  model!: Table<TopicModel>;

  constructor() {
    super('TopicsExplorer');
    this.version(1).stores({ textDocuments: 'id', vocabulary: '++', model: '++' });
  }

  /**
   * Saves text documents to the database.
   */
  public async saveTextDocuments(textDocuments: TextDocument[]): Promise<void> {
    await this.textDocuments.bulkPut(textDocuments);
  }

  /**
   * Saves a text document to the database.
   */
  public async saveTextDocument(textDocument: TextDocument): Promise<void> {
    await this.textDocuments.put(textDocument);
  }

  /**
   * Gets the text documents from the database.
   */
  public async getTextDocuments(): Promise<Maybe<TextDocument[]>> {
    return await this.textDocuments.toArray();
  }

  /**
   * Clears all text documents from the database.
   */
  public async clearTextDocuments(): Promise<void> {
    await this.textDocuments.clear();
  }

  /**
   * Saves the vocabulary to the database.
   */
  public async saveVocabulary(vocabulary: string[]): Promise<void> {
    await this.vocabulary.bulkAdd(vocabulary);
  }

  public async clearVocabulary(): Promise<void> {
    await this.vocabulary.clear();
  }

  /**
   * Gets the vocabulary size from the database.
   */
  public async getVocabSize(): Promise<number> {
    return await this.vocabulary.count();
  }

  public async getVocabulary(): Promise<string[]> {
    return await this.vocabulary.toArray();
  }

  /**
   * Gets a text document from the database.
   */
  public async getTextDocument(id: string): Promise<Maybe<TextDocument>> {
    return await this.textDocuments.get(id);
  }

  /**
   * Saves the topic model to the database.
   */
  public async saveModel(model: TopicModel): Promise<void> {
    await this.model.put(model, 0);
  }

  /**
   * Gets the topic model from the database.
   */
  public async getModel(): Promise<Maybe<TopicModel>> {
    const params = await this.model.get(0);

    console.error(params)

    if (!params) {
      return;
    }

    const model = new TopicModel();
    const textDocuments = await this.getTextDocuments();
    const vocabulary = await this.getVocabulary();
    model.setCorpus(textDocuments!, vocabulary);

    return model;
  }

  public async clearModel(): Promise<void> {
    await this.model.clear();
  }
}

export const db = new Storage();
