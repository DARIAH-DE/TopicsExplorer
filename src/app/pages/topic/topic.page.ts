import { Component, inject } from '@angular/core';
import { LdaService } from '../../services/lda.service';

@Component({
  selector: 'app-topic',
  templateUrl: './topic.page.html',
  styleUrl: './topic.page.css',
})
export class TopicPage {
  readonly #ldaService = inject(LdaService);

  public readonly topics = this.#ldaService.topics;
}
