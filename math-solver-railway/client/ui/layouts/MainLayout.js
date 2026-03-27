// MainLayout.js - Assembles the full page layout
import { initHeader } from '../components/Header.js';
import { initSolverInput } from '../components/SolverInput.js';
import { initUploadPanel } from '../components/UploadPanel.js';
import { initOCRPreview } from '../components/OCRPreview.js';
import { initAnswerPanel } from '../components/AnswerPanel.js';
import { initStepsPanel } from '../components/StepsPanel.js';
import { initGraphPanel } from '../components/GraphPanel.js';
import { initDownloadPanel } from '../components/DownloadPanel.js';
import { initStatusBanner } from '../components/StatusBanner.js';

export function initMainLayout(container, state) {
  // Create layout structure
  const layout = document.createElement('div');
  layout.className = 'main-layout';
  layout.innerHTML = `
    <div class="layout-header" id="layout-header"></div>
    <div class="layout-body">
      <div class="layout-sidebar" id="layout-sidebar">
        <div id="solver-input-container"></div>
        <div id="upload-panel-container"></div>
      </div>
      <div class="layout-main" id="layout-main">
        <div id="status-banner-container"></div>
        <div id="answer-panel-container"></div>
        <div id="steps-panel-container"></div>
        <div id="ocr-preview-container"></div>
        <div id="graph-panel-container"></div>
        <div id="download-panel-container"></div>
      </div>
    </div>
  `;
  container.appendChild(layout);

  // Initialize all components
  initHeader(document.getElementById('layout-header'), state);
  initSolverInput(document.getElementById('solver-input-container'), state);
  initUploadPanel(document.getElementById('upload-panel-container'), state);
  initStatusBanner(document.getElementById('status-banner-container'), state);
  initAnswerPanel(document.getElementById('answer-panel-container'), state);
  initStepsPanel(document.getElementById('steps-panel-container'), state);
  initOCRPreview(document.getElementById('ocr-preview-container'), state);
  initGraphPanel(document.getElementById('graph-panel-container'), state);
  initDownloadPanel(document.getElementById('download-panel-container'), state);
}
