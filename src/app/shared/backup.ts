import { TextDocument, Topic, TopicModelOptions, TopicWord } from './interfaces.shared';

interface Hyperparameters {
  numTopics: number;
  alpha: number;
  beta: number;
}

interface Corpus {
  textDocuments: TextDocument[];
  numDocuments: number;
  vocab: string[];
  vocabSize: number;
  word2Id: Map<string, number>;
}

export interface Counts {
  docTopicCounts: number[][];
  topicWordCounts: number[][];
  topicCounts: number[];
  docLengths: number[];
  topicAssignments: number[][];
}



export class TopicModel implements Hyperparameters, Corpus, Counts {
  public numTopics: number = 0;
  public numIterations: number = 0;
  public alpha: number = 0;
  public beta: number = 0;

  public textDocuments: TextDocument[] = [];
  public numDocuments: number = 0;
  public vocab: string[] = [];
  public vocabSize: number = 0;
  public word2Id: Map<string, number> = new Map();

  public docTopicCounts: number[][] = []; // docTopicCounts[docId][topicId]
  public topicWordCounts: number[][] = []; // topicWordCounts[topicId][wordId]
  public topicCounts: number[] = []; // total number of words assigned to each topic
  public docLengths: number[] = []; // total number of words in each document
  public topicAssignments: number[][] = []; // topicAssignments[docId][wordPosition]

  public initializeRandomly(textDocuments: TextDocument[], vocab: string[], options: TopicModelOptions) {
    this.numTopics = options.numTopics;
    this.numIterations = options.numIterations;
    this.alpha = options.alpha;
    this.beta = options.beta;

    this.textDocuments = textDocuments;
    this.numDocuments = textDocuments.length;
    this.vocab = vocab;
    this.vocabSize = vocab.length;

    this.word2Id = new Map<string, number>();
    for (let i = 0; i < this.vocab.length; i++) {
      this.word2Id.set(this.vocab[i], i);
    }

    this.docTopicCounts = new Array(this.numDocuments);
    this.topicWordCounts = new Array(options.numTopics);
    this.topicCounts = new Array(options.numTopics).fill(0);
    this.docLengths = new Array(this.numDocuments).fill(0);
    this.topicAssignments = new Array(this.numDocuments);

    for (let d = 0; d < this.numDocuments; d++) {
      this.docTopicCounts[d] = new Array(options.numTopics).fill(0);
      this.topicAssignments[d] = [];
    }

    for (let k = 0; k < options.numTopics; k++) {
      this.topicWordCounts[k] = new Array(this.vocabSize).fill(0);
    }

    // Initialize topic assignments randomly and update counts
    for (let d = 0; d < this.numDocuments; d++) {
      const doc = textDocuments[d];
      const tokens = doc.tokens;
      for (let n = 0; n < tokens.length; n++) {
        const token = tokens[n];
        if (token.isStopword || !this.word2Id.has(token.text)) {
          continue;
        }
        const word = token.text;
        const wordId = this.word2Id.get(word)!;

        // Randomly assign a topic
        const topic = Math.floor(Math.random() * options.numTopics);

        this.topicAssignments[d].push(topic);

        // Update counts
        this.docTopicCounts[d][topic]++;
        this.topicWordCounts[topic][wordId]++;
        this.topicCounts[topic]++;
        this.docLengths[d]++;
      }
    }
  }

  public initializeFromModel(textDocuments: TextDocument[], vocab: string[], options: TopicModelOptions, counts: Counts) {
    this.numTopics = options.numTopics;
    this.numIterations = options.numIterations;
    this.alpha = options.alpha;
    this.beta = options.beta;

    this.textDocuments = textDocuments;
    this.numDocuments = textDocuments.length;
    this.vocab = vocab;
    this.vocabSize = vocab.length;

    this.word2Id = new Map<string, number>();
    for (let i = 0; i < this.vocab.length; i++) {
      this.word2Id.set(this.vocab[i], i);
    }

    this.docTopicCounts = counts.docTopicCounts;
    this.topicWordCounts = counts.topicWordCounts;
    this.topicCounts = counts.topicCounts;
    this.docLengths = counts.docLengths;
    this.topicAssignments = counts.topicAssignments;
  }

  public export(): TopicModelOptions & Counts {
    return {
      numTopics: this.numTopics,
      numIterations: this.numIterations,
      alpha: this.alpha,
      beta: this.beta,
      docTopicCounts: this.docTopicCounts,
      topicWordCounts: this.topicWordCounts,
      topicCounts: this.topicCounts,
      docLengths: this.docLengths,
      topicAssignments: this.topicAssignments,
    };
  }

