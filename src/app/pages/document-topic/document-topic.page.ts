import { Component, computed, inject, signal } from '@angular/core';
import { NgxChartsModule } from '@swimlane/ngx-charts';
import { CorpusService } from '../../services/corpus.service';
import { LdaService } from '../../services/lda.service';
import { ThemeService } from '../../services/theme.service';

@Component({
  selector: 'app-document-topic',
  templateUrl: './document-topic.page.html',
  styleUrl: './document-topic.page.css',
  imports: [NgxChartsModule],
})
export class DocumentTopicPage {
  readonly #corpusService = inject(CorpusService);
  readonly #ldaService = inject(LdaService);
  readonly #themeService = inject(ThemeService);

  public readonly height = computed(() => this.#corpusService.numDocuments() * 50 + 100);
  public readonly color = computed(() => (this.#themeService.isDarkTheme() ? '#ffffff' : '#000000'));
  public readonly xAxisLabel = signal('Topics');
  public readonly yAxisLabel = signal('Probability');

  public readonly results = computed(() => {
    const theta = this.#ldaService.theta();
    const topics = this.#ldaService.topics();

    return topics.map((_, topicIndex) => ({
      name: this.#ldaService.getTopicLabel(topicIndex, 3),
      series: theta.map((docTopics, docIndex) => ({
        name: this.#corpusService.getDocumentName(docIndex),
        value: docTopics[topicIndex],
      })),
    }));
  });
}
