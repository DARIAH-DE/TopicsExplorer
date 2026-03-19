import { DecimalPipe } from '@angular/common';
import { Component, computed, inject, signal, ChangeDetectionStrategy } from '@angular/core';
import { NgxChartsModule, Series } from '@swimlane/ngx-charts';
import { LdaService } from '../../services/lda.service';
import { ThemeService } from '../../services/theme.service';

@Component({
  selector: 'app-training',
  templateUrl: './training.page.html',
  styleUrl: './training.page.css',
  imports: [NgxChartsModule, DecimalPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TrainingPage {
  readonly #ldaService = inject(LdaService);
  readonly #themeService = inject(ThemeService);

  public readonly results = computed<Series[]>(() => [{ name: '', series: this.#ldaService.perplexityOverTime() }]);
  public readonly hasResults = computed(() => this.results().some((result) => result.series.length > 1));

  public readonly yAxisLabel = signal('Perplexity');
  public readonly xAxisLabel = signal('Iteration');
  public readonly color = computed(() => (this.#themeService.isDarkTheme() ? '#ffffff' : '#000000'));
  public readonly numIterations = this.#ldaService.numIterations;

  public readonly isTraining = this.#ldaService.isTraining;
  public readonly currentIteration = this.#ldaService.currentIteration;
  public readonly currentPerplexity = this.#ldaService.currentPerplexity;
  public readonly hasModel = this.#ldaService.hasModel;

  public readonly progress = computed(() => {
    const current = this.currentIteration();
    const total = this.numIterations();
    return total > 0 ? current / total : 0;
  });

  public readonly progressPercent = computed(() => Math.round(this.progress() * 100));

  public readonly status = computed(() => {
    if (this.isTraining()) {
      return 'Training in progress...';
    }
    if (this.hasModel()) {
      return 'Training complete!';
    }
    return 'Waiting to start...';
  });
}
