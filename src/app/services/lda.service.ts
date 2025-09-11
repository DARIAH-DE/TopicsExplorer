import { Injectable, signal } from '@angular/core';
import { invoke } from '@tauri-apps/api/core';
import { LdaHyperparameters, LdaResult, TextDocument, Topic } from '../core/core.models';

@Injectable({ providedIn: 'root' })
export class LdaService {
  public readonly isTraining = signal(false);

  public readonly theta = signal<number[][]>([]);
  public readonly phi = signal<number[][]>([]);
  public readonly topics = signal<Topic[]>([]);
  public readonly perplexity = signal<number | null>(null);

  /**
   * Trains an LDA model using the provided documents and parameters.
   */
  public async trainModel(docs: TextDocument[], params: LdaHyperparameters): Promise<void> {
    this.isTraining.set(true);

    try {
      const { theta, phi, topics, perplexity } = await invoke<LdaResult>('train_model', { docs, params });

      this.theta.set(theta);
      this.phi.set(phi);
      this.topics.set(topics);
      this.perplexity.set(perplexity);
    } finally {
      this.isTraining.set(false);
    }
  }
}
