import { Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ModelService } from '../../services/model.service';
import { TextDocument } from '../../shared/interfaces.shared';
import { CorpusService } from '../../services/corpus.service';


interface Foo extends TextDocument {
  proportion: number;
}

@Component({
  selector: 'app-topic',
  templateUrl: './topic.component.html',
  styleUrl: './topic.component.scss',
  standalone: true,
})
export class TopicComponent implements OnInit {
  #router = inject(ActivatedRoute);
  #modelService = inject(ModelService);
  #corpusService = inject(CorpusService);

  public textDocumentTitles: Foo[] = [];

  public async ngOnInit(): Promise<void> {
    const topicId = this.#router.snapshot.paramMap.get('id');

    const model = await this.#modelService.getModel();
    if (model) {
      const docs: any[] = []; // model.getDocumentsForTopic(Number(topicId!));
      for (const doc of docs) {
        const textDocument = await this.#corpusService.getTextDocument(doc.documentId);
        if (textDocument) {
          this.textDocumentTitles.push({...textDocument, proportion: doc.proportion});
        }
      }
    }
  }
}
