import { Component, computed, inject, signal } from '@angular/core';
import { NgxChartsModule, Series } from '@swimlane/ngx-charts';
import { LdaService } from '../../services/lda.service';

@Component({
  selector: 'app-training',
  templateUrl: './training.page.html',
  styleUrl: './training.page.css',
  imports: [NgxChartsModule],
})
export class TrainingPage {
  readonly #ldaService = inject(LdaService);

  public results = computed<Series[]>(() => [{ name: 'Progress', series: this.#ldaService.perplexityOverTime() }]);

  public readonly yAxisLabel = signal('Perplexity');
  public readonly xAxisLabel = signal('Iteration');
  public readonly numIterations = this.#ldaService.numIterations;

  public xAxisTickFormatting(value: number): string {
    return value % 10 === 0 ? String(value) : '';
  }
}
