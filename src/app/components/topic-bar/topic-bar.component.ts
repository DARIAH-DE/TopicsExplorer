import { NgStyle } from '@angular/common';
import { Component, inject, input } from '@angular/core';
import { Topic } from '../../shared/interfaces.shared';
import { Router } from '@angular/router';

@Component({
  selector: 'app-topic-bar',
  templateUrl: './topic-bar.component.html',
  styleUrl: './topic-bar.component.scss',
  imports: [NgStyle],
  standalone: true,
})
export class TopicBarComponent {
  #router = inject(Router);

  readonly topic = input.required<Topic>();

  /**
   * Label for the topic bar (the first 10 words).
   */
  public get label(): string {
    return this.topic()
      .words.slice(0, 10)
      .map((word) => word.text)
      .join(' ');
  }

  public get width(): string {
    return `calc(50% + ${Math.round(this.topic().presence * 100)}%)`;
  }

  /**
   * Navigates to the topic page.
   */
  public onClick(): void {
    this.#router.navigate(['topics', this.topic().id]);
  }
}
