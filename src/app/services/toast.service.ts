import { ComponentRef, Injectable, ViewContainerRef } from '@angular/core';
import { ToastComponent, type ToastType } from '../components/toast/toast.component';

@Injectable({ providedIn: 'root' })
export class ToastService {
  #toastComponentRef: ComponentRef<ToastComponent> | undefined;
  #viewContainerRef: ViewContainerRef | undefined;

  /**
   * Sets the view container reference for the toast service.
   */
  public setViewContainerRef(viewContainerRef: ViewContainerRef) {
    this.#viewContainerRef = viewContainerRef;
  }

  /**
   * Shows a danger toast with the given message.
   */
  public showDangerToast(message: string, duration: number = 3000) {
    this.showToast('danger', message, duration);
  }

  /**
   * Shows a warning toast with the given message.
   */
  public showWarningToast(message: string, duration: number = 3000) {
    this.showToast('warning', message, duration);
  }

  /**
   * Shows a warning toast with the given message.
   */
  public showInfoToast(message: string, duration: number = 3000) {
    this.showToast('info', message, duration);
  }

  /**
   * Shows a toast of given type with the given message.
   */
  public showToast(type: ToastType, message: string, duration: number = 3000) {
    if (this.#toastComponentRef || !this.#viewContainerRef) {
      return;
    }

    this.#toastComponentRef = this.#viewContainerRef.createComponent(ToastComponent);
    this.#toastComponentRef.setInput('message', message);
    this.#toastComponentRef.setInput('type', type);

    setTimeout(() => this.closeToast(), duration);
  }

  /**
   * Closes the toast.
   */
  public closeToast() {
    if (this.#toastComponentRef) {
      this.#toastComponentRef.destroy();
      this.#toastComponentRef = undefined;
    }
  }
}
