import { Component, OnDestroy, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { faFileArrowUp } from '@fortawesome/free-solid-svg-icons';
import { ProcessingModalComponent } from '../../components/processing-modal/processing-modal.component';
import { TextCorpus, TopicModelOptions } from '../../shared/interfaces.shared';
import { TopicModel } from '../../shared/topic-model.shared';
import { Maybe } from '../../shared/types.shared';
import { getTokens, getVocabulary } from '../../shared/utils.shared';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [FaIconComponent, FormsModule, ProcessingModalComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
})
export class HomeComponent implements OnInit, OnDestroy {
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

  /**
   * Initializes the component and creates a new Web Worker.
   */
  public ngOnInit(): void {
    if (typeof Worker !== 'undefined') {
      this.#worker = new Worker(new URL('../../workers/topic-model.worker', import.meta.url));

      this.#worker.onmessage = (message: MessageEvent<{ model: Maybe<TopicModel>; currentIteration: number }>) => {
        this.currentIteration.set(message.data.currentIteration);
        if (message.data.model) {
          this.model = message.data.model;
          this.topics = message.data.model.getTopics();
          this.isTraining.set(false);
        }
      };
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
      // TODO throw error
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
      // TODO throw error
      return;
    }

    this.isTraining.set(true);
    this.#worker.postMessage({
      textCorpus: this.textCorpus,
      options: this.topicModelOptions,
    });
  }

  private get topicModelOptions(): TopicModelOptions {
    return { numTopics: this.numTopics, numIterations: this.numIterations, alpha: this.alpha, beta: this.beta };
  }
}
