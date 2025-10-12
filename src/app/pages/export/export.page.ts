import { Component, inject } from '@angular/core';
import { LdaService } from '../../services/lda.service';

@Component({
  selector: 'app-export',
  templateUrl: './export.page.html',
  styleUrl: './export.page.css',
})
export class ExportPage {
  readonly #ldaService = inject(LdaService);

  public readonly topics = this.#ldaService.topics;
}
