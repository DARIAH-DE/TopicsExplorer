import {
  AfterViewInit,
  Component,
  inject,
  OnDestroy,
  OnInit,
  signal,
  ViewChild,
  ViewContainerRef,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { faFileArrowUp } from '@fortawesome/free-solid-svg-icons';
import { ProcessingModalComponent } from '../../components/training-modal/training-modal.component';
import { ToastService } from '../../services/toast.service';
import { TextCorpus, TopicModelOptions, WorkerMessage } from '../../shared/interfaces.shared';
import { TopicModel } from '../../shared/topic-model.shared';
import { Maybe } from '../../shared/types.shared';
import { getTokens, getVocabulary } from '../../shared/utils.shared';
import { TopicsTableComponent } from "../../components/topics-table/topics-table.component";

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [FaIconComponent, FormsModule, ProcessingModalComponent, TopicsTableComponent],
  providers: [ToastService],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
})
export class HomeComponent implements OnInit, OnDestroy, AfterViewInit {
  public faFileArrowUp = faFileArrowUp;

  public currentIteration = signal(0);
  public isTraining = signal(false);

  public textCorpus: Maybe<TextCorpus>;
  public numDocuments = 0;
  public model: Maybe<TopicModel>;

  public numTopics: number = 10;
  public numIterations: number = 1000;
  public alpha: number = 0.1;
  public beta: number = 0.01;

  public topics: any[] = [];

  #worker: Maybe<Worker>;
  #toastService = inject(ToastService);

  @ViewChild('toastContainer', { read: ViewContainerRef }) viewContainerRef!: ViewContainerRef;

  /**
   * Initializes the component and creates a new Web Worker.
   */
  public ngOnInit(): void {
    this.setWorker();
  }

  /**
   * Sets the view container reference for the toast service.
   */
  public ngAfterViewInit(): void {
    this.#toastService.setViewContainerRef(this.viewContainerRef);
  }

  /**
   * Creates a new Web Worker for training the topic model.
   */
  private setWorker(): void {
    if (typeof Worker !== 'undefined') {
      this.#worker = new Worker(new URL('../../workers/topic-model.worker', import.meta.url));

      this.#worker.onmessage = this.onMessage.bind(this);
    } else {
      this.#toastService.showDangerToast('Sorry, your browser does not support Web Workers.');
    }
  }

  /**
   * Handles the message event from the Web Worker.
   */
  private onMessage(message: MessageEvent<WorkerMessage>): void {
    this.currentIteration.set(message.data.currentIteration);
    this.topics = message.data.topics;

    if (message.data.currentIteration === this.numIterations) {
      this.isTraining.set(false);
      this.model = message.data.model;
      this.topics = message.data.model?.getTopics(5) ?? [];
    }
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
   * Loads and tokenizes the text documents from the file input.
   */
  public async onFilesChanged(event: Event): Promise<void> {
    if (!(event.target instanceof HTMLInputElement) || !event.target.files) {
      this.#toastService.showDangerToast('No files selected');
      return;
    }

    const textDocuments = [];
    for (const file of event.target.files) {
      const text = await file.text();
      const tokens = getTokens(text.toLocaleLowerCase());

      textDocuments.push({
        id: crypto.randomUUID(),
        name: file.name,
        text,
        tokens,
      });

      this.numDocuments++;
    }

    const vocabulary = getVocabulary(textDocuments);
    for (const textDocument of textDocuments) {
      textDocument.tokens = textDocument.tokens.filter((token) => vocabulary.has(token.text));
    }

    this.textCorpus = { textDocuments, vocabSize: vocabulary.size };
  }

  /**
   * Trains the topic model on the currently loaded text documents.
   */
  public trainModel(): void {
    if (!this.#worker || !this.textCorpus) {
      this.#toastService.showDangerToast('Sorry, cannot start training.');
      return;
    }

    this.isTraining.set(true);
    this.#worker.postMessage({ textCorpus: this.textCorpus, options: this.topicModelOptions });
  }

  /**
   * Cancels the training of the topic model and resets the worker.
   */
  public onCancel(): void {
    if (this.#worker) {
      this.#worker.terminate();
    }

    this.currentIteration.set(0);
    this.isTraining.set(false);

    this.setWorker();
  }

  /**
   * Current options for the topic model.
   */
  private get topicModelOptions(): TopicModelOptions {
    return { numTopics: this.numTopics, numIterations: this.numIterations, alpha: this.alpha, beta: this.beta };
  }
}
