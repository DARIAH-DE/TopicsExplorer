const fs = require('fs');
const path = require('path');
const XRegExp = require('xregexp');
const snowball = require('node-snowball');

class topicModelling {
  constructor(settings, sentences, dict) {
    this.settings = settings || {};
    
    if (dict) {
      this.dict = dict;
    }
    if (!isNaN(this.settings.numberTopics) && this.settings.numberTopics > 0) {
      this.numTopics = this.settings.numberTopics;
    } else {
      this.numTopics = 10;
    }

    this.documentTopicSmoothing = 0.1;
    this.topicWordSmoothing = 0.01;
    this.docSortSmoothing = 10.0;
    this.sumDocSortSmoothing = this.docSortSmoothing * this.numTopics;

    this.completeSweeps = 0;
    this.reqiestedSweeps = 0;

    // vocabulary
    this.vocabularySize = 0;
    this.vocabularyCounts = {};

    if (this.settings.stem !== undefined) {
      this.stem = this.settings.stem;
    }

    if (this.settings.displayingStopWords !== undefined) {
      this.displayingStopwords = settings.displayingStopWords;
    }

    //documents
    this.documents = [];
    this.wordTopicCounts = {};
    this.topicWordCounts = [];
    this.topicScores = this.zeros(this.numTopics);
    this.tokensPerTopic = this.zeros(this.numTopics);
    this.topicWeights = this.zeros(this.numTopics);

    this.loadVocabulary();
    this.prepareData(sentences);
    if (this.settings.sweeps !== undefined) {
      this.requestedSweeps = this.settings.sweeps;
    } else {
      this.requestedSweeps = 500;
    }
    while (this.completeSweeps <= this.requestedSweeps) {
      this.sweep();
    }
  }

  loadVocabulary() {
    let stopwordsFileName = `./languages/${this.settings.language}/stopwords_${this.settings.language}.json`;
    try {
      // eslint-disable-next-line
      this.stopwords = JSON.parse(
        fs.readFileSync(path.resolve(__dirname, stopwordsFileName))
      );
    } catch (ex) {
      this.stopwords = {};
    }
    if (this.dict !== undefined) {
      this.addStopWords();
    }
  }

  prepareData(documents) {
    if (!documents || documents.length < 0) {
      return;
    }
    let wordPattern = XRegExp('\\p{L}[\\p{L}\\p{P}]*\\p{L}', 'g');
    for (let item of documents) {
      if (item.text == '') {
        continue;
      }
      let sentence = Array.isArray(item.text)
        ? item.text
        : item.text.toLowerCase().match(wordPattern);
      let docID = item.id;
      let tokens = [];
      let topicCounts = this.zeros(this.numTopics);
      if (sentence == null) {
        continue;
      }
      sentence.forEach(word => {
        if (word !== '') {
          let topic = Math.floor(Math.random() * this.numTopics);

          if (word.length <= 2) {
            this.stopwords[word] = 1;
          }

          let isStopword = this.stopwords[word];

          if (this.stem && !isStopword) {
            word = snowball.stemword(word, this.settings.language);
            isStopword = this.stopwords[word];
          }
          if (isStopword) {
            // Record counts for stopwords, but nothing else
            if (!this.vocabularyCounts[word]) {
              this.vocabularyCounts[word] = 1;
            } else {
              this.vocabularyCounts[word] += 1;
            }
          } else {
            this.tokensPerTopic[topic]++;
            if (!this.wordTopicCounts[word]) {
              this.wordTopicCounts[word] = {};
              this.vocabularySize++;
              this.vocabularyCounts[word] = 0;
            }
            if (!this.wordTopicCounts[word][topic]) {
              this.wordTopicCounts[word][topic] = 0;
            }
            this.wordTopicCounts[word][topic] += 1;
            this.vocabularyCounts[word] += 1;
            topicCounts[topic] += 1;
          }
          tokens.push({ word: word, topic: topic, isStopword: isStopword });
        }
      });
      this.documents.push({
        originalOrder: documents.length,
        id: docID,
        originalText: item.text,
        tokens: tokens,
        topicCounts: topicCounts
      });
    }
  }

