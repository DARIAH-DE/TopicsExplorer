import { Component, inject } from '@angular/core';
import { LdaService } from '../../services/lda.service';

@Component({
  selector: 'app-topics',
  templateUrl: './topics.page.html',
  styleUrl: './topics.page.css',
})
export class TopicsPage {
  readonly #ldaService = inject(LdaService);

  public readonly topics = this.#ldaService.topics;
}
