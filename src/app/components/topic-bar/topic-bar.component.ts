import { NgStyle } from '@angular/common';
import { Component, computed, inject, input } from '@angular/core';
import { Router } from '@angular/router';
import { Topic } from '../../core/core.models';

@Component({
  selector: 'app-topic-bar',
  templateUrl: './topic-bar.component.html',
  styleUrl: './topic-bar.component.css',
})
export class TopicBarComponent {
  readonly #router = inject(Router);

  public readonly topic = input.required<Topic>();

  public readonly label = computed(() =>
    this.topic()
      .topWords.slice(0, 10)
      .map(({ word }) => word)
      .join(' '),
  );
  public readonly width = computed(() => `${this.topic().dominanceScore * 100}%`);

  public onClick(): void {
    this.#router.navigate(['topics', this.topic().topicIndex]);
  }
}
