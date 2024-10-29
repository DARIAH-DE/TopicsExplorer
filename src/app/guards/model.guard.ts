import { inject } from '@angular/core';
import { CanActivateFn } from '@angular/router';
import { ModelService } from '../services/model.service';
import { ToastService } from '../services/toast.service';

/**
 * Guard to ensure that a model is available before navigating to a route.
 */
export const modelGuard: CanActivateFn = (_route, _state) => {
  const modelService = inject(ModelService);
  const toastService = inject(ToastService);

  if (modelService.hasModel()) {
    return true;
  } else {
    toastService.showDangerToast('You must train a model before you can access this page.');
    return false;
  }
};
