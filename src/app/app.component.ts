import { AfterViewInit, Component, inject, viewChild, ViewContainerRef } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent } from './components/navbar/navbar.component';
import { ToastService } from './services/toast.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
  imports: [NavbarComponent, RouterOutlet],
  standalone: true,
})
export class AppComponent implements AfterViewInit {
  #toastService = inject(ToastService);

  public readonly toastContainer = viewChild.required('toastContainer', { read: ViewContainerRef });

  /**
   * Sets the view container reference for the toast service.
   */
  public ngAfterViewInit(): void {
    this.#toastService.setViewContainerRef(this.toastContainer());
  }
}
