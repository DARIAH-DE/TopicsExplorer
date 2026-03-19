import { Routes } from '@angular/router';
import { DocumentTopicPage } from './pages/document-topic/document-topic.page';
import { DocumentPage } from './pages/document/document.page';
import { DocumentsPage } from './pages/documents/documents.page';
import { ExportPage } from './pages/export/export.page';
import { HomePage } from './pages/home/home.page';
import { TopicPage } from './pages/topic/topic.page';
import { TopicsPage } from './pages/topics/topics.page';
import { TrainingPage } from './pages/training/training.page';
import { VocabularyPage } from './pages/vocabulary/vocabulary.page';

export const routes: Routes = [
  { path: '', component: HomePage },
  { path: 'training', component: TrainingPage },
  { path: 'topics', component: TopicsPage },
  { path: 'topics/:id', component: TopicPage },
  { path: 'documents', component: DocumentsPage },
  { path: 'documents/:id', component: DocumentPage },
  { path: 'document-topic', component: DocumentTopicPage },
  { path: 'vocabulary', component: VocabularyPage },
  { path: 'export', component: ExportPage },
];
