import { Injectable, signal } from '@angular/core';
import { db } from '../database/storage.database';
import { Topic, TopicModelOptions } from '../shared/interfaces.shared';
import { TopicModel } from '../shared/topic-model.shared';
import { Maybe } from '../shared/types.shared';

@Injectable({ providedIn: 'root' })
export class ModelService {
  #model: Maybe<TopicModel>;

  public readonly hasModel = signal(false);
  public readonly isTraining = signal(false);

  public readonly currentIteration = signal(0);

  public readonly numTopics = signal(10);
  public readonly numIterations = signal(1000);
  public readonly alpha = signal(0.1);
  public readonly beta = signal(0.01);

  /**
   * Sets the given model.
   */
  public async setModel(model: TopicModel): Promise<void> {
    await db.saveModel(model);
    this.#model = model;
    this.hasModel.set(true);
  }

  /**
   * Gets the current model.
   */
  public async getModel(): Promise<Maybe<TopicModel>> {
    return await db.getModel();
  }

  public async getTopics(numWords: number = 10): Promise<Topic[]> {
    const model = await this.getModel();
    console.error(model)
    if (model) {
      return model.getTopics(numWords);
    }

    return [];
  }

  /**
   * Resets the current model.
   */
  public async clearModel(): Promise<void> {
    if (this.hasModel()) {
      await db.clearModel();
      this.hasModel.set(false);
    }
  }

  /**
   * Hyperparameter options for the model.
   */
  public getOptions(): TopicModelOptions {
    return { numTopics: this.numTopics(), numIterations: this.numIterations(), alpha: this.alpha(), beta: this.beta() };
  }
}
