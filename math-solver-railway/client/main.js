// main.js - Entry point for the Arithmetic client application
import './main.css';
import './ui/App.css';
import './ui/components/Header.css';
import './ui/components/ThemeToggle.css';
import './ui/components/SolverInput.css';
import './ui/components/UploadPanel.css';
import './ui/components/OCRPreview.css';
import './ui/components/AnswerPanel.css';
import './ui/components/StepsPanel.css';
import './ui/components/GraphPanel.css';
import './ui/components/DownloadPanel.css';
import './ui/components/StatusBanner.css';
import './ui/layouts/MainLayout.css';

import { ReactiveVar } from 'meteor/reactive-var';
import { Tracker } from 'meteor/tracker';

import { initTheme } from './lib/theme';
import { initApp } from './ui/App';
import { initRouter } from './routes/index';

// Global application state using ReactiveVar
export const AppState = {
  theme: new ReactiveVar(localStorage.getItem('arithmetic-theme') || 'dark'),
  inputMode: new ReactiveVar('type'),        // 'type' | 'handwrite'
  currentProblem: new ReactiveVar(''),
  solverResult: new ReactiveVar(null),
  isLoading: new ReactiveVar(false),
  loadingMessage: new ReactiveVar(''),
  ocrResult: new ReactiveVar(null),
  graphData: new ReactiveVar(null),
  uploadedFile: new ReactiveVar(null),
  solverMode: new ReactiveVar('auto'),
  options: new ReactiveVar({
    detailedSteps: true,
    autoGraph: true,
    crossVerify: false,
  }),
  error: new ReactiveVar(null),
  statusMessage: new ReactiveVar(null),

  // Chat state
  chatMessages: new ReactiveVar([]),   // Array of { id, role, problem, answer, steps, graph, latex, confidence, sourceType, problemType, timestamp }
  sidebarOpen: new ReactiveVar(false),
  handwriteMode: new ReactiveVar(false),
};

// Initialize the application when DOM is ready
Meteor.startup(() => {
  initTheme(AppState);
  initRouter();
  initApp(AppState);
});
