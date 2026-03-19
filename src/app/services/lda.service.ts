import { computed, inject, Injectable, signal } from '@angular/core';
import { DataItem } from '@swimlane/ngx-charts';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { LdaHyperparameters, LdaProgress, LdaResult, TextDocument, Topic } from '../core/core.models';
import { NavigationService } from './navigation.service';
import { ToastService } from './toast.service';

@Injectable({ providedIn: 'root' })
export class LdaService {
  readonly #navigationService = inject(NavigationService);
  readonly #toastService = inject(ToastService);

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

    // Reset progress state for a fresh training run
    this.perplexityOverTime.set([]);
    this.currentIteration.set(0);
    this.currentPerplexity.set(0);

    const unlisten = await this.registerListener();

    const params: LdaHyperparameters = {
      numIterations: this.numIterations(),
      numTopics: this.numTopics(),
      alpha: this.alpha(),
      beta: this.beta(),
    };

    try {
      const { theta, phi, topics, perplexity } = (await invoke('train_model', { docs, params })) as LdaResult;

      // Assign in one microtask to batch change detection
      queueMicrotask(() => {
        this.theta.set(theta);
        this.phi.set(phi);
        this.topics.set(topics);
        this.perplexity.set(perplexity);
      });

      this.#navigationService.navigateTopics();
    } finally {
      this.isTraining.set(false);
      unlisten();
    }
  }

  /**
   * Imports a previously exported model from a JSON file.
   */
  public async importModel(file: File): Promise<void> {
    try {
      const text = await file.text();
      const data = JSON.parse(text);

      const hyper = data.hyperparameters as Partial<LdaHyperparameters> | undefined;
      const topics = data.topics as Topic[] | undefined;
      const theta = data.documentTopicDistribution as number[][] | undefined;
      const phi = data.topicWordDistribution as number[][] | undefined;

      if (!hyper || !topics || !theta || !phi) {
        throw new Error('Missing required fields in model file');
      }

      this.numTopics.set(hyper.numTopics ?? topics.length);
      this.numIterations.set(hyper.numIterations ?? this.numIterations());
      this.alpha.set(hyper.alpha ?? this.alpha());
      this.beta.set(hyper.beta ?? this.beta());

      this.topics.set(topics);
      this.theta.set(theta);
      this.phi.set(phi);
      this.perplexity.set((data.metrics?.perplexity as number | undefined) ?? 0);

      this.perplexityOverTime.set([]);
      this.currentIteration.set(this.numIterations());
      this.currentPerplexity.set(this.perplexity());

      await this.#navigationService.navigateTopics();
      this.#toastService.showInfoToast('Model imported successfully');
    } catch (error) {
      console.error(error);
      this.#toastService.showDangerToast('Failed to import model. Please select a valid JSON export.');
    }
  }

  private async registerListener(): Promise<() => void> {
    return await listen('lda:progress', ({ payload }: { payload: LdaProgress }) => {
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
   * Downloads the current model as a JSON file.
   */
  public async downloadModel(): Promise<void> {
    if (!this.hasModel()) {
      return;
    }

    const data = {
      hyperparameters: {
        numTopics: this.numTopics(),
        numIterations: this.numIterations(),
        alpha: this.alpha(),
        beta: this.beta(),
      },
      metrics: {
        perplexity: this.perplexity(),
      },
      topics: this.topics(),
      documentTopicDistribution: this.theta(),
      topicWordDistribution: this.phi(),
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'lda-model.json';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
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
