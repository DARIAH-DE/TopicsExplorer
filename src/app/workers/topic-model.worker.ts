/// <reference lib="webworker" />

import { TextCorpus, TopicModelOptions, WorkerMessage } from '../shared/interfaces.shared';
import { TopicModel } from '../shared/topic-model.shared';

addEventListener('message', (message: MessageEvent<{ textCorpus: TextCorpus; options: TopicModelOptions }>) => {
  const model = new TopicModel(message.data.textCorpus, message.data.options);

  console.error("START TRAINING")

  for (let i = 0; i < message.data.options.numIterations; i++) {
    console.error(i)
    model.update();
    postMessage({ currentIteration: i + 1 });
  }

  postMessage({ currentIteration: message.data.options.numIterations, model });
});
