import { Component, computed, ElementRef, inject, viewChild, ChangeDetectionStrategy } from '@angular/core';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { faDownload, faFileCode, faFileCsv, faTable } from '@fortawesome/free-solid-svg-icons';
import { CorpusService } from '../../services/corpus.service';
import { LdaService } from '../../services/lda.service';
import { ToastService } from '../../services/toast.service';

@Component({
  selector: 'app-export',
  templateUrl: './export.page.html',
  styleUrl: './export.page.css',
  imports: [FaIconComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExportPage {
  readonly #ldaService = inject(LdaService);
  readonly #corpusService = inject(CorpusService);
  readonly #toastService = inject(ToastService);

  public readonly fileInput = viewChild<ElementRef<HTMLInputElement>>('fileInput');

  public readonly faDownload = faDownload;
  public readonly faFileCode = faFileCode;
  public readonly faFileCsv = faFileCsv;
  public readonly faTable = faTable;

  public readonly topics = this.#ldaService.topics;
  public readonly theta = this.#ldaService.theta;
  public readonly phi = this.#ldaService.phi;
  public readonly perplexity = this.#ldaService.perplexity;
  public readonly numTopics = this.#ldaService.numTopics;
  public readonly numIterations = this.#ldaService.numIterations;
  public readonly alpha = this.#ldaService.alpha;
  public readonly beta = this.#ldaService.beta;

  public readonly hasModel = this.#ldaService.hasModel;

  public readonly summary = computed(() => ({
    numDocuments: this.#corpusService.numDocuments(),
    numTopics: this.numTopics(),
    numIterations: this.numIterations(),
    alpha: this.alpha(),
    beta: this.beta(),
    perplexity: this.perplexity(),
  }));

  /**
   * Exports topics with their top words as JSON.
   */
  public exportTopicsJson(): void {
    const data = {
      topics: this.topics().map((topic) => ({
        topicIndex: topic.topicIndex,
        dominanceScore: topic.dominanceScore,
        topWords: topic.topWords,
      })),
    };
    this.downloadFile(JSON.stringify(data, null, 2), 'topics.json', 'application/json');
    this.#toastService.showInfoToast('Topics exported as JSON');
  }

  /**
   * Exports topics with their top words as CSV.
   */
  public exportTopicsCsv(): void {
    const headers = ['Topic Index', 'Dominance Score', 'Word', 'Probability'];
    const rows = this.topics().flatMap((topic) =>
      topic.topWords.map((wp) => [topic.topicIndex, topic.dominanceScore, wp.word, wp.prob].join(',')),
    );
    const csv = [headers.join(','), ...rows].join('\n');
    this.downloadFile(csv, 'topics.csv', 'text/csv');
    this.#toastService.showInfoToast('Topics exported as CSV');
  }

  /**
   * Exports the document-topic distribution (theta) as JSON.
   */
  public exportThetaJson(): void {
    const data = {
      documentTopicDistribution: this.theta().map((docTopics, docIndex) => ({
        documentIndex: docIndex,
        documentName: this.#corpusService.getDocumentName(docIndex),
        topicProbabilities: docTopics,
      })),
    };
    this.downloadFile(JSON.stringify(data, null, 2), 'document-topic-distribution.json', 'application/json');
    this.#toastService.showInfoToast('Document-Topic distribution exported as JSON');
  }

  /**
   * Exports the document-topic distribution (theta) as CSV.
   */
  public exportThetaCsv(): void {
    const numTopics = this.theta()[0]?.length ?? 0;
    const topicHeaders = Array.from({ length: numTopics }, (_, i) => `Topic ${i + 1}`);
    const headers = ['Document Index', 'Document Name', ...topicHeaders];

    const rows = this.theta().map((docTopics, docIndex) => {
      const docName = this.#corpusService.getDocumentName(docIndex);
      return [docIndex, `"${docName}"`, ...docTopics.map((p) => p.toFixed(6))].join(',');
    });

    const csv = [headers.join(','), ...rows].join('\n');
    this.downloadFile(csv, 'document-topic-distribution.csv', 'text/csv');
    this.#toastService.showInfoToast('Document-Topic distribution exported as CSV');
  }

  /**
   * Exports the topic-word distribution (phi) as JSON.
   */
  public exportPhiJson(): void {
    const data = {
      topicWordDistribution: this.phi().map((topicWords, topicIndex) => ({
        topicIndex,
        wordProbabilities: topicWords,
      })),
    };
    this.downloadFile(JSON.stringify(data, null, 2), 'topic-word-distribution.json', 'application/json');
    this.#toastService.showInfoToast('Topic-Word distribution exported as JSON');
  }

  /**
   * Exports the complete model including hyperparameters and all distributions.
   */
  public exportFullModel(): void {
    const data = {
      hyperparameters: {
        numTopics: this.numTopics(),
        numIterations: this.numIterations(),
        alpha: this.alpha(),
        beta: this.beta(),
      },
      metrics: {
        perplexity: this.perplexity(),
      },
      topics: this.topics(),
      documentTopicDistribution: this.theta(),
      topicWordDistribution: this.phi(),
      documents: this.#corpusService.textDocuments().map((doc, i) => ({
        index: i,
        name: this.#corpusService.getDocumentName(i),
      })),
    };
    this.downloadFile(JSON.stringify(data, null, 2), 'lda-model.json', 'application/json');
    this.#toastService.showInfoToast('Full model exported as JSON');
  }

  /**
   * Downloads content as a file.
   */
  private downloadFile(content: string, filename: string, mimeType: string): void {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  public triggerImport(): void {
    this.fileInput()?.nativeElement.click();
  }

    /**
     * Handles file input change to import a model.
     */
    public async onImportModel(event: Event): Promise<void> {
      const input = event.target as HTMLInputElement;
      const file = input.files?.[0];
      if (!file) return;

      await this.#ldaService.importModel(file);
      input.value = '';
    }
}
