import { Component, computed, input } from '@angular/core';

export type ToastType = 'info' | 'success' | 'warning' | 'danger';

@Component({
  selector: 'app-toast',
  templateUrl: 'toast.component.html',
  styleUrl: 'toast.component.css',
})
export class ToastComponent {
  public readonly message = input.required<string>();
  public readonly type = input<ToastType>('info');

  public readonly isInfo = computed(() => this.type() === 'info');
  public readonly isSuccess = computed(() => this.type() === 'success');
  public readonly isWarning = computed(() => this.type() === 'warning');
  public readonly isDanger = computed(() => this.type() === 'danger');
}
