import { Component, inject, input, OnInit } from '@angular/core';
import { TopicBarComponent } from '../../components/topic-bar/topic-bar.component';
import { TopicModel } from '../../shared/topic-model.shared';
import { ModelService } from '../../services/model.service';
import { CorpusService } from '../../services/corpus.service';
import { Topic } from '../../shared/interfaces.shared';

@Component({
  selector: 'app-topics',
  templateUrl: './topics.component.html',
  styleUrl: './topics.component.scss',
  imports: [TopicBarComponent],
  standalone: true,
})
export class TopicsComponent implements OnInit {
  public numTopics = 0;
  public numDocuments = 0;
  public topics: Topic[] = [];

  #modelService = inject(ModelService);
  #corpusService = inject(CorpusService);

  public async ngOnInit(): Promise<void> {
    this.numTopics = this.#modelService.getOptions().numTopics;
    this.numDocuments = this.#corpusService.numDocuments();
    this.topics = await this.#modelService.getTopics();
  }
}