  public update() {
    for (let d = 0; d < this.numDocuments; d++) {
      const doc = this.textDocuments[d];
      const tokens = doc.tokens;
      const docLength = this.docLengths[d];
      const docTopicCounts = this.docTopicCounts[d];
      const topicAssignments = this.topicAssignments[d];
      let n = 0;
      for (let t = 0; t < tokens.length; t++) {
        const token = tokens[t];
        if (token.isStopword || !this.word2Id.has(token.text)) {
          continue;
        }
        const word = token.text;
        const wordId = this.word2Id.get(word)!;
        const topic = topicAssignments[n];

        // Decrement counts
        docTopicCounts[topic]--;
        this.topicWordCounts[topic][wordId]--;
        this.topicCounts[topic]--;

        // Compute p(k) for each topic k
        const p = new Array(this.numTopics);
        let sumP = 0;
        for (let k = 0; k < this.numTopics; k++) {
          const term1 = (docTopicCounts[k] + this.alpha) / (docLength - 1 + this.numTopics * this.alpha);
          const term2 =
            (this.topicWordCounts[k][wordId] + this.beta) / (this.topicCounts[k] + this.vocabSize * this.beta);
          p[k] = term1 * term2;
          sumP += p[k];
        }

        // Normalize p(k)
        for (let k = 0; k < this.numTopics; k++) {
          p[k] /= sumP;
        }

        // Sample a new topic from p(k)
        const newTopic = this.sampleTopic(p);

        // Increment counts with new topic
        topicAssignments[n] = newTopic;
        docTopicCounts[newTopic]++;
        this.topicWordCounts[newTopic][wordId]++;
        this.topicCounts[newTopic]++;

        n++;
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
    // Should not reach here
    return p.length - 1;
  }

  public getTopics(numWords: number = 10): Topic[] {
    const topics: Topic[] = [];
    const numTopics = this.numTopics;
    const V = this.vocabSize;
    const beta = this.beta;

    for (let k = 0; k < numTopics; k++) {
      const wordWeights: TopicWord[] = [];
      for (let v = 0; v < V; v++) {
        const count = this.topicWordCounts[k][v];
        const weight = (count + beta) / (this.topicCounts[k] + V * beta);
        if (count > 0) {
          const word = this.vocab[v];
          wordWeights.push({
            text: word,
            isStopword: false, // Assume no stopwords in topic words
            weight: weight,
          });
        }
      }

      // Sort words by weight in descending order
      wordWeights.sort((a, b) => b.weight - a.weight);

      const presence = this.topicCounts[k] / this.totalWords();

      topics.push({
        id: k.toString(),
        words: wordWeights.slice(0, numWords),
        presence: presence,
      });
    }

    return topics.sort((a, b) => b.presence - a.presence);
  }

  public getTopicsForDocument(documentId: string): { topicId: number; proportion: number }[] {
    const docIndex = this.textDocuments.findIndex((doc) => doc.id === documentId);
    if (docIndex === -1) {
      throw new Error(`Document with ID ${documentId} not found`);
    }
    const docTopicCounts = this.docTopicCounts[docIndex];
    const total = this.docLengths[docIndex];

    const topicProportions = docTopicCounts.map((count, topicId) => ({
      topicId: topicId,
      proportion: count / total,
    }));

    // Sort by proportion descending
    topicProportions.sort((a, b) => b.proportion - a.proportion);

    return topicProportions;
  }

  public getDocumentsForTopic(topicId: number): { documentId: string; proportion: number }[] {
    if (topicId < 0 || topicId >= this.numTopics) {
      throw new Error(`Invalid topic ID ${topicId}`);
    }
    const documentsForTopic = [];
    for (let d = 0; d < this.numDocuments; d++) {
      const docTopicCounts = this.docTopicCounts[d];
      const total = this.docLengths[d];
      const count = docTopicCounts[topicId];
      const proportion = count / total;
      if (count > 0) {
        documentsForTopic.push({
          documentId: this.textDocuments[d].id,
          proportion: proportion,
        });
      }
    }

    // Sort by proportion descending
    documentsForTopic.sort((a, b) => b.proportion - a.proportion);

    return documentsForTopic;
  }

  private totalWords(): number {
    return this.topicCounts.reduce((sum, count) => sum + count, 0);
  }
}
