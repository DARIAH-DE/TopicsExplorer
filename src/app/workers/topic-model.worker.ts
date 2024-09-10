/// <reference lib="webworker" />

import { TextCorpus, TopicModelOptions } from '../shared/interfaces.shared';
import { TopicModel } from '../shared/topic-model.shared';

addEventListener('message', onTrainTopicModel);

/**
 * Trains a topic model using the given text corpus and options.
 *
 * @param message The message containing the text corpus and options.
 */
export function onTrainTopicModel(message: MessageEvent<{ textCorpus: TextCorpus; options: TopicModelOptions }>): void {
  const model = new TopicModel(message.data.textCorpus, message.data.options);

  for (let i = 0; i < message.data.options.numIterations; i++) {
    model.update();

    postMessage({ currentIteration: i + 1, topics: model.getTopics(5) });
  }

  postMessage({ currentIteration: message.data.options.numIterations, model });
}
