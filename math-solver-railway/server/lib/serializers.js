import { createLogger } from './logger.js';

const log = createLogger('Serializers');

/**
 * Serialize a solve request for the Python service.
 * @param {object} params
 * @returns {object} Body ready for JSON.stringify
 */
export function serializeSolveRequest({ expression, problemType, options = {} }) {
  return {
    expression,
    problem_type: problemType || 'auto',
    step_by_step: options.stepByStep !== false,
    simplify: options.simplify !== false,
    verify: options.verify !== false,
    latex: options.latex !== false,
    provider: options.provider || null,
  };
}

/**
 * Deserialize a solve response from the Python service.
 * @param {object} raw - Raw JSON response
 * @returns {object} Normalized result
 */
export function deserializeSolveResponse(raw) {
  if (!raw) return null;

  return {
    answer: raw.answer ?? raw.result ?? null,
    steps: normalizeSteps(raw.steps),
    latex: raw.latex ?? null,
    problemType: raw.problem_type ?? raw.problemType ?? 'unknown',
    confidence: raw.confidence ?? null,
    method: raw.method ?? null,
    alternativeForms: raw.alternative_forms ?? raw.alternativeForms ?? [],
    executionTime: raw.execution_time ?? raw.executionTime ?? null,
    warnings: raw.warnings ?? [],
  };
}

/**
 * Serialize an OCR request for the Python service.
 * @param {object} params
 * @returns {object}
 */
export function serializeOCRRequest({ imageData, mimeType, options = {} }) {
  return {
    image: imageData,
    mime_type: mimeType || 'image/png',
    preprocess: options.preprocess !== false,
    language: options.language || 'en',
    provider: options.provider || null,
  };
}

/**
 * Deserialize an OCR response.
 * @param {object} raw
 * @returns {object}
 */
export function deserializeOCRResponse(raw) {
  if (!raw) return null;

  return {
    text: raw.text ?? raw.extracted_text ?? '',
    latex: raw.latex ?? null,
    confidence: raw.confidence ?? null,
    regions: raw.regions ?? [],
    language: raw.language ?? 'en',
  };
}

/**
 * Serialize a graph generation request.
 * @param {object} params
 * @returns {object}
 */
export function serializeGraphRequest({ expression, graphType, options = {} }) {
  return {
    expression,
    graph_type: graphType || 'line',
    x_range: options.xRange || [-10, 10],
    y_range: options.yRange || [-10, 10],
    width: options.width || 800,
    height: options.height || 600,
    title: options.title || '',
    format: options.format || 'png',
  };
}

/**
 * Deserialize a graph response.
 * @param {object} raw
 * @returns {object}
 */
export function deserializeGraphResponse(raw) {
  if (!raw) return null;

  return {
    image: raw.image ?? raw.graph ?? null,
    format: raw.format ?? 'png',
    mimeType: raw.mime_type ?? 'image/png',
    metadata: raw.metadata ?? {},
  };
}

/**
 * Serialize a report generation request.
 * @param {object} params
 * @returns {object}
 */
export function serializeReportRequest({ solution, format, options = {} }) {
  return {
    solution: {
      input: solution.input,
      answer: solution.answer,
      steps: solution.steps,
      latex: solution.latex,
      problem_type: solution.problemType,
      confidence: solution.confidence,
      graphs: solution.graphs || [],
    },
    format: format || 'pdf',
    include_graphs: options.includeGraphs !== false,
    include_steps: options.includeSteps !== false,
    title: options.title || 'Math Solution Report',
  };
}

/**
 * Deserialize a report response.
 * @param {object} raw
 * @returns {object}
 */
export function deserializeReportResponse(raw) {
  if (!raw) return null;

  return {
    data: raw.data ?? raw.report ?? null,
    format: raw.format ?? 'pdf',
    mimeType: raw.mime_type ?? 'application/pdf',
    filename: raw.filename ?? 'report.pdf',
  };
}

/**
 * Serialize a verification request.
 * @param {object} params
 * @returns {object}
 */
export function serializeVerificationRequest({ expression, answer, problemType }) {
  return {
    expression,
    answer,
    problem_type: problemType || 'auto',
  };
}

/**
 * Deserialize a verification response.
 * @param {object} raw
 * @returns {object}
 */
export function deserializeVerificationResponse(raw) {
  if (!raw) return null;

  return {
    verified: raw.verified ?? raw.is_correct ?? false,
    confidence: raw.confidence ?? null,
    method: raw.method ?? null,
    notes: raw.notes ?? raw.explanation ?? '',
    alternativeAnswer: raw.alternative_answer ?? null,
  };
}

/**
 * Serialize a handwriting OCR request.
 * @param {object} params
 * @returns {object}
 */
export function serializeHandwritingRequest({ imageData, mimeType, options = {} }) {
  return {
    image: imageData,
    mime_type: mimeType || 'image/png',
    preprocess: true,
    enhance: options.enhance !== false,
    language: options.language || 'en',
  };
}

/**
 * Serialize a PDF extraction request.
 * @param {object} params
 * @returns {object}
 */
export function serializePDFRequest({ pdfData, options = {} }) {
  return {
    pdf: pdfData,
    pages: options.pages || 'all',
    ocr_fallback: options.ocrFallback !== false,
    language: options.language || 'en',
  };
}

/**
 * Deserialize a PDF extraction response.
 * @param {object} raw
 * @returns {object}
 */
export function deserializePDFResponse(raw) {
  if (!raw) return null;

  return {
    pages: (raw.pages || []).map((page) => ({
      pageNumber: page.page_number ?? page.pageNumber,
      text: page.text ?? '',
      latex: page.latex ?? null,
      confidence: page.confidence ?? null,
    })),
    totalPages: raw.total_pages ?? raw.totalPages ?? 0,
    combinedText: raw.combined_text ?? raw.combinedText ?? '',
  };
}

/**
 * Normalize step-by-step solution steps into a consistent array format.
 * @param {*} steps
 * @returns {Array}
 */
function normalizeSteps(steps) {
  if (!steps) return [];
  if (Array.isArray(steps)) {
    return steps.map((step, i) => {
      if (typeof step === 'string') {
        return { number: i + 1, description: step, expression: null };
      }
      return {
        number: step.number ?? step.step_number ?? i + 1,
        description: step.description ?? step.text ?? '',
        expression: step.expression ?? step.latex ?? null,
      };
    });
  }
  if (typeof steps === 'string') {
    return steps.split('\n').filter(Boolean).map((line, i) => ({
      number: i + 1,
      description: line.trim(),
      expression: null,
    }));
  }
  return [];
}
