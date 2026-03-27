import { createLogger } from '../lib/logger.js';
import { PROBLEM_TYPES } from '../lib/constants.js';
import { ParseError } from '../lib/errors.js';

const log = createLogger('ParserService');

/**
 * Pattern definitions for detecting problem types.
 * Order matters - more specific patterns should come first.
 */
const PATTERN_MAP = [
  {
    type: PROBLEM_TYPES.DIFFERENTIAL_EQUATIONS,
    patterns: [/d[y-z]\/d[x-z]/, /\bdy\b/, /\bdx\b/, /\\frac\{d/, /y['']/, /y''+/, /\bdiff\b/i],
  },
  {
    type: PROBLEM_TYPES.CALCULUS,
    patterns: [/\bintegr(al|ate)\b/i, /\bderivat(ive|e)\b/i, /\blim(it)?\b/i, /\\int/, /\\lim/, /\\sum/, /\\prod/, /\bd\/dx\b/, /\binfinity\b/i, /\\infty/],
  },
  {
    type: PROBLEM_TYPES.LINEAR_ALGEBRA,
    patterns: [/\bmatrix\b/i, /\bmatrices\b/i, /\bdet(erminant)?\b/i, /\beigen/i, /\bvector\b/i, /\\begin\{[pbvBV]?matrix\}/, /\brank\b/i, /\btranspose\b/i],
  },
  {
    type: PROBLEM_TYPES.TRIGONOMETRY,
    patterns: [/\b(sin|cos|tan|cot|sec|csc)\b/i, /\b(arcsin|arccos|arctan)\b/i, /\b(asin|acos|atan)\b/i, /\\(sin|cos|tan|cot|sec|csc)/, /\bradians?\b/i, /\bdegrees?\b/i],
  },
  {
    type: PROBLEM_TYPES.STATISTICS,
    patterns: [/\bmean\b/i, /\bmedian\b/i, /\bstandard\s+deviation\b/i, /\bvariance\b/i, /\bprobability\b/i, /\bcombination\b/i, /\bpermutation\b/i, /\bnormal\s+distribution\b/i, /\bP\(/],
  },
  {
    type: PROBLEM_TYPES.GEOMETRY,
    patterns: [/\barea\b/i, /\bperimeter\b/i, /\bvolume\b/i, /\bangle\b/i, /\btriangle\b/i, /\bcircle\b/i, /\bradius\b/i, /\bdiameter\b/i, /\bpythag/i],
  },
  {
    type: PROBLEM_TYPES.NUMBER_THEORY,
    patterns: [/\bprime\b/i, /\bgcd\b/i, /\blcm\b/i, /\bmod(ulo)?\b/i, /\bfactor(iz|is)/i, /\bdivisib/i, /\bcongruent\b/i, /\beuler/i],
  },
  {
    type: PROBLEM_TYPES.ALGEBRA,
    patterns: [/[=<>]/, /\bsolve\b/i, /\bsimplify\b/i, /\bexpand\b/i, /\bfactor\b/i, /\bequation\b/i, /\bpolynomial\b/i, /\bquadratic\b/i, /\broot\b/i, /\bx\b/, /\by\b/],
  },
  {
    type: PROBLEM_TYPES.ARITHMETIC,
    patterns: [/^[\d\s+\-*/^().,%]+$/, /\bplus\b/i, /\bminus\b/i, /\btimes\b/i, /\bdivide\b/i, /\bsqrt\b/i],
  },
];

/**
 * Detect the problem type of a math expression based on pattern matching.
 * @param {string} input - Math expression or problem text.
 * @returns {string} One of PROBLEM_TYPES values.
 */
export function detectProblemType(input) {
  if (!input || typeof input !== 'string') {
    return PROBLEM_TYPES.UNKNOWN;
  }

  const trimmed = input.trim();

  for (const entry of PATTERN_MAP) {
    for (const pattern of entry.patterns) {
      if (pattern.test(trimmed)) {
        log.debug(`Detected problem type: ${entry.type} for input "${trimmed.substring(0, 50)}..."`);
        return entry.type;
      }
    }
  }

  return PROBLEM_TYPES.UNKNOWN;
}

/**
 * Pre-parse and normalize a math expression before sending to the Python service.
 * Handles common formatting issues, implicit multiplication, etc.
 * @param {string} input - Raw math input from the user.
 * @returns {{ expression: string, problemType: string, normalized: boolean }}
 * @throws {ParseError}
 */
export function parseMathInput(input) {
  if (!input || typeof input !== 'string') {
    throw new ParseError('Input must be a non-empty string');
  }

  let expression = input.trim();

  if (expression.length === 0) {
    throw new ParseError('Expression is empty after trimming');
  }

  // Track whether we modified the expression
  const original = expression;

  // Normalize unicode math symbols to ASCII equivalents
  expression = expression
    .replace(/\u00D7/g, '*')     // multiplication sign
    .replace(/\u00F7/g, '/')     // division sign
    .replace(/\u2212/g, '-')     // minus sign
    .replace(/\u00B2/g, '^2')    // superscript 2
    .replace(/\u00B3/g, '^3')    // superscript 3
    .replace(/\u221A/g, 'sqrt')  // square root
    .replace(/\u03C0/g, 'pi')    // pi
    .replace(/\u221E/g, 'infinity') // infinity
    .replace(/\u2264/g, '<=')    // less than or equal
    .replace(/\u2265/g, '>=');   // greater than or equal

  // Replace common word-based operators
  expression = expression
    .replace(/\bsquared\b/gi, '^2')
    .replace(/\bcubed\b/gi, '^3')
    .replace(/\bto\s+the\s+power\s+of\b/gi, '^');

  // Detect problem type
  const problemType = detectProblemType(expression);

  log.debug(`Parsed: "${original.substring(0, 50)}" -> type=${problemType}, normalized=${expression !== original}`);

  return {
    expression,
    problemType,
    normalized: expression !== original,
  };
}

/**
 * Extract multiple math expressions from a block of text.
 * Useful when OCR returns a page with multiple problems.
 * @param {string} text
 * @returns {string[]}
 */
export function extractExpressions(text) {
  if (!text) return [];

  // Split on common delimiters: newlines, semicolons, numbered items
  const lines = text.split(/[\n;]/).map((l) => l.trim()).filter(Boolean);

  const expressions = [];
  for (const line of lines) {
    // Strip leading numbering like "1.", "1)", "a)", "(a)"
    const cleaned = line.replace(/^[\s]*(?:\d+[.)]\s*|[a-z][.)]\s*|\([a-z]\)\s*)/i, '').trim();
    if (cleaned.length > 0 && cleaned.length <= 5000) {
      expressions.push(cleaned);
    }
  }

  return expressions;
}
