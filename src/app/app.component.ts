import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { faDownload, faLayerGroup, faMoon, faSun } from '@fortawesome/free-solid-svg-icons';
import { HomeComponent } from './pages/home/home.component';
import { ModelComponent } from './pages/model/model.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FaIconComponent, RouterOutlet, HomeComponent, ModelComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  public faDownload = faDownload;
  public faLayerGroup = faLayerGroup;
  public faSun = faSun;
  public faMoon = faMoon;

  #theme: 'dark' | 'light' = 'dark';

  /**
   * Toggles the theme between light and dark mode.
   */
  public toggleTheme() {
    this.#theme = this.isDarkTheme ? 'light' : 'dark';
    const root = document.getElementById('root');
    if (root) {
      root.setAttribute('data-theme', this.#theme);
    }
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
