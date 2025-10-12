import { Routes } from '@angular/router';
import { DocumentTopicPage } from './pages/document-topic/document-topic.page';
import { ExportPage } from './pages/export/export.page';
import { HomePage } from './pages/home/home.page';
import { TopicPage } from './pages/topic/topic.page';
import { TopicsPage } from './pages/topics/topics.page';
import { TrainingPage } from './pages/training/training.page';

export const routes: Routes = [
  { path: '', component: HomePage },
  { path: 'training', component: TrainingPage },
  { path: 'topics', component: TopicsPage },
  { path: 'topics/:id', component: TopicPage },
  { path: 'document-topic', component: DocumentTopicPage },
  { path: 'export', component: ExportPage },
];
