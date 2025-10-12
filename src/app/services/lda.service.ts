import { computed, inject, Injectable, signal } from '@angular/core';
import { DataItem } from '@swimlane/ngx-charts';
import { invoke } from '@tauri-apps/api/core';
import { listen, UnlistenFn } from '@tauri-apps/api/event';
import { LdaHyperparameters, LdaProgress, LdaResult, TextDocument, Topic } from '../core/core.models';
import { NavigationService } from './navigation.service';

@Injectable({ providedIn: 'root' })
export class LdaService {
  readonly #navigationService = inject(NavigationService);

  public readonly numTopics = signal(10);
  public readonly numIterations = signal(1_000);
  public readonly alpha = signal(0.1);
  public readonly beta = signal(0.01);

  public readonly isTraining = signal(false);

  public readonly perplexityOverTime = signal<DataItem[]>([]);

  public readonly hasValidNumTopics = computed(() => {
    const numTopics = this.numTopics();
    return numTopics > 0 && numTopics <= 1_000;
  });

  public readonly hasValidNumIterations = computed(() => {
    const numIterations = this.numIterations();
    return numIterations > 0 && numIterations <= 100_000;
  });

  public readonly hasValidAlpha = computed(() => {
    const alpha = this.alpha();
    return alpha > 0 && alpha <= 1;
  });

  public readonly hasValidBeta = computed(() => {
    const beta = this.beta();
    return beta > 0 && beta <= 1;
  });

  public readonly hasValidHyperparameters = computed(() => {
    const numTopicsValid = this.hasValidNumTopics();
    const numIterationsValid = this.hasValidNumIterations();
    const alphaValid = this.hasValidAlpha();
    const betaValid = this.hasValidBeta();
    return numTopicsValid && numIterationsValid && alphaValid && betaValid;
  });

  public readonly hasModel = computed(() => {
    const theta = this.theta();
    const phi = this.phi();
    const topics = this.topics();
    return theta.length > 0 && phi.length > 0 && topics.length > 0;
  });

  public readonly theta = signal<number[][]>([]);
  public readonly phi = signal<number[][]>([]);
  public readonly topics = signal<Topic[]>([]);
  public readonly perplexity = signal(0.0);

  public readonly currentIteration = signal(0);
  public readonly currentPerplexity = signal(0);

  /**
   * Trains an LDA model using the provided documents and current parameters.
   */
  public async trainModel(docs: TextDocument[]): Promise<void> {
    this.isTraining.set(true);

    const unlisten = await this.registerListener();

    const params: LdaHyperparameters = {
      numIterations: this.numIterations(),
      numTopics: this.numTopics(),
      alpha: this.alpha(),
      beta: this.beta(),
    };

    try {
      const { theta, phi, topics, perplexity } = await invoke<LdaResult>('train_model', { docs, params });

      this.theta.set(theta);
      this.phi.set(phi);
      this.topics.set(topics);
      this.perplexity.set(perplexity);

      this.#navigationService.navigateTopics();
    } finally {
      this.isTraining.set(false);
      unlisten();
    }
  }

  private async registerListener(): Promise<UnlistenFn> {
    return await listen<LdaProgress>('lda:progress', ({ payload }) => {
      this.currentIteration.set(payload.iteration);
      this.currentPerplexity.set(payload.perplexity);

      if (this.currentPerplexity() !== 0) {
        this.perplexityOverTime.update((previous) => [
          ...previous,
          {
            name: this.currentIteration(),
            value: this.currentPerplexity(),
          },
        ]);
      }
    });
  }

  /**
   * Downloads the current model as a file.
   */
  public async downloadModel(): Promise<void> {
    alert('Not implemented yet');
  }

  /**
   * Gets a label for the specified topic by joining its top words.
   */
  public getTopicLabel(index: number, numWords: number): string {
    return this.topics()
      [index].topWords.slice(0, numWords)
      .map(({ word }) => word)
      .join(' ');
  }
}
