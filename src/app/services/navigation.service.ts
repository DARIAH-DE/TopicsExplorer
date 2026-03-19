import { computed, inject, Injectable, signal } from '@angular/core';
import { Router } from '@angular/router';

/**
 * Available pages in the application.
 */
enum Page {
  HOME = 'HOME',
  TRAINING = 'TRAINING',
  TOPIC = 'TOPIC',
  TOPICS = 'TOPICS',
  DOCUMENTS = 'DOCUMENTS',
  DOCUMENT = 'DOCUMENT',
  DOCUMENT_TOPIC = 'DOCUMENT_TOPIC',
  VOCABULARY = 'VOCABULARY',
  EXPORT = 'EXPORT',
}

@Injectable({ providedIn: 'root' })
export class NavigationService {
  readonly #router = inject(Router);

  readonly currentPage = signal(Page.HOME);

  readonly isHome = computed(() => this.currentPage() === Page.HOME);
  readonly isTraining = computed(() => this.currentPage() === Page.TRAINING);
  readonly isTopics = computed(() => this.currentPage() === Page.TOPICS);
  readonly isTopic = computed(() => this.currentPage() === Page.TOPIC);
  readonly isDocuments = computed(() => this.currentPage() === Page.DOCUMENTS);
  readonly isDocument = computed(() => this.currentPage() === Page.DOCUMENT);
  readonly isDocumentTopic = computed(() => this.currentPage() === Page.DOCUMENT_TOPIC);
  readonly isVocabulary = computed(() => this.currentPage() === Page.VOCABULARY);
  readonly isExport = computed(() => this.currentPage() === Page.EXPORT);

  public async navigateHome(): Promise<void> {
    await this.#router.navigate(['/']);
    this.currentPage.set(Page.HOME);
  }

  public async navigateTraining(): Promise<void> {
    await this.#router.navigate(['/training']);
    this.currentPage.set(Page.TRAINING);
  }

  public async navigateTopics(): Promise<void> {
    await this.#router.navigate(['/topics']);
    this.currentPage.set(Page.TOPICS);
  }

  public async navigateTopic(topicIndex: number): Promise<void> {
    await this.#router.navigate([`/topics/${topicIndex}`]);
    this.currentPage.set(Page.TOPIC);
  }

  public async navigateDocuments(): Promise<void> {
    await this.#router.navigate(['/documents']);
    this.currentPage.set(Page.DOCUMENTS);
  }

  public async navigateDocument(documentIndex: number): Promise<void> {
    await this.#router.navigate([`/documents/${documentIndex}`]);
    this.currentPage.set(Page.DOCUMENT);
  }

  public async navigateDocumentTopic(): Promise<void> {
    await this.#router.navigate(['/document-topic']);
    this.currentPage.set(Page.DOCUMENT_TOPIC);
  }

  public async navigateVocabulary(): Promise<void> {
    await this.#router.navigate(['/vocabulary']);
    this.currentPage.set(Page.VOCABULARY);
  }

  public async navigateExport(): Promise<void> {
    await this.#router.navigate(['/export']);
    this.currentPage.set(Page.EXPORT);
  }
}
