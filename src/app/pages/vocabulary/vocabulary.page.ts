import { Component, computed, inject, signal, ChangeDetectionStrategy } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { faSearch } from '@fortawesome/free-solid-svg-icons';
import { NgxChartsModule } from '@swimlane/ngx-charts';
import { LdaService } from '../../services/lda.service';
import { NavigationService } from '../../services/navigation.service';
import { ThemeService } from '../../services/theme.service';

interface WordTopicResult {
  topicIndex: number;
  topicLabel: string;
  probability: number;
  rank: number;
}

@Component({
  selector: 'app-vocabulary',
  templateUrl: './vocabulary.page.html',
  styleUrl: './vocabulary.page.css',
  imports: [FaIconComponent, FormsModule, NgxChartsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class VocabularyPage {
  readonly #ldaService = inject(LdaService);
  readonly #navigationService = inject(NavigationService);
  readonly #themeService = inject(ThemeService);

  public readonly faSearch = faSearch;
  public readonly searchQuery = signal('');
  public readonly color = computed(() => (this.#themeService.isDarkTheme() ? '#ffffff' : '#000000'));

  public readonly hasModel = this.#ldaService.hasModel;
  public readonly topics = this.#ldaService.topics;

  public readonly allWords = computed(() => {
    const topics = this.topics();
    const wordSet = new Set<string>();
    topics.forEach((topic) => {
      topic.topWords.forEach((wp) => wordSet.add(wp.word));
    });
    return Array.from(wordSet).sort();
  });

  public readonly filteredWords = computed(() => {
    const query = this.searchQuery().toLowerCase().trim();
    if (!query) return this.allWords().slice(0, 100);
    return this.allWords().filter((word) => word.toLowerCase().includes(query));
  });

  public readonly selectedWord = signal<string | null>(null);

  public readonly wordTopicDistribution = computed<WordTopicResult[]>(() => {
    const word = this.selectedWord();
    if (!word) return [];

    const topics = this.topics();
    const results: WordTopicResult[] = [];

    topics.forEach((topic) => {
      const wordProb = topic.topWords.find((wp) => wp.word === word);
      if (wordProb) {
        const rank = topic.topWords.findIndex((wp) => wp.word === word) + 1;
        results.push({
          topicIndex: topic.topicIndex,
          topicLabel: this.#ldaService.getTopicLabel(topic.topicIndex, 3),
          probability: wordProb.prob,
          rank,
        });
      }
    });

    return results.sort((a, b) => b.probability - a.probability);
  });

  public readonly chartData = computed(() => {
    return this.wordTopicDistribution().map(({ topicIndex, probability }) => ({
      name: `Topic ${topicIndex + 1}`,
      value: probability,
    }));
  });

  public readonly topWordsPerTopic = computed(() => {
    return this.topics().map((topic) => ({
      topicIndex: topic.topicIndex,
      words: topic.topWords.slice(0, 15),
    }));
  });

  public selectWord(word: string): void {
    this.selectedWord.set(word);
  }

  public clearSelection(): void {
    this.selectedWord.set(null);
  }

  public navigateToTopic(topicIndex: number): void {
    this.#navigationService.navigateTopic(topicIndex);
  }

  public formatPercent(value: number): string {
    return `${(value * 100).toFixed(3)}%`;
  }
}
