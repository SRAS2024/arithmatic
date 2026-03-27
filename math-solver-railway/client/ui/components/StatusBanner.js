// ui/components/StatusBanner.js - Status and progress display
import { Tracker } from 'meteor/tracker';

export function createStatusBanner(appState) {
  const banner = document.createElement('div');
  banner.className = 'status-banner';
  banner.style.display = 'none';

  const content = document.createElement('div');
  content.className = 'status-content';

  const iconEl = document.createElement('div');
  iconEl.className = 'status-icon';

  const textEl = document.createElement('div');
  textEl.className = 'status-text';

  const dismissBtn = document.createElement('button');
  dismissBtn.className = 'status-dismiss';
  dismissBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`;

  content.appendChild(iconEl);
  content.appendChild(textEl);
  content.appendChild(dismissBtn);

  // Progress bar
  const progressBar = document.createElement('div');
  progressBar.className = 'status-progress-bar';

  const progressFill = document.createElement('div');
  progressFill.className = 'status-progress-fill';

  progressBar.appendChild(progressFill);

  // Retry button (for errors)
  const retryBtn = document.createElement('button');
  retryBtn.className = 'btn btn-secondary btn-retry';
  retryBtn.textContent = 'Retry';
  retryBtn.style.display = 'none';

  banner.appendChild(content);
  banner.appendChild(progressBar);
  banner.appendChild(retryBtn);

  // --- Events ---

  dismissBtn.addEventListener('click', () => {
    appState.error.set(null);
    appState.statusMessage.set(null);
    appState.isLoading.set(false);
    appState.loadingMessage.set('');
  });

  retryBtn.addEventListener('click', () => {
    appState.error.set(null);
    // Re-trigger solve with current problem
    const problem = appState.currentProblem.get();
    if (problem) {
      const solveBtn = document.querySelector('.btn-solve');
      if (solveBtn) solveBtn.click();
    }
  });

  // Auto-dismiss success messages
  let successTimeout = null;

  // --- Reactive updates ---

  Tracker.autorun(() => {
    const isLoading = appState.isLoading.get();
    const loadingMsg = appState.loadingMessage.get();
    const error = appState.error.get();
    const status = appState.statusMessage.get();

    clearTimeout(successTimeout);

    if (isLoading) {
      banner.className = 'status-banner status-loading';
      iconEl.innerHTML = '<div class="status-spinner"></div>';
      textEl.textContent = loadingMsg || 'Processing...';
      progressBar.style.display = 'block';
      progressFill.style.animation = 'progressIndeterminate 1.5s ease-in-out infinite';
      retryBtn.style.display = 'none';
      dismissBtn.style.display = 'none';
    } else if (error) {
      banner.className = 'status-banner status-error';
      iconEl.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`;
      textEl.textContent = typeof error === 'string' ? error : (error.message || 'An error occurred');
      progressBar.style.display = 'none';
      retryBtn.style.display = 'inline-flex';
      dismissBtn.style.display = 'flex';
    } else if (status) {
      const type = (typeof status === 'object') ? status.type : 'success';
      const text = (typeof status === 'object') ? status.text : status;
      banner.className = `status-banner status-${type}`;

      if (type === 'success') {
        iconEl.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`;
      } else {
        iconEl.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;
      }

      textEl.textContent = text;
      progressBar.style.display = 'none';
      retryBtn.style.display = 'none';
      dismissBtn.style.display = 'flex';

      // Auto-dismiss success after 4s
      if (type === 'success') {
        successTimeout = setTimeout(() => {
          appState.statusMessage.set(null);
        }, 4000);
      }
    }
  });

  return banner;
}
