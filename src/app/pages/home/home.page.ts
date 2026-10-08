import { Component } from '@angular/core';

@Component({
  selector: 'app-home',
  templateUrl: './home.page.html',
  styleUrl: './home.page.css',
})
export class HomePage {
  public async trainModel(): Promise<void> {
    console.info('training');
  }
}
