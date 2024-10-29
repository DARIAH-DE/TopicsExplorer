import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { faDownload, faLayerGroup, faMoon, faRotateLeft, faSun, faUpload } from '@fortawesome/free-solid-svg-icons';
import { ModelService } from '../../services/model.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.scss',
  standalone: true,
  imports: [FaIconComponent]
})
export class NavbarComponent {
  #theme: 'dark' | 'light' = 'dark';
  #modelService = inject(ModelService);
  #router = inject(Router);

  public readonly hasModel = this.#modelService.hasModel;

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
    // this.#modelService.setModel();
  }

  /**
   * Downloads the current model.
   */
  public downloadModel(): void {}

  /**
   * Resets the current model.
   */
  public async clearModel(): Promise<void> {
    await this.#modelService.clearModel();
    await this.#router.navigate(['/']);
  }

  /**
   * Toggles the theme between light and dark mode.
   */
  public toggleTheme() {
    this.#theme = this.isDarkTheme ? 'light' : 'dark';
    document.getElementById('root')?.setAttribute('data-theme', this.#theme);
  }

  /**
   * True if the current theme is dark.
   */
  public get isDarkTheme(): boolean {
    return this.#theme === 'dark';
  }

  /**
   * True if the current theme is light.
   */
  public get isLightTheme(): boolean {
    return this.#theme === 'light';
  }
}