  sweep() {
    let topicNormalizers = this.zeros(this.numTopics);
    for (let topic = 0; topic < this.numTopics; topic++) {
      topicNormalizers[topic] =
        1.0 /
        (this.vocabularySize * this.topicWordSmoothing +
          this.tokensPerTopic[topic]);
    }

    for (let doc = 0; doc < this.documents.length; doc++) {
      let currentDoc = this.documents[doc];
      let docTopicCounts = currentDoc.topicCounts;

      for (let position = 0; position < currentDoc.tokens.length; position++) {
        let token = currentDoc.tokens[position];
        if (token.isStopword) {
          continue;
        }

        this.tokensPerTopic[token.topic]--;
        let currentWordTopicCounts = this.wordTopicCounts[token.word];
        currentWordTopicCounts[token.topic]--;
        if (currentWordTopicCounts[token.topic] == 0) {
          //delete(currentWordTopicCounts[ token.topic ]);
        }
        docTopicCounts[token.topic]--;
        topicNormalizers[token.topic] =
          1.0 /
          (this.vocabularySize * this.topicWordSmoothing +
            this.tokensPerTopic[token.topic]);

        let sum = 0.0;
        for (let topic = 0; topic < this.numTopics; topic++) {
          if (currentWordTopicCounts[topic]) {
            this.topicWeights[topic] =
              (this.documentTopicSmoothing + docTopicCounts[topic]) *
              (this.topicWordSmoothing + currentWordTopicCounts[topic]) *
              topicNormalizers[topic];
          } else {
            this.topicWeights[topic] =
              (this.documentTopicSmoothing + docTopicCounts[topic]) *
              this.topicWordSmoothing *
              topicNormalizers[topic];
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
        docTopicCounts[token.topic]++;

        topicNormalizers[token.topic] =
          1.0 /
          (this.vocabularySize * this.topicWordSmoothing +
            this.tokensPerTopic[token.topic]);
      }
    }

    //console.log("sweep in " + (Date.now() - startTime) + " ms");
    this.completeSweeps += 1;
    if (this.completeSweeps >= this.requestedSweeps) {
      this.sortTopicWords();
    }
  }

  byCountDescending(a, b) {
    return b.count - a.count;
  }

  topNWords(wordCounts, n) {
    return wordCounts
      .slice(0, n)
      .map(d => {
        return d.word;
      })
      .join(' ');
  }

  sortTopicWords() {
    this.topicWordCounts = [];
    for (let topic = 0; topic < this.numTopics; topic++) {
      this.topicWordCounts[topic] = [];
    }

    for (let word in this.wordTopicCounts) {
      for (let topic in this.wordTopicCounts[word]) {
        this.topicWordCounts[topic].push({
          word: word,
          count: this.wordTopicCounts[word][topic]
        });
      }
    }

    for (let topic = 0; topic < this.numTopics; topic++) {
      this.topicWordCounts[topic].sort(this.byCountDescending);
    }
  }

  getTopicWords() {
    let topicTopWords = [];
    for (let topic = 0; topic < this.numTopics; topic++) {
      topicTopWords.push(this.topNWords(this.topicWordCounts[topic], 10));
    }
    this.calcDominantTopic();

    let topicData = topicTopWords.map((words, index) => {
      return { id: index, topicText: words, score: this.topicScores[index] };
    });
    return topicData;
  }

  calcDominantTopic() {
    this.documents.map((doc, i) => {
      let topic = -1;
      let score = -1;
      for (
        let selectedTopic = 0;
        selectedTopic < this.numTopics;
        selectedTopic++
      ) {
        let tempScore =
          (doc.topicCounts[selectedTopic] + this.docSortSmoothing) /
          (doc.tokens.length + this.sumDocSortSmoothing);
        if (tempScore >= score) {
          score = tempScore;
          topic = selectedTopic;
        }
      }
      this.topicScores[topic] += 1;
    });
    this.topicScores = this.topicScores.map(val => val / this.documents.length);
  }

  getDocuments() {
    let sentences = [];

    for (
      let selectedTopic = 0;
      selectedTopic < this.numTopics;
      selectedTopic++
    ) {
      let documentVocab = this.getVocab(selectedTopic, true);
      let scores = this.documents.map((doc, i) => {
        return {
          docID: i,
          score:
            (doc.topicCounts[selectedTopic] + this.docSortSmoothing) /
            (doc.tokens.length + this.sumDocSortSmoothing)
        };
      });
      scores.sort((a, b) => {
        return b.score - a.score;
      });
      let docinfo = [];
      for (let val of scores) {
        if (this.documents[val.docID].topicCounts[selectedTopic] > 0) {
          docinfo.push({
            id: this.documents[val.docID].id,
            text: this.documents[val.docID].originalText,
            score: val.score
          });
        }
      }
      sentences.push({
        topic: selectedTopic,
        documents: docinfo,
        documentVocab
      });
    }
    return sentences;
  }
  //
  // Vocabulary
  //

  mostFrequentWords(includeStops, sortByTopic, selectedTopic) {
    // Convert the random-access map to a list of word:count pairs that
    //  we can then sort.
    let wordCounts = [];

    if (sortByTopic) {
      for (let word in this.vocabularyCounts) {
        if (
          this.wordTopicCounts[word] &&
          this.wordTopicCounts[word][selectedTopic]
        ) {
          wordCounts.push({
            word: word,
            count: this.wordTopicCounts[word][selectedTopic]
          });
        }
      }
    } else {
      for (let word in this.vocabularyCounts) {
        if (includeStops || !this.stopwords[word]) {
          wordCounts.push({ word: word, count: this.vocabularyCounts[word] });
        }
      }
    }

    wordCounts.sort(this.byCountDescending);
    return wordCounts;
  }

  entropy(counts) {
    counts = counts.filter(function(x) {
      return x > 0.0;
    });
    let sum = this.sum(counts);
    return (
      Math.log(sum) - (1.0 / sum) * this.sum(counts.map(x => x * Math.log(x)))
    );
  }

  specificity(word) {
    if (this.wordTopicCounts[word] == undefined) {
      return 0;
    }
    return (
      1.0 -
      this.entropy(Object.values(this.wordTopicCounts[word])) /
        Math.log(this.numTopics)
    );
  }

  getVocab(selectedTopic, sortVocabByTopic) {
    let vocab = [];
    let wordFrequencies = this.mostFrequentWords(
      this.displayingStopwords,
      sortVocabByTopic,
      selectedTopic
    ).slice(0, 499);
    wordFrequencies.forEach(d => {
      let isStopword = this.stopwords[d.word];
      let score = this.specificity(d.word);
      vocab.push({
        word: d.word,
        count: d.count,
        stopword: isStopword,
        specificity: score
      });
    });
    return vocab;
  }

  truncate(s) {
    return s.length > 300 ? s.substring(0, 299) + '...' : s;
  }

  zeros(n) {
    var x = new Array(n);
    for (var i = 0; i < n; i++) {
      x[i] = 0.0;
    }
    return x;
  }

  sum(arr) {
    return arr.reduce((sum, currentValue) => {
      return sum + currentValue;
    });
  }
z
}
