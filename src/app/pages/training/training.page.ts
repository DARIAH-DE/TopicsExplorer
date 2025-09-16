import { Component, effect, inject, signal } from '@angular/core';
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

  public results: Series[] = [
    {
      name: 'Progress',
      series: [],
    },
  ];

  public readonly yAxisLabel = signal('Perplexity');
  public readonly xAxisLabel = signal('Iteration');
  public readonly xScaleMax = this.#ldaService.numIterations;

  public readonly numIterations = this.#ldaService.numIterations;
  public readonly currentIteration = this.#ldaService.currentIteration;
  public readonly currentPerplexity = this.#ldaService.currentPerplexity;

  constructor() {
    effect(() => {
      if (this.currentPerplexity() === 0) {
        return;
      }

      this.results[0].series.push({
        name: this.currentIteration(),
        value: this.currentPerplexity(),
      });

      this.results = [...this.results];
    });
  }

  public xAxisTickFormatting(value: number): string {
    return value % 10 === 0 ? String(value) : '';
  }
}
