import { Component, computed, inject, input, ChangeDetectionStrategy } from '@angular/core';
import { Router } from '@angular/router';
import { Topic } from '../../core/core.models';
import { NavigationService } from '../../services/navigation.service';

@Component({
  selector: 'app-topic-bar',
  templateUrl: './topic-bar.component.html',
  styleUrl: './topic-bar.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TopicBarComponent {
  readonly #navigationService = inject(NavigationService);

  public readonly topic = input.required<Topic>();

  public readonly label = computed(() =>
    this.topic()
      .topWords.slice(0, 10)
      .map(({ word }) => word)
      .join(' '),
  );
  public readonly width = computed(() => {
    const score = this.topic().dominanceScore;
    const percentage = Math.min(score * 100 + 50, 100);
    return `${percentage}%`;
  });

  public onClick(): void {
    this.#navigationService.navigateTopic(this.topic().topicIndex);
  }
}
