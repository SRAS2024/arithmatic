// ui/components/UploadPanel.js - File upload component
import { Tracker } from 'meteor/tracker';
import { Meteor } from 'meteor/meteor';
import { formatFileSize } from '../../lib/formatters';

const ACCEPTED_TYPES = {
  'image/png': '.png',
  'image/jpeg': '.jpg',
  'image/gif': '.gif',
  'image/bmp': '.bmp',
  'application/pdf': '.pdf',
};

const ACCEPT_STRING = Object.values(ACCEPTED_TYPES).join(',');

export function createUploadPanel(appState) {
  const panel = document.createElement('div');
  panel.className = 'card upload-panel';
  panel.style.display = 'none';

  const title = document.createElement('div');
  title.className = 'card-title';
  title.textContent = 'Upload';

  // Drop zone
  const dropZone = document.createElement('div');
  dropZone.className = 'drop-zone';

  const dropIcon = document.createElement('div');
  dropIcon.className = 'drop-zone-icon';
  dropIcon.innerHTML = `<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
    <polyline points="17 8 12 3 7 8"></polyline>
    <line x1="12" y1="3" x2="12" y2="15"></line>
  </svg>`;

  const dropText = document.createElement('div');
  dropText.className = 'drop-zone-text';
  dropText.innerHTML = '<strong>Drag & drop</strong> your file here, or <span class="drop-browse">click to browse</span>';

  const dropHint = document.createElement('div');
  dropHint.className = 'drop-zone-hint';
  dropHint.textContent = 'Supports PNG, JPG, GIF, BMP, PDF';

  dropZone.appendChild(dropIcon);
  dropZone.appendChild(dropText);
  dropZone.appendChild(dropHint);

  // Hidden file input
  const fileInput = document.createElement('input');
  fileInput.type = 'file';
  fileInput.accept = ACCEPT_STRING;
  fileInput.style.display = 'none';

  // Preview area
  const previewArea = document.createElement('div');
  previewArea.className = 'upload-preview-area';
  previewArea.style.display = 'none';

  const previewImage = document.createElement('img');
  previewImage.className = 'upload-preview-image';

  const pdfPreview = document.createElement('div');
  pdfPreview.className = 'upload-pdf-preview';
  pdfPreview.innerHTML = `<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
    <span class="pdf-label">PDF Document</span>`;

  previewArea.appendChild(previewImage);
  previewArea.appendChild(pdfPreview);

  // File info
  const fileInfo = document.createElement('div');
  fileInfo.className = 'upload-file-info';
  fileInfo.style.display = 'none';

  const fileInfoName = document.createElement('div');
  fileInfoName.className = 'file-info-name';

  const fileInfoDetails = document.createElement('div');
  fileInfoDetails.className = 'file-info-details';

  fileInfo.appendChild(fileInfoName);
  fileInfo.appendChild(fileInfoDetails);

  // Progress bar
  const progressBar = document.createElement('div');
  progressBar.className = 'upload-progress';
  progressBar.style.display = 'none';

  const progressFill = document.createElement('div');
  progressFill.className = 'upload-progress-fill';

  const progressText = document.createElement('div');
  progressText.className = 'upload-progress-text';
  progressText.textContent = '0%';

  progressBar.appendChild(progressFill);
  progressBar.appendChild(progressText);

  // Action buttons
  const uploadActions = document.createElement('div');
  uploadActions.className = 'upload-actions';
  uploadActions.style.display = 'none';

  const extractBtn = document.createElement('button');
  extractBtn.className = 'btn btn-primary';
  extractBtn.textContent = 'Extract Text';

  const clearUploadBtn = document.createElement('button');
  clearUploadBtn.className = 'btn btn-secondary';
  clearUploadBtn.textContent = 'Clear';

  uploadActions.appendChild(extractBtn);
  uploadActions.appendChild(clearUploadBtn);

  // Assemble
  panel.appendChild(title);
  panel.appendChild(dropZone);
  panel.appendChild(fileInput);
  panel.appendChild(previewArea);
  panel.appendChild(fileInfo);
  panel.appendChild(progressBar);
  panel.appendChild(uploadActions);

  // --- State ---
  let currentFileData = null;

  // --- Helpers ---
  function handleFile(file) {
    if (!file) return;

    // Validate type
    if (!ACCEPTED_TYPES[file.type]) {
      appState.error.set('Unsupported file type. Please upload PNG, JPG, GIF, BMP, or PDF.');
      return;
    }

    // Show file info
    fileInfoName.textContent = file.name;
    fileInfoDetails.textContent = `${formatFileSize(file.size)} \u2022 ${file.type}`;
    fileInfo.style.display = 'block';

    // Read as base64
    const reader = new FileReader();

    reader.onprogress = (e) => {
      if (e.lengthComputable) {
        const pct = Math.round((e.loaded / e.total) * 100);
        progressBar.style.display = 'block';
        progressFill.style.width = `${pct}%`;
        progressText.textContent = `${pct}%`;
      }
    };

    reader.onload = () => {
      progressBar.style.display = 'none';
      const base64 = reader.result;
      currentFileData = {
        name: file.name,
        type: file.type,
        size: file.size,
        data: base64,
      };

      appState.uploadedFile.set(currentFileData);

      // Show preview
      previewArea.style.display = 'flex';
      if (file.type.startsWith('image/')) {
        previewImage.src = base64;
        previewImage.style.display = 'block';
        pdfPreview.style.display = 'none';
      } else {
        previewImage.style.display = 'none';
        pdfPreview.style.display = 'flex';
        pdfPreview.querySelector('.pdf-label').textContent = file.name;
      }

      dropZone.style.display = 'none';
      uploadActions.style.display = 'flex';
    };

    reader.onerror = () => {
      progressBar.style.display = 'none';
      appState.error.set('Failed to read file');
    };

    reader.readAsDataURL(file);
  }

  function clearUpload() {
    currentFileData = null;
    appState.uploadedFile.set(null);
    fileInput.value = '';
    previewArea.style.display = 'none';
    fileInfo.style.display = 'none';
    uploadActions.style.display = 'none';
    progressBar.style.display = 'none';
    dropZone.style.display = 'flex';
    previewImage.src = '';
  }

  // --- Event Handlers ---

  // Click to browse
  dropZone.addEventListener('click', () => fileInput.click());

  fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  });

  // Drag & drop
  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.add('drag-over');
  });

  dropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('drag-over');
  });

  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('drag-over');
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  });

  // Extract text
  extractBtn.addEventListener('click', () => {
    if (!currentFileData) return;

    appState.isLoading.set(true);
    appState.loadingMessage.set('Extracting text...');
    appState.error.set(null);
    extractBtn.disabled = true;
    extractBtn.textContent = 'Extracting...';

    Meteor.call('upload', {
      fileName: currentFileData.name,
      fileType: currentFileData.type,
      fileData: currentFileData.data,
    }, (err, result) => {
      appState.isLoading.set(false);
      appState.loadingMessage.set('');
      extractBtn.disabled = false;
      extractBtn.textContent = 'Extract Text';

      if (err) {
        appState.error.set(err.reason || err.message || 'Failed to extract text');
        return;
      }

      if (result) {
        appState.ocrResult.set(result);
        appState.statusMessage.set({ type: 'success', text: 'Text extracted successfully!' });
      }
    });
  });

  // Clear
  clearUploadBtn.addEventListener('click', clearUpload);

  return panel;
}
