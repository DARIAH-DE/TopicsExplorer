import { Component, inject, signal, ChangeDetectionStrategy } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { faAngleDown, faAngleUp, faFlask } from '@fortawesome/free-solid-svg-icons';
import { LdaService } from '../../services/lda.service';

@Component({
  selector: 'app-hyperparameters',
  templateUrl: './hyperparameters.component.html',
  styleUrl: './hyperparameters.component.css',
  imports: [FaIconComponent, FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HyperparametersComponent {
  readonly #ldaService = inject(LdaService);

  public readonly isCollapsed = signal(true);

  public readonly faFlask = faFlask;
  public readonly faAngleUp = faAngleUp;
  public readonly faAngleDown = faAngleDown;

  public readonly numTopics = this.#ldaService.numTopics;
  public readonly numIterations = this.#ldaService.numIterations;
  public readonly alpha = this.#ldaService.alpha;
  public readonly beta = this.#ldaService.beta;

  public toggleCard(): void {
    this.isCollapsed.set(!this.isCollapsed());
  }
}
