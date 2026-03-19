import { Component, computed, inject, OnInit, signal, ChangeDetectionStrategy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { NgxChartsModule } from '@swimlane/ngx-charts';
import { CorpusService } from '../../services/corpus.service';
import { LdaService } from '../../services/lda.service';
import { NavigationService } from '../../services/navigation.service';
import { ThemeService } from '../../services/theme.service';

interface TopicProbability {
  topicIndex: number;
  label: string;
  probability: number;
}

@Component({
  selector: 'app-document',
  templateUrl: './document.page.html',
  styleUrl: './document.page.css',
  imports: [NgxChartsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DocumentPage implements OnInit {
  readonly #route = inject(ActivatedRoute);
  readonly #corpusService = inject(CorpusService);
  readonly #ldaService = inject(LdaService);
  readonly #navigationService = inject(NavigationService);
  readonly #themeService = inject(ThemeService);

  public readonly documentIndex = signal<number>(0);
  public readonly color = computed(() => (this.#themeService.isDarkTheme() ? '#ffffff' : '#000000'));

  public readonly document = computed(() => {
    const docs = this.#corpusService.textDocuments();
    const index = this.documentIndex();
    return docs[index] ?? null;
  });

  public readonly documentName = computed(() => {
    const index = this.documentIndex();
    return this.#corpusService.getDocumentName(index);
  });

  public readonly documentText = computed(() => {
    const doc = this.document();
    return doc?.text ?? '';
  });

  public readonly wordCount = computed(() => {
    const text = this.documentText();
    return text.split(/\s+/).filter((w) => w.length > 0).length;
  });

  public readonly charCount = computed(() => this.documentText().length);

  public readonly hasModel = this.#ldaService.hasModel;

  public readonly topicProbabilities = computed<TopicProbability[]>(() => {
    const theta = this.#ldaService.theta();
    const index = this.documentIndex();

    if (theta.length === 0 || !theta[index]) return [];

    return theta[index]
      .map((prob, topicIndex) => ({
        topicIndex,
        label: this.#ldaService.getTopicLabel(topicIndex, 3),
        probability: prob,
      }))
      .sort((a, b) => b.probability - a.probability);
  });

  public readonly chartData = computed(() => {
    return this.topicProbabilities().map(({ topicIndex, probability }) => ({
      name: `Topic ${topicIndex + 1}`,
      value: probability,
    }));
  });

  public readonly dominantTopic = computed(() => {
    const probs = this.topicProbabilities();
    return probs.length > 0 ? probs[0] : null;
  });

  public ngOnInit(): void {
    const idParam = this.#route.snapshot.paramMap.get('id');
    if (idParam) {
      this.documentIndex.set(parseInt(idParam, 10));
    }
  }

  public navigateToTopic(topicIndex: number): void {
    this.#navigationService.navigateTopic(topicIndex);
  }

  public formatPercent(value: number): string {
    return `${(value * 100).toFixed(2)}%`;
  }
}
