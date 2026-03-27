// ui/components/StepsPanel.js - Step-by-step solution display
import { Tracker } from 'meteor/tracker';
import { renderMixedContent, renderLatex } from '../../lib/mathPreview';

export function createStepsPanel(appState) {
  const panel = document.createElement('div');
  panel.className = 'card steps-panel';
  panel.style.display = 'none';

  const titleRow = document.createElement('div');
  titleRow.className = 'steps-title-row';

  const title = document.createElement('div');
  title.className = 'card-title';
  title.textContent = 'Step-by-Step Solution';

  const titleActions = document.createElement('div');
  titleActions.className = 'steps-title-actions';

  const expandAllBtn = document.createElement('button');
  expandAllBtn.className = 'btn-text-action';
  expandAllBtn.textContent = 'Expand all';

  const copyStepsBtn = document.createElement('button');
  copyStepsBtn.className = 'btn-text-action';
  copyStepsBtn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg> Copy`;

  titleActions.appendChild(expandAllBtn);
  titleActions.appendChild(copyStepsBtn);
  titleRow.appendChild(title);
  titleRow.appendChild(titleActions);

  // Steps container
  const stepsContainer = document.createElement('div');
  stepsContainer.className = 'steps-list';

  // Assemble
  panel.appendChild(titleRow);
  panel.appendChild(stepsContainer);

  // Track expand state
  let allExpanded = false;

  // --- Events ---

  expandAllBtn.addEventListener('click', () => {
    allExpanded = !allExpanded;
    expandAllBtn.textContent = allExpanded ? 'Collapse all' : 'Expand all';
    const details = stepsContainer.querySelectorAll('.step-card-details');
    details.forEach(d => {
      d.style.display = allExpanded ? 'block' : 'none';
    });
    const arrows = stepsContainer.querySelectorAll('.step-toggle-arrow');
    arrows.forEach(a => {
      a.classList.toggle('expanded', allExpanded);
    });
  });

  copyStepsBtn.addEventListener('click', () => {
    const result = appState.solverResult.get();
    if (!result || !result.steps) return;

    const text = result.steps.map((step, i) => {
      const num = i + 1;
      const title = step.title || step.description || `Step ${num}`;
      const math = step.math || step.expression || '';
      const explanation = step.explanation || '';
      return `Step ${num}: ${title}\n${math}\n${explanation}`;
    }).join('\n\n');

    navigator.clipboard.writeText(text).then(() => {
      copyStepsBtn.textContent = 'Copied!';
      setTimeout(() => { copyStepsBtn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg> Copy`; }, 1500);
    });
  });

  // --- Reactive updates ---

  Tracker.autorun(() => {
    const result = appState.solverResult.get();
    stepsContainer.innerHTML = '';

    if (!result || !result.steps || result.steps.length === 0) return;

    result.steps.forEach((step, index) => {
      const stepCard = document.createElement('div');
      stepCard.className = 'step-card';

      // Step header
      const stepHeader = document.createElement('div');
      stepHeader.className = 'step-header';

      const stepNumber = document.createElement('div');
      stepNumber.className = 'step-number';
      stepNumber.textContent = index + 1;

      const stepTitle = document.createElement('div');
      stepTitle.className = 'step-title';
      stepTitle.textContent = step.title || step.description || `Step ${index + 1}`;

      const toggleArrow = document.createElement('span');
      toggleArrow.className = 'step-toggle-arrow';
      toggleArrow.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>`;

      stepHeader.appendChild(stepNumber);
      stepHeader.appendChild(stepTitle);
      stepHeader.appendChild(toggleArrow);

      // Step details (collapsible)
      const stepDetails = document.createElement('div');
      stepDetails.className = 'step-card-details';
      stepDetails.style.display = allExpanded ? 'block' : 'block'; // Show by default

      // Math content
      if (step.math || step.expression || step.latex) {
        const mathEl = document.createElement('div');
        mathEl.className = 'step-math';
        const latexStr = step.latex || step.math || step.expression || '';
        renderLatex(mathEl, latexStr, true);
        stepDetails.appendChild(mathEl);
      }

      // Explanation text
      if (step.explanation || step.text) {
        const explanation = document.createElement('div');
        explanation.className = 'step-explanation';
        const explText = step.explanation || step.text || '';
        // Check if text contains math delimiters
        if (explText.includes('$')) {
          renderMixedContent(explanation, explText);
        } else {
          explanation.textContent = explText;
        }
        stepDetails.appendChild(explanation);
      }

      // Toggle expand/collapse
      stepHeader.addEventListener('click', () => {
        const isVisible = stepDetails.style.display !== 'none';
        stepDetails.style.display = isVisible ? 'none' : 'block';
        toggleArrow.classList.toggle('expanded', !isVisible);
      });

      stepCard.appendChild(stepHeader);
      stepCard.appendChild(stepDetails);
      stepsContainer.appendChild(stepCard);
    });
  });

  return panel;
}
