import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { faFileArrowUp } from '@fortawesome/free-solid-svg-icons';
import { TrainingModalComponent } from '../../components/training-modal/training-modal.component';
import { CorpusService } from '../../services/corpus.service';
import { ModelService } from '../../services/model.service';
import { ToastService } from '../../services/toast.service';
import { Maybe } from '../../shared/types.shared';
import { getTokens, getVocabulary } from '../../shared/utils.shared';

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrl: './settings.component.scss',
  imports: [FaIconComponent, FormsModule, TrainingModalComponent],
  standalone: true,
})
export class SettingsComponent implements OnInit, OnDestroy {
  #modelService = inject(ModelService);
  #corpusService = inject(CorpusService);
  #toastService = inject(ToastService);
  #router = inject(Router);

  #worker: Maybe<Worker>;
  #isProcessingTextDocuments = false;

  public readonly faFileArrowUp = faFileArrowUp;
  public readonly numDocuments = this.#corpusService.numDocuments;
  public statusMessage = '';

  /**
   * Initializes the component, creates a new Web Worker and optionally clears the corpus and model.
   */
  public async ngOnInit(): Promise<void> {
    this.setWorker();

    await Promise.all([this.#corpusService.clearCorpus(), this.#modelService.clearModel()]);
  }

  /**
   * Terminates the Web Worker when the component is destroyed.
   */
  public ngOnDestroy(): void {
    if (this.#worker) {
      this.#worker.terminate();
    }
  }

  /**
   * Creates a new Web Worker for training the topic model.
   */
  private setWorker(): void {
    if (typeof Worker !== 'undefined') {
      this.#worker = new Worker(new URL('../../workers/topic-model.worker', import.meta.url));

      this.#worker.onmessage = this.onMessage.bind(this);
    } else {
      this.#toastService.showDangerToast('Sorry, your browser does not support training a model.');
    }
  }

  /**
   * Handles the message event from the Web Worker.
   */
  private async onMessage(message: MessageEvent<{ currentIteration: number; isFinished: boolean }>): Promise<void> {
    this.#modelService.setCurrentIteration(message.data.currentIteration);

    if (message.data.isFinished) {
      await this.#modelService.finishTraining();
      await this.#router.navigate(['/topics']);
    }
  }

  /**
   * Trains the topic model on the currently loaded text documents.
   */
  public trainModel(): void {
    if (!this.#worker) {
      this.#toastService.showDangerToast('Sorry, your browser does not support training a model.');
      return;
    }

    this.#modelService.startTraining();
    this.#worker.postMessage({ options: this.#modelService.getOptions() });
  }

  /**
   * Cancels the training of the topic model and resets the worker.
   */
  public async onCancel(): Promise<void> {
    if (this.#worker) {
      this.#worker.terminate();
    }

    this.setWorker();

    await this.#modelService.finishTraining();
    await this.#router.navigate(['/topics']);
  }

  /**
   * Loads and tokenizes the text documents from the file input.
   */
  public async onFilesChanged(event: Event): Promise<void> {
    if (!(event.target instanceof HTMLInputElement) || !event.target.files) {
      return;
    }

    if (event.target.files.length > 0) {
      // Delete existing corpus if at least one file is selected
      await this.#corpusService.clearCorpus();
    }

    this.#isProcessingTextDocuments = true;
    const counts = new Map<string, number>();

    for (const file of event.target.files) {
      this.statusMessage = `Processing ${file.name}`;
      const text = await file.text();
      const tokens = getTokens(text.toLocaleLowerCase());
      const textDocument = {
        id: crypto.randomUUID(),
        name: file.name,
        text,
        tokens,
      };

      for (const token of tokens) {
        counts.set(token.text, (counts.get(token.text) || 0) + 1);
      }

      await this.#corpusService.saveTextDocument(textDocument)
    }

    this.statusMessage = 'Extracing vocabulary from text corpus';
    const vocabulary = getVocabulary(counts);
    await this.#corpusService.saveVocabulary(vocabulary);
    this.statusMessage = '';

    this.#isProcessingTextDocuments = false;
  }

  public get isReady(): boolean {
    return Boolean(!this.#isProcessingTextDocuments && this.#corpusService.hasCorpus() && this.numTopics && this.numIterations && this.alpha && this.beta);
  }

  public get numTopics(): number {
    return this.#modelService.numTopics();
  }

  public set numTopics(value: number) {
    this.#modelService.numTopics.set(value);
  }

  public get numIterations(): number {
    return this.#modelService.numIterations();
  }

  public set numIterations(value: number) {
    this.#modelService.numIterations.set(value);
  }

  public get alpha(): number {
    return this.#modelService.alpha();
  }

  public set alpha(value: number) {
    this.#modelService.alpha.set(value);
  }

  public get beta(): number {
    return this.#modelService.beta();
  }

  public set beta(value: number) {
    this.#modelService.beta.set(value);
  }
}
