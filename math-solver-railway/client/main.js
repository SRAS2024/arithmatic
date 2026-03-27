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
  theme: new ReactiveVar(localStorage.getItem('arithmetic-theme') || 'light'),
  inputMode: new ReactiveVar('type'),        // 'type' | 'image' | 'pdf' | 'handwritten'
  currentProblem: new ReactiveVar(''),
  solverResult: new ReactiveVar(null),
  isLoading: new ReactiveVar(false),
  loadingMessage: new ReactiveVar(''),
  ocrResult: new ReactiveVar(null),
  graphData: new ReactiveVar(null),
  uploadedFile: new ReactiveVar(null),
  solverMode: new ReactiveVar('auto'),        // 'auto' | 'local' | 'api'
  options: new ReactiveVar({
    detailedSteps: true,
    autoGraph: false,
    crossVerify: false,
  }),
  error: new ReactiveVar(null),
  statusMessage: new ReactiveVar(null),
};

// Initialize the application when DOM is ready
Meteor.startup(() => {
  initTheme(AppState);
  initRouter();
  initApp(AppState);
});
