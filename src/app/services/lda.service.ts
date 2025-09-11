import { Injectable } from '@angular/core';
import { invoke } from '@tauri-apps/api/core';
import { LdaResult, LdaHyperparameters, TextDocument } from '../core/core.models';

@Injectable({ providedIn: 'root' })
export class LdaService {
  /**
   * Trains an LDA model using the provided documents and parameters.
   */
  public async trainModel(docs: TextDocument[], params: LdaHyperparameters): Promise<LdaResult> {
    return await invoke<LdaResult>('train_model', { docs, params });
  }
}
