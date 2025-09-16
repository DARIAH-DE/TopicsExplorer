import { computed, Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  public readonly theme = signal<'dark' | 'light'>('dark');

  public readonly isLightTheme = computed(() => this.theme() === 'light');
  public readonly isDarkTheme = computed(() => this.theme() === 'dark');

  /**
   * Toggles the theme between light and dark mode.
   */
  public toggleTheme(): void {
    this.theme.set(this.isDarkTheme() ? 'light' : 'dark');
    document.getElementById('root')?.setAttribute('data-theme', this.theme());
  }
}
