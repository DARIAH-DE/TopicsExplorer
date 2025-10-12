import { computed, Injectable, signal } from '@angular/core';
import { TextDocument } from '../core/core.models';

@Injectable({ providedIn: 'root' })
export class CorpusService {
  public readonly textDocuments = signal<TextDocument[]>([]);
  public readonly numDocuments = computed(() => this.textDocuments().length);
  public readonly hasDocuments = computed(() => this.numDocuments() > 0);

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
}
