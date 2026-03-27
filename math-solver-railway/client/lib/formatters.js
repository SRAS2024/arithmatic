// formatters.js - Output formatting utilities
export const Formatters = {
  formatAnswer(result) {
    if (!result) return 'No answer available';
    if (typeof result === 'string') return result;
    if (result.answer) return result.answer;
    if (result.result) return String(result.result);
    return JSON.stringify(result);
  },

  formatSteps(steps) {
    if (!steps) return [];
    if (typeof steps === 'string') return steps.split('\n').filter(s => s.trim());
    if (Array.isArray(steps)) return steps;
    return [];
  },

  formatConfidence(confidence) {
    if (!confidence) return { level: 'unknown', text: 'Confidence not available', className: 'confidence-unknown' };
    const c = typeof confidence === 'string' ? confidence.toLowerCase() : '';
    if (c === 'high' || (typeof confidence === 'number' && confidence >= 0.8))
      return { level: 'high', text: 'High confidence', className: 'confidence-high' };
    if (c === 'medium' || (typeof confidence === 'number' && confidence >= 0.5))
      return { level: 'medium', text: 'Medium confidence', className: 'confidence-medium' };
    return { level: 'low', text: 'Low confidence - verify result', className: 'confidence-low' };
  },

  formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  },

  formatTimestamp(date) {
    const d = date || new Date();
    return d.toLocaleString('en-US', {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
  },

  formatLatex(text) {
    if (!text) return '';
    return text
      .replace(/\*\*/g, '^')
      .replace(/sqrt\(([^)]+)\)/g, '\\sqrt{$1}')
      .replace(/pi/g, '\\pi')
      .replace(/infinity/g, '\\infty')
      .replace(/alpha/g, '\\alpha')
      .replace(/beta/g, '\\beta')
      .replace(/theta/g, '\\theta');
  },

  truncate(str, maxLen = 100) {
    if (!str || str.length <= maxLen) return str;
    return str.substring(0, maxLen) + '...';
  },

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
};
