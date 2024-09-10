import { ComponentRef, Injectable, ViewContainerRef } from '@angular/core';
import { ToastComponent } from '../components/toast/toast.component';
import { Maybe } from '../shared/types.shared';

@Injectable()
export class ToastService {
  #toastComponentRef: Maybe<ComponentRef<ToastComponent>>;
  #viewContainerRef: Maybe<ViewContainerRef>;

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
   * Shows a toast of given type with the given message.
   */
  public showToast(type: 'warning' | 'danger', message: string, duration: number = 3000) {
    if (this.#toastComponentRef || !this.#viewContainerRef) {
      return;
    }

    this.#toastComponentRef = this.#viewContainerRef.createComponent(ToastComponent);
    this.#toastComponentRef.instance.message = message;
    this.#toastComponentRef.instance.type = type;

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
