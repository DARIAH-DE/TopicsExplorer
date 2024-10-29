import { Routes } from '@angular/router';
import { modelGuard } from './guards/model.guard';
import { DocumentComponent, DocumentsComponent, SettingsComponent, TopicComponent, TopicsComponent } from './pages';

export const routes: Routes = [
  { path: '', component: SettingsComponent },
  { path: 'topics', component: TopicsComponent, canActivate: [modelGuard] },
  { path: 'topics/:id', component: TopicComponent, canActivate: [modelGuard] },
  { path: 'documents', component: DocumentsComponent, canActivate: [modelGuard] },
  { path: 'documents/:id', component: DocumentComponent, canActivate: [modelGuard] },
];
