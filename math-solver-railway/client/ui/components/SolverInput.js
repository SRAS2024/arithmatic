// ui/components/SolverInput.js - Main input component
import { Tracker } from 'meteor/tracker';
import { Meteor } from 'meteor/meteor';
import { expressionToLatex, renderLatex } from '../../lib/mathPreview';

const SAMPLE_PROBLEMS = [
  { label: 'Quadratic equation', value: 'x^2 + 5x + 6 = 0' },
  { label: 'Derivative', value: 'd/dx(x^3 + 2x^2 - 5x + 3)' },
  { label: 'Integral', value: 'int(x^2 + 3x, x)' },
  { label: 'Matrix determinant', value: 'det([[1,2],[3,4]])' },
  { label: 'Simplify expression', value: 'simplify (x^2 - 9)/(x + 3)' },
  { label: 'Solve system', value: '2x + y = 10, x - y = 2' },
  { label: 'Trigonometry', value: 'sin(pi/4) + cos(pi/3)' },
  { label: 'Limit', value: 'lim(x->0) sin(x)/x' },
  { label: 'Factor', value: 'factor x^3 - 8' },
  { label: 'Sum series', value: 'sum(1/n^2, n=1 to 100)' },
];

const INPUT_MODES = [
  { key: 'type', label: 'Type', icon: '\u2328' },
  { key: 'image', label: 'Upload Image', icon: '\uD83D\uDDBC' },
  { key: 'pdf', label: 'Upload PDF', icon: '\uD83D\uDCC4' },
  { key: 'handwritten', label: 'Handwritten', icon: '\u270D' },
];

