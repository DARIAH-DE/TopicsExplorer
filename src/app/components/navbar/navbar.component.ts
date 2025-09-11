import { Component, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { faDownload, faLayerGroup, faMoon, faRotateLeft, faSun, faUpload } from '@fortawesome/free-solid-svg-icons';
import { LdaService } from '../../services/lda.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css',
  imports: [FaIconComponent],
})
export class NavbarComponent {
  readonly #ldaService = inject(LdaService);
  readonly #router = inject(Router);

  public readonly hasModel = this.#ldaService.hasModel;

  public readonly theme = signal<'dark' | 'light'>('dark');

  public readonly isLightTheme = computed(() => this.theme() === 'light');
  public readonly isDarkTheme = computed(() => this.theme() === 'dark');

  public readonly faLayerGroup = faLayerGroup;
  public readonly faRotateLeft = faRotateLeft;
  public readonly faDownload = faDownload;
  public readonly faSun = faSun;
  public readonly faMoon = faMoon;
  public readonly faUpload = faUpload;

  /**
   * Uploads a previously saved model.
   */
  public uploadModel(): void {
    // TODO: implement this
  }

  /**
   * Downloads the current model.
   */
  public downloadModel(): void {
    // TODO: implement this
  }

  /**
   * Resets the current model.
   */
  public async clearModel(): Promise<void> {
    await this.#router.navigate(['/']);
  }

  /**
   * Toggles the theme between light and dark mode.
   */
  public toggleTheme(): void {
    this.theme.set(this.isDarkTheme() ? 'light' : 'dark');
    document.getElementById('root')?.setAttribute('data-theme', this.theme());
  }
}
