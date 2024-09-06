import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-processing-modal',
  standalone: true,
  imports: [],
  templateUrl: './processing-modal.component.html',
  styleUrl: './processing-modal.component.scss'
})
export class ProcessingModalComponent {
  @Input() isActive = false;
  @Input() currentValue: number = 0;
  @Input() maxValue: number = 0;
  @Output() close = new EventEmitter<void>();


  public onClose(): void {
    this.close.emit();
  }
}
