import { Component, inject } from '@angular/core';
import { LdaService } from '../../services/lda.service';
import { TopicBarComponent } from '../../components/topic-bar/topic-bar.component';

@Component({
  selector: 'app-topics',
  templateUrl: './topics.page.html',
  styleUrl: './topics.page.css',
  imports: [TopicBarComponent],
})
export class TopicsPage {
  readonly #ldaService = inject(LdaService);

  public readonly topics = this.#ldaService.topics;
}
