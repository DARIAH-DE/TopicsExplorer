import { computed, Injectable, signal } from '@angular/core';
import { invoke } from '@tauri-apps/api/core';
import { listen, UnlistenFn } from '@tauri-apps/api/event';
import { LdaHyperparameters, LdaProgress, LdaResult, TextDocument, Topic } from '../core/core.models';

@Injectable({ providedIn: 'root' })
export class LdaService {
  public readonly isTraining = signal(false);

  public readonly hasModel = computed(() => {
    const theta = this.theta();
    const phi = this.phi();
    const topics = this.topics();
    return theta.length > 0 && phi.length > 0 && topics.length > 0;
  });

  public readonly theta = signal<number[][]>([]);
  public readonly phi = signal<number[][]>([]);
  public readonly topics = signal<Topic[]>([]);
  public readonly perplexity = signal<number | null>(null);

  public readonly currentIteration = signal(0);
  public readonly currentPerplexity = signal(0);

  /**
   * Trains an LDA model using the provided documents and parameters.
   */
  public async trainModel(docs: TextDocument[], params: LdaHyperparameters): Promise<void> {
    this.isTraining.set(true);

    const unlisten = await this.registerListener();

    try {
      const { theta, phi, topics, perplexity } = await invoke<LdaResult>('train_model', { docs, params });

      this.theta.set(theta);
      this.phi.set(phi);
      this.topics.set(topics);
      this.perplexity.set(perplexity);
    } finally {
      this.isTraining.set(false);
      unlisten();
    }
  }

  private async registerListener(): Promise<UnlistenFn> {
    return await listen<LdaProgress>('lda:progress', ({ payload }) => {
      this.currentIteration.set(payload.iteration);
      this.currentPerplexity.set(payload.perplexity);
    });
  }
}
