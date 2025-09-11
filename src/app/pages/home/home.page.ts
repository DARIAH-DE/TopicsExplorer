import { Component, computed, inject } from '@angular/core';
import { Router } from '@angular/router';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { faFileArrowUp } from '@fortawesome/free-solid-svg-icons';
import { CorpusComponent } from '../../components/corpus/corpus.component';
import { HyperparametersComponent } from '../../components/hyperparameters/hyperparameters.component';
import { CorpusService } from '../../services/corpus.service';
import { HyperparametersService } from '../../services/hyperparameters.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.page.html',
  styleUrl: './home.page.css',
  imports: [FaIconComponent, CorpusComponent, HyperparametersComponent],
})
export class HomePage {
  readonly #documentService = inject(CorpusService);
  readonly #router = inject(Router);
  readonly #hyperparametersService = inject(HyperparametersService);

  public readonly faFileArrowUp = faFileArrowUp;

  public readonly numDocuments = this.#documentService.numDocuments;
  public readonly numTopics = this.#hyperparametersService.numTopics;
  public readonly numIterations = this.#hyperparametersService.numIterations;
  public readonly alpha = this.#hyperparametersService.alpha;
  public readonly beta = this.#hyperparametersService.beta;

  public readonly isReady = computed(() => {
    const hasDocuments = this.#documentService.hasDocuments();
    const hasValidHyperparameters = this.#hyperparametersService.hasValidHyperparameters();
    return hasDocuments && hasValidHyperparameters;
  });

  public async trainModel(): Promise<void> {
    this.#router.navigate(['/training']);
  }
}
