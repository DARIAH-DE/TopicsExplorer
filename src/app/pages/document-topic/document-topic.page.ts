import { Component, inject } from '@angular/core';
import { LdaService } from '../../services/lda.service';

@Component({
  selector: 'app-document-topic',
  templateUrl: './document-topic.page.html',
  styleUrl: './document-topic.page.css',
})
export class DocumentTopicPage {
  readonly #ldaService = inject(LdaService);
}
