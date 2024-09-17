import { Component } from '@angular/core';

type ToastType = 'info' | 'success' | 'warning' | 'danger';

@Component({
  selector: 'app-toast',
  templateUrl: 'toast.component.html',
  styleUrl: 'toast.component.scss',
  standalone: true,
})
export class ToastComponent {
  public message: string = '';
  public type: ToastType = 'info';

  /**
   * True if the toast is an info message.
   */
  public get isInfo(): boolean {
    return this.type === 'info';
  }

  /**
   * True if the toast is a success message.
   */
  public get isSuccess(): boolean {
    return this.type === 'success';
  }

  /**
   * True if the toast is a warning message.
   */
  public get isWarning(): boolean {
    return this.type === 'warning';
  }

  /**
   * True if the toast is a danger message.
   */
  public get isDanger(): boolean {
    return this.type === 'danger';
  }
}
