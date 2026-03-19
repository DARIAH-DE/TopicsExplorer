import { Location } from '@angular/common';
import { Component, computed, inject, signal, ChangeDetectionStrategy } from '@angular/core';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { faArrowLeft, faArrowRight, faDownload, faLayerGroup, faMoon, faSun } from '@fortawesome/free-solid-svg-icons';
import { CorpusService } from '../../services/corpus.service';
import { LdaService } from '../../services/lda.service';
import { NavigationService } from '../../services/navigation.service';
import { ThemeService } from '../../services/theme.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css',
  imports: [FaIconComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class NavbarComponent {
  readonly #corpusService = inject(CorpusService);
  readonly #ldaService = inject(LdaService);
  readonly #location = inject(Location);
  readonly #navigationService = inject(NavigationService);
  readonly #themeService = inject(ThemeService);

  public readonly hasDocuments = this.#corpusService.hasDocuments;
  public readonly hasModel = this.#ldaService.hasModel;

  public readonly theme = this.#themeService.theme;

  public readonly isLightTheme = this.#themeService.isLightTheme;
  public readonly isDarkTheme = this.#themeService.isDarkTheme;

  public readonly faLayerGroup = faLayerGroup;

  public readonly faArrowLeft = faArrowLeft;
  public readonly faArrowRight = faArrowRight;

  public readonly faDownload = faDownload;
  public readonly faSun = faSun;
  public readonly faMoon = faMoon;

  public readonly isHome = this.#navigationService.isHome;
  public readonly isTraining = this.#navigationService.isTraining;
  public readonly isTopics = this.#navigationService.isTopics;
  public readonly isTopic = this.#navigationService.isTopic;
  public readonly isDocuments = this.#navigationService.isDocuments;
  public readonly isDocument = this.#navigationService.isDocument;
  public readonly isDocumentTopic = this.#navigationService.isDocumentTopic;
  public readonly isVocabulary = this.#navigationService.isVocabulary;
  public readonly isExport = this.#navigationService.isExport;

  public readonly showTraining = computed(
    () => this.#ldaService.isTraining() || this.#ldaService.currentIteration() > 0,
  );

  public async navigateHome(): Promise<void> {
    await this.#navigationService.navigateHome();
  }

  public async navigateTraining(): Promise<void> {
    await this.#navigationService.navigateTraining();
  }

  public async navigateTopics(): Promise<void> {
    await this.#navigationService.navigateTopics();
  }

  public async navigateDocuments(): Promise<void> {
    await this.#navigationService.navigateDocuments();
  }

  public async navigateDocumentTopic(): Promise<void> {
    await this.#navigationService.navigateDocumentTopic();
  }

  public async navigateVocabulary(): Promise<void> {
    await this.#navigationService.navigateVocabulary();
  }

  public async navigateExport(): Promise<void> {
    await this.#navigationService.navigateExport();
  }

  /**
   * Downloads the current model.
   */
  public async downloadModel(): Promise<void> {
    await this.#ldaService.downloadModel();
  }

  /**
   * Toggles the theme between light and dark mode.
   */
  public toggleTheme(): void {
    this.#themeService.toggleTheme();
  }
}
