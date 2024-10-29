import { Component, inject, output } from '@angular/core';
import { ModelService } from '../../services/model.service';
import { TopicsTableComponent } from '../topics-table/topics-table.component';
import { ToastService } from '../../services/toast.service';

@Component({
  selector: 'app-training-modal',
  templateUrl: './training-modal.component.html',
  styleUrl: './training-modal.component.scss',
  imports: [TopicsTableComponent],
  standalone: true,
})
export class TrainingModalComponent {
  #modelService = inject(ModelService);
  #toastService = inject(ToastService);

  public readonly isTraining = this.#modelService.isTraining;
  public readonly currentIteration = this.#modelService.currentIteration;
  public readonly numIterations = this.#modelService.numIterations;

  public readonly cancel = output<void>();

  /**
   * Cancels the training process.
   */
  public onCancel(): void {
    this.#toastService.showInfoToast(`You have stopped training after ${this.currentIteration} iterations.`);
    this.cancel.emit();
  }
}
