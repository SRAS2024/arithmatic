// lib/mathPreview.js - Live math preview using KaTeX

/**
 * Attempt to convert a plain math expression into LaTeX.
 * Handles common patterns like x^2, sqrt(), fractions, etc.
 */
export function expressionToLatex(input) {
  if (!input || !input.trim()) return '';

  let expr = input.trim();

  // If it already looks like LaTeX (contains backslashes), return as-is
  if (expr.includes('\\')) return expr;

  // Replace common patterns
  expr = expr
    // Fractions: a/b -> \frac{a}{b} (simple single-char or parenthesized)
    .replace(/\(([^)]+)\)\/\(([^)]+)\)/g, '\\frac{$1}{$2}')
    // sqrt
    .replace(/sqrt\(([^)]+)\)/gi, '\\sqrt{$1}')
    // cbrt
    .replace(/cbrt\(([^)]+)\)/gi, '\\sqrt[3]{$1}')
    // Powers: x^2 -> x^{2}, x^(2+1) -> x^{2+1}
    .replace(/\^(\([^)]+\))/g, (_, p) => `^{${p.slice(1, -1)}}`)
    .replace(/\^(\d+)/g, '^{$1}')
    // pi
    .replace(/\bpi\b/gi, '\\pi')
    // theta
    .replace(/\btheta\b/gi, '\\theta')
    // infinity
    .replace(/\binfinity\b/gi, '\\infty')
    .replace(/\binf\b/gi, '\\infty')
    // Trig functions
    .replace(/\bsin\b/g, '\\sin')
    .replace(/\bcos\b/g, '\\cos')
    .replace(/\btan\b/g, '\\tan')
    .replace(/\bsec\b/g, '\\sec')
    .replace(/\bcsc\b/g, '\\csc')
    .replace(/\bcot\b/g, '\\cot')
    .replace(/\bln\b/g, '\\ln')
    .replace(/\blog\b/g, '\\log')
    .replace(/\blim\b/g, '\\lim')
    // Integral and sum
    .replace(/\bint\b/g, '\\int')
    .replace(/\bsum\b/g, '\\sum')
    .replace(/\bprod\b/g, '\\prod')
    // Multiplication dot
    .replace(/\*/g, '\\cdot ')
    // >= and <=
    .replace(/>=/g, '\\geq ')
    .replace(/<=/g, '\\leq ')
    .replace(/!=/g, '\\neq ')
    // Plus-minus
    .replace(/\+-/g, '\\pm ')
    // Arrows
    .replace(/->/g, '\\rightarrow ')
    .replace(/<-/g, '\\leftarrow ');

  return expr;
}

/**
 * Render LaTeX into a DOM element using KaTeX.
 * Returns true if successful, false otherwise.
 */
export function renderLatex(element, latex, displayMode = true) {
  if (!element) return false;
  if (!latex || !latex.trim()) {
    element.innerHTML = '<span class="math-preview-placeholder">Type a math expression to see preview...</span>';
    return true;
  }

  try {
    if (typeof katex !== 'undefined') {
      katex.render(latex, element, {
        displayMode: displayMode,
        throwOnError: false,
        errorColor: '#ef4444',
        trust: true,
        strict: false,
      });
      return true;
    } else {
      element.textContent = latex;
      return false;
    }
  } catch (err) {
    element.innerHTML = `<span class="math-preview-error">${escapeHtml(latex)}</span>`;
    return false;
  }
}

/**
 * Render LaTeX inline within text. Processes $...$ and $$...$$ delimiters.
 */
export function renderMixedContent(element, text) {
  if (!element || !text) return;

  const parts = [];
  let remaining = text;

  // Process $$...$$ (display math) and $...$ (inline math)
  const regex = /\$\$([\s\S]*?)\$\$|\$([\s\S]*?)\$/g;
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(remaining)) !== null) {
    // Text before the match
    if (match.index > lastIndex) {
      const span = document.createElement('span');
      span.textContent = remaining.slice(lastIndex, match.index);
      parts.push(span);
    }

    const mathSpan = document.createElement('span');
    const isDisplay = match[1] !== undefined;
    const latex = isDisplay ? match[1] : match[2];

    renderLatex(mathSpan, latex, isDisplay);
    parts.push(mathSpan);

    lastIndex = match.index + match[0].length;
  }

  // Remaining text
  if (lastIndex < remaining.length) {
    const span = document.createElement('span');
    span.textContent = remaining.slice(lastIndex);
    parts.push(span);
  }

  element.innerHTML = '';
  parts.forEach(p => element.appendChild(p));
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
