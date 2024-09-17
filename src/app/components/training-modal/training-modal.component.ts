import { Component, input, output } from '@angular/core';
import { Topic } from '../../shared/interfaces.shared';
import { TopicsTableComponent } from '../topics-table/topics-table.component';

@Component({
  selector: 'app-training-modal',
  templateUrl: './training-modal.component.html',
  styleUrl: './training-modal.component.scss',
  imports: [TopicsTableComponent],
  standalone: true,
})
export class TrainingModalComponent {
  public readonly isTraining = input(false);
  public readonly currentValue = input(0);
  public readonly maxValue = input(0);
  public readonly topics = input<Topic[]>([]);

  public readonly cancel = output<void>();

  /**
   * Cancels the training process.
   */
  public onCancel(): void {
    this.cancel.emit();
  }
}
