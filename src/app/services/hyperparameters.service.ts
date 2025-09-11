import { computed, Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class HyperparametersService {
  public readonly numTopics = signal(10);
  public readonly numIterations = signal(1_000);
  public readonly alpha = signal(0.1);
  public readonly beta = signal(0.01);

  public readonly hasValidNumTopics = computed(() => {
    const numTopics = this.numTopics();
    return numTopics > 0 && numTopics <= 1_000;
  });

  public readonly hasValidNumIterations = computed(() => {
    const numIterations = this.numIterations();
    return numIterations > 0 && numIterations <= 100_000;
  });

  public readonly hasValidAlpha = computed(() => {
    const alpha = this.alpha();
    return alpha > 0 && alpha <= 1;
  });

  public readonly hasValidBeta = computed(() => {
    const beta = this.beta();
    return beta > 0 && beta <= 1;
  });

  public readonly hasValidHyperparameters = computed(() => {
    const numTopicsValid = this.hasValidNumTopics();
    const numIterationsValid = this.hasValidNumIterations();
    const alphaValid = this.hasValidAlpha();
    const betaValid = this.hasValidBeta();
    return numTopicsValid && numIterationsValid && alphaValid && betaValid;
  });
}
