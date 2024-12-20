import { TextDocument, Topic, TopicWord } from './interfaces.shared';


export class TopicModel {
  public numTopics: number = 0;
  public alpha: number = 0;
  public beta: number = 0;

  public textDocuments: TextDocument[] = [];
  public vocabulary: string[] = [];

  public docTopicCounts: number[][] = []; // docTopicCounts[docId][topicId]
  public topicWordCounts: number[][] = []; // topicWordCounts[topicId][wordId]
  public topicCounts: number[] = []; // total number of words assigned to each topic
  public docLengths: number[] = []; // total number of words in each document
  public topicAssignments: number[][] = []; // topicAssignments[docId][wordPosition]

  #numDocuments: number = 0;
  #vocabularySize: number = 0;
  #wordMap: Map<string, number> = new Map();

  /**
   * Sets the hyperparameters for the LDA model.
   */
  public setHyperparameters(numTopics: number, alpha: number, beta: number): void {
    this.numTopics = numTopics;
    this.alpha = alpha;
    this.beta = beta;
  }

  /**
   * Sets the corpus of text documents and the vocabulary.
   */
  public setCorpus(textDocuments: TextDocument[], vocabulary: string[]): void {
    this.textDocuments = textDocuments;
    this.vocabulary = vocabulary;
    this.#numDocuments = textDocuments.length;
    this.#vocabularySize = vocabulary.length;

    this.#wordMap = new Map();
    for (let i = 0; i < this.#vocabularySize; i++) {
      this.#wordMap.set(vocabulary[i], i);
    }
  }

  /**
   * Randomly initializes the topic assignments and counts.
   */
  public initializeValues(): void {
    this.docTopicCounts = new Array(this.#numDocuments);
    this.topicWordCounts = new Array(this.numTopics);
    this.topicCounts = new Array(this.numTopics).fill(0);
    this.docLengths = new Array(this.#numDocuments).fill(0);
    this.topicAssignments = new Array(this.#numDocuments);

    for (let d = 0; d < this.#numDocuments; d++) {
      this.docTopicCounts[d] = new Array(this.numTopics).fill(0);
      this.topicAssignments[d] = [];
    }

    for (let k = 0; k < this.numTopics; k++) {
      this.topicWordCounts[k] = new Array(this.#vocabularySize).fill(0);
    }

    for (let d = 0; d < this.#numDocuments; d++) {
      const doc = this.textDocuments[d];
      for (let n = 0; n < doc.tokens.length; n++) {
        const token = doc.tokens[n];
        if (this.#wordMap.has(token.text)) {
          const word = token.text;
          const wordId = this.#wordMap.get(word)!;

          const topic = Math.floor(Math.random() * this.numTopics);

          this.topicAssignments[d].push(topic);

          this.docTopicCounts[d][topic]++;
          this.topicWordCounts[topic][wordId]++;
          this.topicCounts[topic]++;
          this.docLengths[d]++;
        }
      }
    }
  }

  public update(): void {
    for (let d = 0; d < this.#numDocuments; d++) {
      const doc = this.textDocuments[d];
      const tokens = doc.tokens;
      const docLength = this.docLengths[d];
      const docTopicCounts = this.docTopicCounts[d];
      const topicAssignments = this.topicAssignments[d];

      let n = 0;
      for (let t = 0; t < tokens.length; t++) {
        const token = tokens[t];
        if (this.#wordMap.has(token.text)) {
          const word = token.text;
          const wordId = this.#wordMap.get(word)!;
          const topic = topicAssignments[n];

          docTopicCounts[topic]--;
          this.topicWordCounts[topic][wordId]--;
          this.topicCounts[topic]--;

          const p = new Array(this.numTopics);
          let sumP = 0;
          for (let k = 0; k < this.numTopics; k++) {
            const term1 = (docTopicCounts[k] + this.alpha) / (docLength - 1 + this.numTopics * this.alpha);
            const term2 =
              (this.topicWordCounts[k][wordId] + this.beta) / (this.topicCounts[k] + this.#vocabularySize * this.beta);
            p[k] = term1 * term2;
            sumP += p[k];
          }

          for (let k = 0; k < this.numTopics; k++) {
            p[k] /= sumP;
          }

          const newTopic = this.sampleTopic(p);

          topicAssignments[n] = newTopic;
          docTopicCounts[newTopic]++;
          this.topicWordCounts[newTopic][wordId]++;
          this.topicCounts[newTopic]++;

          n++;
        }
      }
    }
  }

  private sampleTopic(p: number[]): number {
    const cumulative = [];
    let sum = 0;
    for (let i = 0; i < p.length; i++) {
      sum += p[i];
      cumulative.push(sum);
    }
    const r = Math.random();
    for (let i = 0; i < cumulative.length; i++) {
      if (r < cumulative[i]) {
        return i;
      }
    }
    return p.length - 1;
  }

  public getTopics(numWords: number = 100): Topic[] {
    const topics: Topic[] = [];

    for (let k = 0; k < this.numTopics; k++) {
      const wordWeights: TopicWord[] = [];
      for (let v = 0; v < this.#vocabularySize; v++) {
        const count = this.topicWordCounts[k][v];
        const weight = (count + this.beta) / (this.topicCounts[k] + this.#vocabularySize * this.beta);
        if (count > 0) {
          wordWeights.push({
            text: this.vocabulary[v],
            weight,
          });
        }
      }

      wordWeights.sort((a, b) => b.weight - a.weight);

      topics.push({
        id: k.toString(),
        words: wordWeights.slice(0, numWords),
        presence: this.topicCounts[k] / this.totalWords(),
      });
    }

    return topics.sort((a, b) => b.presence - a.presence);
  }

  private totalWords(): number {
    return this.topicCounts.reduce((sum, count) => sum + count, 0);
  }
}
