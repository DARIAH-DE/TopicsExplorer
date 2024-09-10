import { Component, EventEmitter, Input, Output } from '@angular/core';
import { TopicsTableComponent } from '../topics-table/topics-table.component';

@Component({
  selector: 'app-training-modal',
  standalone: true,
  imports: [TopicsTableComponent],
  templateUrl: './training-modal.component.html',
  styleUrl: './training-modal.component.scss',
})
export class ProcessingModalComponent {
  @Input() isActive = false;
  @Input() currentValue: number = 0;
  @Input() maxValue: number = 0;
  @Input() topics: any[] = [];
  @Output() cancel = new EventEmitter<void>();

  public onCancel(): void {
    this.cancel.emit();
    this.isActive = false;
  }
}
