import { Component, computed, inject, signal } from '@angular/core';
import { NgxChartsModule, Series } from '@swimlane/ngx-charts';
import { LdaService } from '../../services/lda.service';
import { ThemeService } from '../../services/theme.service';

@Component({
  selector: 'app-training',
  templateUrl: './training.page.html',
  styleUrl: './training.page.css',
  imports: [NgxChartsModule],
})
export class TrainingPage {
  readonly #ldaService = inject(LdaService);
  readonly #themeService = inject(ThemeService);

  public readonly results = computed<Series[]>(() => [{ name: '', series: this.#ldaService.perplexityOverTime() }]);
  public readonly hasResults = computed(() => this.results().some((result) => result.series.length > 1));

  public readonly yAxisLabel = signal('Perplexity');
  public readonly xAxisLabel = signal('Iteration');
  public readonly style = computed(() => `fill: ${this.#themeService.isDarkTheme() ? '#ffffff' : '#000000'};`);
  public readonly numIterations = this.#ldaService.numIterations;
}
