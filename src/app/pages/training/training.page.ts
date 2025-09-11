import { Component, inject, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { NgxChartsModule } from '@swimlane/ngx-charts';
import { CorpusService } from '../../services/corpus.service';
import { HyperparametersService } from '../../services/hyperparameters.service';
import { LdaService } from '../../services/lda.service';

@Component({
  selector: 'app-training',
  templateUrl: './training.page.html',
  styleUrl: './training.page.css',
  imports: [NgxChartsModule],
})
export class TrainingPage implements OnInit {
  readonly #documentService = inject(CorpusService);
  readonly #ldaService = inject(LdaService);
  readonly #router = inject(Router);
  readonly #hyperparametersService = inject(HyperparametersService);

  public readonly currentIteration = this.#ldaService.currentIteration;

  public ngOnInit(): void {
    void this.trainModel();
  }

  public async trainModel(): Promise<void> {
    const textDocuments = this.#documentService.textDocuments();
    const numTopics = this.#hyperparametersService.numTopics();
    const numIterations = this.#hyperparametersService.numIterations();
    const alpha = this.#hyperparametersService.alpha();
    const beta = this.#hyperparametersService.beta();

    await this.#ldaService.trainModel(textDocuments, {
      numTopics,
      numIterations,
      alpha,
      beta,
    });

    this.#router.navigate(['/topics']);
  }
}
