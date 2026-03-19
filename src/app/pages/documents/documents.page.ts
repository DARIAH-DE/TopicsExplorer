import { Component, computed, inject, signal, ChangeDetectionStrategy } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { faFile, faSearch, faSortAmountDown, faSortAmountUp } from '@fortawesome/free-solid-svg-icons';
import { CorpusService } from '../../services/corpus.service';
import { LdaService } from '../../services/lda.service';
import { NavigationService } from '../../services/navigation.service';

interface DocumentSummary {
  index: number;
  name: string;
  dominantTopicIndex: number;
  dominantTopicLabel: string;
  dominantTopicProb: number;
  textPreview: string;
}

type SortField = 'name' | 'dominantTopic' | 'probability';
type SortDirection = 'asc' | 'desc';

@Component({
  selector: 'app-documents',
  templateUrl: './documents.page.html',
  styleUrl: './documents.page.css',
  imports: [FaIconComponent, FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DocumentsPage {
  readonly #corpusService = inject(CorpusService);
  readonly #ldaService = inject(LdaService);
  readonly #navigationService = inject(NavigationService);

  public readonly faFile = faFile;
  public readonly faSearch = faSearch;
  public readonly faSortAmountDown = faSortAmountDown;
  public readonly faSortAmountUp = faSortAmountUp;

  public readonly searchQuery = signal('');
  public readonly sortField = signal<SortField>('name');
  public readonly sortDirection = signal<SortDirection>('asc');
  public readonly selectedTopicFilter = signal<number | null>(null);

  public readonly topics = this.#ldaService.topics;
  public readonly hasModel = this.#ldaService.hasModel;

  public readonly documents = computed<DocumentSummary[]>(() => {
    const textDocs = this.#corpusService.textDocuments();
    const theta = this.#ldaService.theta();

    if (theta.length === 0) {
      return textDocs.map((doc, index) => ({
        index,
        name: this.#corpusService.getDocumentName(index),
        dominantTopicIndex: -1,
        dominantTopicLabel: 'N/A',
        dominantTopicProb: 0,
        textPreview: doc.text.slice(0, 200) + (doc.text.length > 200 ? '...' : ''),
      }));
    }

    return textDocs.map((doc, index) => {
      const topicProbs = theta[index];
      const dominantTopicIndex = topicProbs.indexOf(Math.max(...topicProbs));
      return {
        index,
        name: this.#corpusService.getDocumentName(index),
        dominantTopicIndex,
        dominantTopicLabel: this.#ldaService.getTopicLabel(dominantTopicIndex, 3),
        dominantTopicProb: topicProbs[dominantTopicIndex],
        textPreview: doc.text.slice(0, 200) + (doc.text.length > 200 ? '...' : ''),
      };
    });
  });

  public readonly filteredDocuments = computed(() => {
    let docs = this.documents();
    const query = this.searchQuery().toLowerCase();
    const topicFilter = this.selectedTopicFilter();

    // Filter by search query
    if (query) {
      docs = docs.filter(
        (doc) => doc.name.toLowerCase().includes(query) || doc.textPreview.toLowerCase().includes(query),
      );
    }

    // Filter by topic
    if (topicFilter !== null) {
      docs = docs.filter((doc) => doc.dominantTopicIndex === topicFilter);
    }

    // Sort
    const field = this.sortField();
    const direction = this.sortDirection();
    const multiplier = direction === 'asc' ? 1 : -1;

    docs = [...docs].sort((a, b) => {
      switch (field) {
        case 'name':
          return multiplier * a.name.localeCompare(b.name);
        case 'dominantTopic':
          return multiplier * (a.dominantTopicIndex - b.dominantTopicIndex);
        case 'probability':
          return multiplier * (a.dominantTopicProb - b.dominantTopicProb);
        default:
          return 0;
      }
    });

    return docs;
  });

  public toggleSort(field: SortField): void {
    if (this.sortField() === field) {
      this.sortDirection.set(this.sortDirection() === 'asc' ? 'desc' : 'asc');
    } else {
      this.sortField.set(field);
      this.sortDirection.set('asc');
    }
  }

  public clearFilters(): void {
    this.searchQuery.set('');
    this.selectedTopicFilter.set(null);
  }

  public viewDocument(index: number): void {
    this.#navigationService.navigateDocument(index);
  }

  public formatPercent(value: number): string {
    return `${(value * 100).toFixed(1)}%`;
  }
}
