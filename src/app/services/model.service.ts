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
    if (!this.#model) {
      this.#model = await db.getModel();
    }

    return this.#model;
  }

  /**
   * Gets the topics from the current model.
   *
   * @param numWords Number of words per topic.
   */
  public async getTopics(numWords: number = 10): Promise<Topic[]> {
    const model = await this.getModel();

    return model?.getTopics(numWords) ?? [];
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

  public startTraining(): void {
    this.isTraining.set(true);
    this.currentIteration.set(0);
  }

  public async finishTraining(): Promise<void> {
    this.isTraining.set(false);
    this.hasModel.set(true);
    this.currentIteration.set(0);

    const model = await db.getModel();
    if (model) {
      await this.setModel(model);
    }
  }

  public setCurrentIteration(iteration: number): void {
    this.currentIteration.set(iteration);
  }
}
