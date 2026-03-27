// ui/App.js - Main app assembly
import { Tracker } from 'meteor/tracker';
import { createMainLayout } from './layouts/MainLayout';
import { createHeader } from './components/Header';
import { createSolverInput } from './components/SolverInput';
import { createUploadPanel } from './components/UploadPanel';
import { createOCRPreview } from './components/OCRPreview';
import { createAnswerPanel } from './components/AnswerPanel';
import { createStepsPanel } from './components/StepsPanel';
import { createGraphPanel } from './components/GraphPanel';
import { createDownloadPanel } from './components/DownloadPanel';
import { createStatusBanner } from './components/StatusBanner';

let _appState = null;

export function initApp(appState) {
  _appState = appState;

  const appRoot = document.getElementById('app');
  if (!appRoot) {
    console.error('Arithmetic: #app element not found');
    return;
  }

  // Clear the root
  appRoot.innerHTML = '';

  // Create components
  const header = createHeader(appState);
  const solverInput = createSolverInput(appState);
  const uploadPanel = createUploadPanel(appState);
  const ocrPreview = createOCRPreview(appState);
  const answerPanel = createAnswerPanel(appState);
  const stepsPanel = createStepsPanel(appState);
  const graphPanel = createGraphPanel(appState);
  const downloadPanel = createDownloadPanel(appState);
  const statusBanner = createStatusBanner(appState);

  // Assemble left column
  const leftColumn = document.createElement('div');
  leftColumn.className = 'layout-left';
  leftColumn.appendChild(solverInput);
  leftColumn.appendChild(uploadPanel);

  // Assemble right column
  const rightColumn = document.createElement('div');
  rightColumn.className = 'layout-right';
  rightColumn.appendChild(statusBanner);
  rightColumn.appendChild(answerPanel);
  rightColumn.appendChild(stepsPanel);
  rightColumn.appendChild(ocrPreview);
  rightColumn.appendChild(graphPanel);
  rightColumn.appendChild(downloadPanel);

  // Create the main layout
  const layout = createMainLayout(header, leftColumn, rightColumn);

  appRoot.appendChild(layout);

  // Set up reactive visibility for panels
  Tracker.autorun(() => {
    const result = appState.solverResult.get();
    const hasResult = result && (result.answer || result.steps || result.latex);
    answerPanel.style.display = hasResult ? 'block' : 'none';
    stepsPanel.style.display = (hasResult && result.steps && result.steps.length > 0) ? 'block' : 'none';
    downloadPanel.style.display = hasResult ? 'block' : 'none';
  });

  Tracker.autorun(() => {
    const ocr = appState.ocrResult.get();
    ocrPreview.style.display = ocr ? 'block' : 'none';
  });

  Tracker.autorun(() => {
    const graph = appState.graphData.get();
    graphPanel.style.display = graph ? 'block' : 'none';
  });

  Tracker.autorun(() => {
    const loading = appState.isLoading.get();
    const error = appState.error.get();
    const status = appState.statusMessage.get();
    statusBanner.style.display = (loading || error || status) ? 'block' : 'none';
  });

  Tracker.autorun(() => {
    const mode = appState.inputMode.get();
    uploadPanel.style.display = (mode === 'image' || mode === 'pdf' || mode === 'handwritten') ? 'block' : 'none';
  });
}

export function getAppState() {
  return _appState;
}
