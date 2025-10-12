import { Component, inject, signal } from '@angular/core';
import { CorpusService } from '../../services/corpus.service';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { faFileArrowUp, faBook, faAngleUp, faAngleDown } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-corpus',
  templateUrl: './corpus.component.html',
  styleUrl: './corpus.component.css',
  imports: [FaIconComponent],
})
export class CorpusComponent {
  readonly #documentService = inject(CorpusService);

  public readonly faAngleUp = faAngleUp;
  public readonly faAngleDown = faAngleDown;
  public readonly faBook = faBook;
  public readonly faFileArrowUp = faFileArrowUp;

  public readonly isCollapsed = signal(true);
  public readonly numDocuments = this.#documentService.numDocuments;

  public async onFilesChanged(event: Event): Promise<void> {
    if (!(event.target instanceof HTMLInputElement) || !event.target.files) {
      return;
    }

    this.isCollapsed.set(false);

    await this.#documentService.loadFiles(event.target.files);
  }

  public toggleCard(): void {
    this.isCollapsed.set(!this.isCollapsed());
  }
}
