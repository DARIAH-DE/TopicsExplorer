/// <reference lib="webworker" />

import { db } from '../database/storage.database';
import { TopicModelOptions } from '../shared/interfaces.shared';
import { TopicModel } from '../shared/topic-model.shared';

addEventListener('message', onTrainTopicModel);

/**
 * Trains a topic model using the given text corpus and options.
 *
 * @param message The message containing the text corpus and options.
 */
export async function onTrainTopicModel(message: MessageEvent<{ options: TopicModelOptions }>): Promise<void> {
  const [textDocuments, vocabulary] = await Promise.all([db.getTextDocuments(), db.getVocabulary()]);

  if (!textDocuments || vocabulary.length === 0) {
    return;
  }

  const model = new TopicModel()
  model.setCorpus(textDocuments, vocabulary);
  model.setHyperparameters(message.data.options.numTopics, message.data.options.alpha, message.data.options.beta);

  for (let i = 0; i < message.data.options.numIterations; i++) {
    model.update();

    await db.saveModel(model);

    postMessage({ currentIteration: i + 1, isFinished: false });
  }

  postMessage({ currentIteration: message.data.options.numIterations, isFinished: true });
}
