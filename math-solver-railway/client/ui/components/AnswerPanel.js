// ui/components/AnswerPanel.js - Final answer display
import { Tracker } from 'meteor/tracker';
import { renderLatex } from '../../lib/mathPreview';
import { formatAnswer } from '../../lib/formatters';

export function createAnswerPanel(appState) {
  const panel = document.createElement('div');
  panel.className = 'card answer-panel';
  panel.style.display = 'none';

  const titleRow = document.createElement('div');
  titleRow.className = 'answer-title-row';

  const title = document.createElement('div');
  title.className = 'card-title';
  title.textContent = 'Answer';

  const badges = document.createElement('div');
  badges.className = 'answer-badges';

  const confidenceBadge = document.createElement('span');
  confidenceBadge.className = 'answer-badge confidence-badge';

  const sourceBadge = document.createElement('span');
  sourceBadge.className = 'answer-badge source-badge';

  badges.appendChild(confidenceBadge);
  badges.appendChild(sourceBadge);

  titleRow.appendChild(title);
  titleRow.appendChild(badges);

  // Main answer display
  const mainAnswer = document.createElement('div');
  mainAnswer.className = 'answer-main';

  const answerKatex = document.createElement('div');
  answerKatex.className = 'answer-katex';

  mainAnswer.appendChild(answerKatex);

  // Sub-answers: simplified, decimal, exact
  const subAnswers = document.createElement('div');
  subAnswers.className = 'answer-sub-grid';

  const simplifiedSection = createSubAnswer('Simplified');
  const decimalSection = createSubAnswer('Decimal Approximation');
  const exactSection = createSubAnswer('Exact Form');

  subAnswers.appendChild(simplifiedSection.container);
  subAnswers.appendChild(decimalSection.container);
  subAnswers.appendChild(exactSection.container);

  // Copy button
  const copyBtn = document.createElement('button');
  copyBtn.className = 'btn btn-secondary btn-copy-answer';
  copyBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
    <span>Copy answer</span>`;

  // Assemble
  panel.appendChild(titleRow);
  panel.appendChild(mainAnswer);
  panel.appendChild(subAnswers);
  panel.appendChild(copyBtn);

  // --- Events ---

  copyBtn.addEventListener('click', () => {
    const result = appState.solverResult.get();
    if (!result) return;

    const text = formatAnswer(result);
    navigator.clipboard.writeText(text).then(() => {
      const span = copyBtn.querySelector('span');
      const original = span.textContent;
      span.textContent = 'Copied!';
      setTimeout(() => { span.textContent = original; }, 1500);
    }).catch(() => {
      // Fallback
      const ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    });
  });

  // --- Reactive updates ---

  Tracker.autorun(() => {
    const result = appState.solverResult.get();
    if (!result) return;

    // Main answer with KaTeX
    const latex = result.latex || result.answer || '';
    if (latex) {
      renderLatex(answerKatex, latex, true);
    } else {
      answerKatex.textContent = result.answer || 'No answer';
    }

    // Sub-answers
    simplifiedSection.setValue(result.simplified || result.answer || '');
    decimalSection.setValue(result.decimal || result.approximation || '');
    exactSection.setValue(result.exact || result.answer || '');

    // Badges
    if (result.confidence !== undefined) {
      const pct = Math.round((result.confidence || 0) * 100);
      confidenceBadge.textContent = `${pct}% confident`;
      confidenceBadge.style.display = 'inline-flex';
      if (pct >= 80) {
        confidenceBadge.className = 'answer-badge confidence-badge high';
      } else if (pct >= 50) {
        confidenceBadge.className = 'answer-badge confidence-badge medium';
      } else {
        confidenceBadge.className = 'answer-badge confidence-badge low';
      }
    } else {
      confidenceBadge.style.display = 'none';
    }

    if (result.source || result.method) {
      sourceBadge.textContent = result.source || result.method || '';
      sourceBadge.style.display = 'inline-flex';
    } else {
      sourceBadge.style.display = 'none';
    }
  });

  return panel;
}

function createSubAnswer(label) {
  const container = document.createElement('div');
  container.className = 'answer-sub-item';

  const labelEl = document.createElement('div');
  labelEl.className = 'answer-sub-label';
  labelEl.textContent = label;

  const valueEl = document.createElement('div');
  valueEl.className = 'answer-sub-value';
  valueEl.textContent = '\u2014';

  container.appendChild(labelEl);
  container.appendChild(valueEl);

  return {
    container,
    setValue(val) {
      if (val) {
        // Try rendering as LaTeX
        try {
          if (typeof katex !== 'undefined' && val.includes('\\')) {
            renderLatex(valueEl, val, false);
          } else {
            valueEl.textContent = val;
          }
        } catch {
          valueEl.textContent = val;
        }
      } else {
        valueEl.textContent = '\u2014';
      }
    }
  };
}
