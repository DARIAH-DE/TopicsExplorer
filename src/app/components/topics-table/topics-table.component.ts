import { Component, input } from '@angular/core';
import { Topic } from '../../shared/interfaces.shared';

@Component({
  selector: 'app-topics-table',
  templateUrl: './topics-table.component.html',
  styleUrl: './topics-table.component.scss',
  standalone: true,
})
export class TopicsTableComponent {
  public readonly topics = input.required<Topic[]>();
}
