import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { faAngleDown, faAngleUp, faFlask } from '@fortawesome/free-solid-svg-icons';
import { HyperparametersService } from '../../services/hyperparameters.service';

@Component({
  selector: 'app-hyperparameters',
  templateUrl: './hyperparameters.component.html',
  styleUrl: './hyperparameters.component.css',
  imports: [FaIconComponent, FormsModule],
})
export class HyperparametersComponent {
  readonly #hyperparametersService = inject(HyperparametersService);

  public readonly isCollapsed = signal(true);

  public readonly faFlask = faFlask;
  public readonly faAngleUp = faAngleUp;
  public readonly faAngleDown = faAngleDown;

  public readonly numTopics = this.#hyperparametersService.numTopics;
  public readonly numIterations = this.#hyperparametersService.numIterations;
  public readonly alpha = this.#hyperparametersService.alpha;
  public readonly beta = this.#hyperparametersService.beta;

  public toggleCard(): void {
    this.isCollapsed.set(!this.isCollapsed());
  }
}
