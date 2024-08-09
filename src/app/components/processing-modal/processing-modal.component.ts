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
  @Input() currentProgress = 0;
  @Output() close = new EventEmitter<void>();


  public onClose(): void {
    this.close.emit();
  }
}
