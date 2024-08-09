import { TextCorpus, Topic } from './interfaces.shared';
import { getZeroVector } from './utils.shared';

interface TopicModelOptions {
  numTopics?: number;
  docTopicSmoothing?: number;
  topicWordSmoothing?: number;
  docSortSmoothing?: number;
  sumDocSortSmoothing?: number;
}

export class TopicModel {
  public numTopics: number;
  public docTopicSmoothing: number;
  public topicWordSmoothing: number;
  public docSortSmoothing: number;
  public sumDocSortSmoothing: number;
  public vocabSize: number;
  public tokensPerTopic: number[];
  public textCorpus: TextCorpus;
  public topicWordCounts: any;
  public wordTopicCounts: any;
  public vocabCounts: any;
  public topicWeights: number[]
  public topicScores: any;
  public numIterations: number = 100;

  constructor(textCorpus: TextCorpus, options: TopicModelOptions) {
    this.numTopics = options.numTopics || 10;
    this.docTopicSmoothing = options.docTopicSmoothing || 0.1;
    this.topicWordSmoothing = options.topicWordSmoothing || 0.01;
    this.docSortSmoothing = options.docSortSmoothing || 10.0;
    this.sumDocSortSmoothing = this.docSortSmoothing * this.numTopics;

    this.textCorpus = textCorpus;
    this.tokensPerTopic = getZeroVector(this.numTopics);
    this.vocabSize = this.textCorpus.vocabSize;
    this.vocabCounts = {};

    this.topicWeights = getZeroVector(this.numTopics);
    this.topicScores = getZeroVector(this.numTopics);

    this.topicWordCounts = [];
    this.wordTopicCounts = {};

    for (const textDocument of this.textCorpus.textDocuments) {
      textDocument.topicCounts = getZeroVector(this.numTopics);
      for (const token of textDocument.tokens) {
        token.topic = this.getRandomTopic();

        this.tokensPerTopic[token.topic]++;
        if (!this.wordTopicCounts[token.text]) {
          this.wordTopicCounts[token.text] = {};
        }
        if (!this.wordTopicCounts[token.text][token.topic]) {
          this.wordTopicCounts[token.text][token.topic] = 0;
        }
        this.wordTopicCounts[token.text][token.topic] += 1;
        textDocument.topicCounts[token.topic] += 1;
      }
    }
  }

  /**
   * Gets a random topic.
   */
  private getRandomTopic(): number {
    return Math.floor(Math.random() * this.numTopics);
  }

  /**
   * Gets the normalizer for the topic distribution.
   */
  private getTopicNormalizer(): number[] {
    const topicNormalizer = getZeroVector(this.numTopics);

    for (let i = 0; i < this.numTopics; i++) {
      topicNormalizer[i] = 1.0 / (this.vocabSize * this.topicWordSmoothing + this.tokensPerTopic[i]);
    }

    return topicNormalizer;
  }

  private sortTopicWords(): void {
    this.topicWordCounts = [];
    for (let topic = 0; topic < this.numTopics; topic++) {
      this.topicWordCounts[topic] = [];
    }

    for (let word in this.wordTopicCounts) {
      for (let topic in this.wordTopicCounts[word]) {
        this.topicWordCounts[topic].push({
          word: word,
          count: this.wordTopicCounts[word][topic],
        });
      }
    }

    for (let topic = 0; topic < this.numTopics; topic++) {
      this.topicWordCounts[topic].sort((a: { count: number; }, b: { count: number; }) => b.count - a.count);
    }
  }

  public update(): void {
    const topicNormalizer = this.getTopicNormalizer();

    for (const textDocument of this.textCorpus.textDocuments) {
      for (const token of textDocument.tokens) {
        if (!token.topic || !textDocument.topicCounts) {
          // TODO
          continue;
        }

        this.tokensPerTopic[token.topic]--;
        let currentWordTopicCounts = this.wordTopicCounts[token.text];
        currentWordTopicCounts[token.topic]--;
        textDocument.topicCounts[token.topic]--;
        topicNormalizer[token.topic] = 1.0 / (this.vocabSize * this.topicWordSmoothing + this.tokensPerTopic[token.topic]);

        let sum = 0.0;
        for (let topic = 0; topic < this.numTopics; topic++) {
          if (currentWordTopicCounts[topic]) {
            this.topicWeights[topic] =
              (this.docTopicSmoothing + textDocument.topicCounts[topic]) *
              (this.topicWordSmoothing + currentWordTopicCounts[topic]) *
              topicNormalizer[topic];
          } else {
            this.topicWeights[topic] =
              (this.docTopicSmoothing + textDocument.topicCounts[topic]) * this.topicWordSmoothing * topicNormalizer[topic];
          }
          sum += this.topicWeights[topic];
        }

        // Sample from an unnormalized discrete distribution
        let sample = sum * Math.random();
        let i = 0;
        sample -= this.topicWeights[i];
        while (sample > 0.0) {
          i++;
          sample -= this.topicWeights[i];
        }
        token.topic = i;

        this.tokensPerTopic[token.topic]++;
        if (!currentWordTopicCounts[token.topic]) {
          currentWordTopicCounts[token.topic] = 1;
        } else {
          currentWordTopicCounts[token.topic] += 1;
        }
        textDocument.topicCounts[token.topic]++;

        topicNormalizer[token.topic] =
          1.0 / (this.vocabSize * this.topicWordSmoothing + this.tokensPerTopic[token.topic]);
      }
    }

    this.sortTopicWords();
  }

  topNWords(wordCounts: any, n: any) {
    return wordCounts
      .slice(0, n)
      .map((d: { word: any; }) => {
        return d.word;
      })
      .join(' ');
  }

  public getTopics(): Topic[] {
    const topics = [];

    for (const topic of this.topicWordCounts) {
      topics.push(topic.slice(0, 1_000));
    }




    this.calcDominantTopic();

    let topicData = topicTopWords.map((words, index) => {
      return { id: index, topicText: words, score: this.topicScores[index] };
    });
    return topicData;
  }

  calcDominantTopic() {
    this.textCorpus.textDocuments.map((doc, i) => {
      let topic = -1;
      let score = -1;
      for (
        let selectedTopic = 0;
        selectedTopic < this.numTopics;
        selectedTopic++
      ) {
        let tempScore =
          (doc.topicCounts![selectedTopic] + this.docSortSmoothing) /
          (doc.tokens.length + this.sumDocSortSmoothing);
        if (tempScore >= score) {
          score = tempScore;
          topic = selectedTopic;
        }
      }
      this.topicScores[topic] += 1;
    });
    this.topicScores = this.topicScores.map((val: number) => val / this.textCorpus.textDocuments.length);
  }
}
