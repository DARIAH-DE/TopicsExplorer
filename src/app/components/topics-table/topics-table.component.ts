import { Component, Input } from '@angular/core';
import { Topic } from '../../shared/interfaces.shared';

@Component({
  selector: 'app-topics-table',
  templateUrl: './topics-table.component.html',
  styleUrl: './topics-table.component.scss',
  standalone: true,
})
export class TopicsTableComponent {
  @Input() topics!: Topic[];
}
