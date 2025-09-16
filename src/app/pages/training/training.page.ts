import { Component, computed, inject, signal, effect } from '@angular/core';
import { LdaService } from '../../services/lda.service';
import { NgxChartsModule } from '@swimlane/ngx-charts';

@Component({
  selector: 'app-training',
  templateUrl: './training.page.html',
  styleUrl: './training.page.css',
  imports: [NgxChartsModule]
})
export class TrainingPage {
  readonly #ldaService = inject(LdaService);

  results: any = [
    {
      name: 'Series',
      series: [],
    },
  ]

  yAxisLabel = signal('Perplexity');
  xAxisLabel = signal('Iteration')
  xScaleMax = this.#ldaService.numIterations;

  xAxisTickFormatting = (val: number) => (val % 10 === 0 ? String(val) : '');

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
        value: this.currentPerplexity()
      });

      this.results[0].series = [...this.results[0].series];
      this.results = [...this.results];
    });
  }
}
