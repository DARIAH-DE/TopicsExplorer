import { Routes } from '@angular/router';
import { HomePage } from './pages/home/home.page';
import { TrainingPage } from './pages/training/training.page';

export const routes: Routes = [
  { path: '', component: HomePage },
  { path: 'training', component: TrainingPage },
];
