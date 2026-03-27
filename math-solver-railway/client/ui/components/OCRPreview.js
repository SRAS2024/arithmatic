// ui/components/OCRPreview.js - OCR extracted text display
import { Tracker } from 'meteor/tracker';
import { Meteor } from 'meteor/meteor';
import { formatConfidence } from '../../lib/formatters';

export function createOCRPreview(appState) {
  const panel = document.createElement('div');
  panel.className = 'card ocr-preview-panel';
  panel.style.display = 'none';

  const title = document.createElement('div');
  title.className = 'card-title';
  title.textContent = 'OCR Result';

  // Confidence badge
  const confidenceBadge = document.createElement('div');
  confidenceBadge.className = 'ocr-confidence';

  // Raw text section
  const rawSection = document.createElement('div');
  rawSection.className = 'ocr-section';

  const rawLabel = document.createElement('div');
  rawLabel.className = 'ocr-section-label';
  rawLabel.textContent = 'Raw Extracted Text';

  const rawText = document.createElement('pre');
  rawText.className = 'ocr-raw-text';

  rawSection.appendChild(rawLabel);
  rawSection.appendChild(rawText);

  // Normalized section
  const normSection = document.createElement('div');
  normSection.className = 'ocr-section';

  const normLabel = document.createElement('div');
  normLabel.className = 'ocr-section-label';
  normLabel.textContent = 'Normalized Expression';

  const normText = document.createElement('div');
  normText.className = 'ocr-norm-text';

  normSection.appendChild(normLabel);
  normSection.appendChild(normText);

  // Actions
  const actions = document.createElement('div');
  actions.className = 'ocr-actions';

  const useBtn = document.createElement('button');
  useBtn.className = 'btn btn-primary';
  useBtn.textContent = 'Use this text';

  const reExtractBtn = document.createElement('button');
  reExtractBtn.className = 'btn btn-secondary';
  reExtractBtn.textContent = 'Re-extract';

  actions.appendChild(useBtn);
  actions.appendChild(reExtractBtn);

  // Assemble
  panel.appendChild(title);
  panel.appendChild(confidenceBadge);
  panel.appendChild(rawSection);
  panel.appendChild(normSection);
  panel.appendChild(actions);

  // --- Event Handlers ---

  useBtn.addEventListener('click', () => {
    const ocr = appState.ocrResult.get();
    if (ocr) {
      const textToUse = ocr.normalized || ocr.raw || ocr.text || '';
      appState.currentProblem.set(textToUse);
      appState.inputMode.set('type');
    }
  });

  reExtractBtn.addEventListener('click', () => {
    const uploadedFile = appState.uploadedFile.get();
    if (!uploadedFile) {
      appState.error.set('No file uploaded to re-extract from');
      return;
    }

    appState.isLoading.set(true);
    appState.loadingMessage.set('Re-extracting text...');
    appState.error.set(null);

    Meteor.call('upload', {
      fileName: uploadedFile.name,
      fileType: uploadedFile.type,
      fileData: uploadedFile.data,
    }, (err, result) => {
      appState.isLoading.set(false);
      appState.loadingMessage.set('');

      if (err) {
        appState.error.set(err.reason || err.message || 'Failed to re-extract text');
        return;
      }

      if (result) {
        appState.ocrResult.set(result);
      }
    });
  });

  // --- Reactive updates ---

  Tracker.autorun(() => {
    const ocr = appState.ocrResult.get();
    if (!ocr) return;

    rawText.textContent = ocr.raw || ocr.text || '';
    normText.textContent = ocr.normalized || ocr.expression || ocr.raw || ocr.text || '';

    const confidence = ocr.confidence || 0;
    const conf = formatConfidence(confidence);
    confidenceBadge.className = `ocr-confidence confidence-${conf.level}`;
    confidenceBadge.textContent = `${conf.label} confidence (${Math.round(confidence * 100)}%)`;
  });

  return panel;
}
