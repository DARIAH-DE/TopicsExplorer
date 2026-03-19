import { Component, computed, inject, OnInit, signal, ChangeDetectionStrategy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { NgxChartsModule } from '@swimlane/ngx-charts';
import { Topic, WordProb } from '../../core/core.models';
import { CorpusService } from '../../services/corpus.service';
import { LdaService } from '../../services/lda.service';
import { ThemeService } from '../../services/theme.service';

interface DocumentScore {
  name: string;
  index: number;
  probability: number;
}

@Component({
  selector: 'app-topic',
  templateUrl: './topic.page.html',
  styleUrl: './topic.page.css',
  imports: [NgxChartsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TopicPage implements OnInit {
  readonly #route = inject(ActivatedRoute);
  readonly #ldaService = inject(LdaService);
  readonly #corpusService = inject(CorpusService);
  readonly #themeService = inject(ThemeService);

  public readonly topicIndex = signal<number>(0);
  public readonly color = computed(() => (this.#themeService.isDarkTheme() ? '#ffffff' : '#000000'));

  public readonly topic = computed<Topic | undefined>(() => {
    const topics = this.#ldaService.topics();
    const index = this.topicIndex();
    return topics.find((t) => t.topicIndex === index);
  });

  public readonly topWords = computed<WordProb[]>(() => {
    const topic = this.topic();
    return topic ? topic.topWords : [];
  });

  public readonly wordChartData = computed(() => {
    return this.topWords()
      .slice(0, 20)
      .map(({ word, prob }) => ({
        name: word,
        value: prob,
      }));
  });

  public readonly wordCloud = computed(() => {
    const words = this.topWords().slice(0, 30);
    if (words.length === 0) return [] as { word: string; size: number }[];

    const probs = words.map((w) => w.prob);
    const min = Math.min(...probs);
    const max = Math.max(...probs);
    const range = max - min || 1;

    return words.map(({ word, prob }) => {
      const normalized = (prob - min) / range;
      const size = 14 + normalized * 18; // 14px to 32px
      return { word, size };
    });
  });

  public readonly topDocuments = computed<DocumentScore[]>(() => {
    const theta = this.#ldaService.theta();
    const topicIdx = this.topicIndex();

    if (theta.length === 0) return [];

    return theta
      .map((docTopics, docIndex) => ({
        name: this.#corpusService.getDocumentName(docIndex),
        index: docIndex,
        probability: docTopics[topicIdx] ?? 0,
      }))
      .sort((a, b) => b.probability - a.probability)
      .slice(0, 10);
  });

  public readonly documentChartData = computed(() => {
    return this.topDocuments().map(({ name, probability }) => ({
      name,
      value: probability,
    }));
  });

  public ngOnInit(): void {
    const idParam = this.#route.snapshot.paramMap.get('id');
    if (idParam) {
      this.topicIndex.set(parseInt(idParam, 10));
    }
  }

  public formatPercent(value: number): string {
    return `${(value * 100).toFixed(2)}%`;
  }
}
