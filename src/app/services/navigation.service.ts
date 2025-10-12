import { computed, inject, Injectable, signal } from '@angular/core';
import { Router } from '@angular/router';

export enum Page {
  HOME = 'HOME',
  TRAINING = 'TRAINING',
  TOPIC = 'TOPIC',
  TOPICS = 'TOPICS',
  DOCUMENT_TOPIC = 'DOCUMENT_TOPIC',
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
  readonly isDocumentTopic = computed(() => this.currentPage() === Page.DOCUMENT_TOPIC);
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

  public async navigateDocumentTopic(): Promise<void> {
    await this.#router.navigate(['/document-topic']);
    this.currentPage.set(Page.DOCUMENT_TOPIC);
  }

  public async navigateExport(): Promise<void> {
    await this.#router.navigate(['/export']);
    this.currentPage.set(Page.EXPORT);
  }
}
