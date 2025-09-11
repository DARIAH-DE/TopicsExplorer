import { Routes } from '@angular/router';
import { HomePage } from './pages/home/home.page';
import { TopicsPage } from './pages/topics/topics.page';
import { TrainingPage } from './pages/training/training.page';

export const routes: Routes = [
  { path: '', component: HomePage },
  { path: 'training', component: TrainingPage },
  { path: 'topics', component: TopicsPage },
];
