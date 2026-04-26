import { Routes } from '@angular/router';
import { Landing } from './pages/landing/landing';
import { Workspace } from './pages/workspace/workspace';
import { LearningPlan } from './pages/learning-plan/learning-plan';
import { InterviewPrep } from './pages/interview-prep/interview-prep';

export const routes: Routes = [
  { path: '', component: Landing },
  { path: 'workspace', component: Workspace },
  { path: 'workspace/:sessionId', component: Workspace },
  { path: 'learning-plan/:sessionId', component: LearningPlan },
  { path: 'interview-prep/:sessionId', component: InterviewPrep },
  { path: '**', redirectTo: '' }
];
