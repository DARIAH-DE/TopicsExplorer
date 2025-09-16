import { Component, computed, inject } from '@angular/core';
import { Router } from '@angular/router';
import { faFileArrowUp } from '@fortawesome/free-solid-svg-icons';
import { CorpusComponent } from '../../components/corpus/corpus.component';
import { HyperparametersComponent } from '../../components/hyperparameters/hyperparameters.component';
import { CorpusService } from '../../services/corpus.service';
import { LdaService } from '../../services/lda.service';
import { NavigationService } from '../../services/navigation.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.page.html',
  styleUrl: './home.page.css',
  imports: [CorpusComponent, HyperparametersComponent],
})
export class HomePage {
  readonly #documentService = inject(CorpusService);
  readonly #navigationService = inject(NavigationService);
  readonly #ldaService = inject(LdaService);

  public readonly faFileArrowUp = faFileArrowUp;

  public readonly numDocuments = this.#documentService.numDocuments;
  public readonly numTopics = this.#ldaService.numTopics;
  public readonly numIterations = this.#ldaService.numIterations;
  public readonly alpha = this.#ldaService.alpha;
  public readonly beta = this.#ldaService.beta;

  public readonly isReady = computed(() => {
    const hasDocuments = this.#documentService.hasDocuments();
    const hasValidHyperparameters = this.#ldaService.hasValidHyperparameters();
    return hasDocuments && hasValidHyperparameters;
  });

  public async trainModel(): Promise<void> {
    const textDocuments = this.#documentService.textDocuments();

    this.#ldaService.trainModel(textDocuments);

    this.#navigationService.navigateTraining();
  }
}