export function createSolverInput(appState) {
  const panel = document.createElement('div');
  panel.className = 'card solver-input-panel';

  // Title
  const title = document.createElement('div');
  title.className = 'card-title';
  title.textContent = 'Input';

  // Input mode tabs
  const tabs = document.createElement('div');
  tabs.className = 'input-mode-tabs';

  INPUT_MODES.forEach(({ key, label, icon }) => {
    const tab = document.createElement('button');
    tab.className = 'input-mode-tab';
    tab.dataset.mode = key;
    tab.innerHTML = `<span class="tab-icon">${icon}</span><span class="tab-label">${label}</span>`;
    tab.addEventListener('click', () => {
      appState.inputMode.set(key);
    });
    tabs.appendChild(tab);
  });

  // Textarea
  const textareaWrapper = document.createElement('div');
  textareaWrapper.className = 'textarea-wrapper';

  const textarea = document.createElement('textarea');
  textarea.className = 'solver-textarea';
  textarea.placeholder = 'Enter a math problem... e.g. x^2 + 5x + 6 = 0';
  textarea.rows = 5;
  textarea.spellcheck = false;

  textareaWrapper.appendChild(textarea);

  // Live LaTeX preview
  const previewContainer = document.createElement('div');
  previewContainer.className = 'latex-preview';

  const previewLabel = document.createElement('div');
  previewLabel.className = 'preview-label';
  previewLabel.textContent = 'Preview';

  const previewContent = document.createElement('div');
  previewContent.className = 'preview-content';
  previewContent.innerHTML = '<span class="math-preview-placeholder">Type a math expression to see preview...</span>';

  previewContainer.appendChild(previewLabel);
  previewContainer.appendChild(previewContent);

  // Sample problems dropdown
  const samplesRow = document.createElement('div');
  samplesRow.className = 'samples-row';

  const samplesLabel = document.createElement('label');
  samplesLabel.className = 'samples-label';
  samplesLabel.textContent = 'Samples:';

  const samplesSelect = document.createElement('select');
  samplesSelect.className = 'samples-select';
  const defaultOpt = document.createElement('option');
  defaultOpt.value = '';
  defaultOpt.textContent = 'Choose a sample problem...';
  samplesSelect.appendChild(defaultOpt);

  SAMPLE_PROBLEMS.forEach(({ label, value }) => {
    const opt = document.createElement('option');
    opt.value = value;
    opt.textContent = label;
    samplesSelect.appendChild(opt);
  });

  samplesRow.appendChild(samplesLabel);
  samplesRow.appendChild(samplesSelect);

  // Solver mode selector
  const modeRow = document.createElement('div');
  modeRow.className = 'solver-mode-row';

  const modeLabel = document.createElement('span');
  modeLabel.className = 'mode-label';
  modeLabel.textContent = 'Solver:';

  const modes = ['auto', 'local', 'api'];
  const modeLabels = { auto: 'Auto', local: 'Local', api: 'API' };

  modes.forEach(mode => {
    const radio = document.createElement('label');
    radio.className = 'mode-radio';
    const input = document.createElement('input');
    input.type = 'radio';
    input.name = 'solver-mode';
    input.value = mode;
    input.checked = mode === 'auto';
    input.addEventListener('change', () => {
      appState.solverMode.set(mode);
    });
    const span = document.createElement('span');
    span.className = 'mode-radio-label';
    span.textContent = modeLabels[mode];
    radio.appendChild(input);
    radio.appendChild(span);
    modeRow.appendChild(radio);
  });

  modeRow.prepend(modeLabel);

  // Options checkboxes
  const optionsRow = document.createElement('div');
  optionsRow.className = 'options-row';

  const optionDefs = [
    { key: 'detailedSteps', label: 'Detailed steps', checked: true },
    { key: 'autoGraph', label: 'Auto-graph', checked: false },
    { key: 'crossVerify', label: 'Cross-verify', checked: false },
  ];

  optionDefs.forEach(({ key, label, checked }) => {
    const lbl = document.createElement('label');
    lbl.className = 'option-checkbox';
    const cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.checked = checked;
    cb.addEventListener('change', () => {
      const opts = appState.options.get();
      opts[key] = cb.checked;
      appState.options.set({ ...opts });
    });
    const span = document.createElement('span');
    span.className = 'option-label';
    span.textContent = label;
    lbl.appendChild(cb);
    lbl.appendChild(span);
    optionsRow.appendChild(lbl);
  });

  // Action buttons
  const actionsRow = document.createElement('div');
  actionsRow.className = 'solver-actions';

  const solveBtn = document.createElement('button');
  solveBtn.className = 'btn btn-primary btn-solve';
  solveBtn.innerHTML = '<span class="btn-text">Solve</span><span class="btn-spinner" style="display:none"></span>';

  const clearBtn = document.createElement('button');
  clearBtn.className = 'btn btn-secondary btn-clear';
  clearBtn.textContent = 'Clear';

  actionsRow.appendChild(solveBtn);
  actionsRow.appendChild(clearBtn);

  // Assemble panel
  panel.appendChild(title);
  panel.appendChild(tabs);
  panel.appendChild(textareaWrapper);
  panel.appendChild(previewContainer);
  panel.appendChild(samplesRow);
  panel.appendChild(modeRow);
  panel.appendChild(optionsRow);
  panel.appendChild(actionsRow);

  // --- Event Handlers ---

  // Textarea input -> update state + preview
  let previewTimeout = null;
  textarea.addEventListener('input', () => {
    appState.currentProblem.set(textarea.value);
    clearTimeout(previewTimeout);
    previewTimeout = setTimeout(() => {
      const latex = expressionToLatex(textarea.value);
      renderLatex(previewContent, latex, true);
    }, 200);
  });

  // Sample select
  samplesSelect.addEventListener('change', () => {
    if (samplesSelect.value) {
      textarea.value = samplesSelect.value;
      appState.currentProblem.set(samplesSelect.value);
      const latex = expressionToLatex(samplesSelect.value);
      renderLatex(previewContent, latex, true);
      samplesSelect.value = '';
    }
  });

  // Clear button
  clearBtn.addEventListener('click', () => {
    textarea.value = '';
    appState.currentProblem.set('');
    appState.solverResult.set(null);
    appState.graphData.set(null);
    appState.error.set(null);
    appState.statusMessage.set(null);
    appState.ocrResult.set(null);
    previewContent.innerHTML = '<span class="math-preview-placeholder">Type a math expression to see preview...</span>';
  });

  // Solve button
  solveBtn.addEventListener('click', () => {
    const problem = appState.currentProblem.get();
    if (!problem || !problem.trim()) return;

    const opts = appState.options.get();
    const mode = appState.solverMode.get();

    appState.isLoading.set(true);
    appState.loadingMessage.set('Solving...');
    appState.error.set(null);
    appState.solverResult.set(null);
    appState.graphData.set(null);

    solveBtn.querySelector('.btn-text').textContent = 'Solving...';
    solveBtn.querySelector('.btn-spinner').style.display = 'inline-block';
    solveBtn.disabled = true;

    Meteor.call('solve', {
      problem: problem.trim(),
      mode: mode,
      detailedSteps: opts.detailedSteps,
      crossVerify: opts.crossVerify,
    }, (err, result) => {
      appState.isLoading.set(false);
      appState.loadingMessage.set('');
      solveBtn.querySelector('.btn-text').textContent = 'Solve';
      solveBtn.querySelector('.btn-spinner').style.display = 'none';
      solveBtn.disabled = false;

      if (err) {
        appState.error.set(err.reason || err.message || 'Failed to solve');
        return;
      }

      appState.solverResult.set(result);
      appState.statusMessage.set({ type: 'success', text: 'Solved successfully!' });

      // Auto-graph if enabled and we have a graphable expression
      if (opts.autoGraph && result) {
        appState.isLoading.set(true);
        appState.loadingMessage.set('Generating graph...');

        Meteor.call('generateGraph', {
          problem: problem.trim(),
          expression: result.expression || problem.trim(),
        }, (graphErr, graphResult) => {
          appState.isLoading.set(false);
          appState.loadingMessage.set('');

          if (!graphErr && graphResult) {
            appState.graphData.set(graphResult);
          }
        });
      }
    });
  });

  // --- Reactive updates ---

  // Active tab highlight
  Tracker.autorun(() => {
    const mode = appState.inputMode.get();
    tabs.querySelectorAll('.input-mode-tab').forEach(tab => {
      tab.classList.toggle('active', tab.dataset.mode === mode);
    });
    // Show/hide textarea for type mode
    textareaWrapper.style.display = mode === 'type' ? 'block' : 'none';
    previewContainer.style.display = mode === 'type' ? 'block' : 'none';
  });

  // Sync external problem changes to textarea
  Tracker.autorun(() => {
    const problem = appState.currentProblem.get();
    if (textarea.value !== problem) {
      textarea.value = problem;
      const latex = expressionToLatex(problem);
      renderLatex(previewContent, latex, true);
    }
  });

  return panel;
}
