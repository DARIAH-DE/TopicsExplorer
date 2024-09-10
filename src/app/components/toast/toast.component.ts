import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-toast',
  templateUrl: 'toast.component.html',
  styleUrl: 'toast.component.scss',
  standalone: true,
})
export class ToastComponent {
  @Input() message: string = '';
  @Input() type: 'info' | 'success' | 'warning' | 'danger' = 'info';

  public get isInfo(): boolean {
    return this.type === 'info';
  }

  public get isSuccess(): boolean {
    return this.type === 'success';
  }

  public get isWarning(): boolean {
    return this.type === 'warning';
  }

  public get isDanger(): boolean {
    return this.type === 'danger';
  }
}
