import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { faFileArrowUp } from '@fortawesome/free-solid-svg-icons';
import { ProcessingModalComponent } from '../../components/processing-modal/processing-modal.component';
import { TextCorpus, TextDocument } from '../../shared/interfaces.shared';
import { TopicModel } from '../../shared/topic-model.shared';
import { Maybe, Nullable } from '../../shared/types.shared';
import { getTokens, getVocabulary, tokenizeText } from '../../shared/utils.shared';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [FaIconComponent, FormsModule, ProcessingModalComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
})
export class HomeComponent {
  public faFileArrowUp = faFileArrowUp;

  public textCorpus: Maybe<TextCorpus>;
  public numDocuments = 0;
  public model: Maybe<TopicModel>;

  public numTopics: number = 10;
  public numIterations: number = 1000;
  public topics: any[] = [];
  public currentProgress: number = 0;

  public isTraining: boolean = false;

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
    this.isTraining = true;

    const options = {
      numTopics: this.numTopics,
      numIterations: this.numIterations,
    };

    const model = new TopicModel(this.textCorpus!, options);
    for (let i = 0; i < this.numIterations; i++) {
      model.update();
      this.currentProgress = i;
    }

    this.topics = model.getTopicWords();
    this.isTraining = false;
  }
}
