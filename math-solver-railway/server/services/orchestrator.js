import { createLogger } from '../lib/logger.js';
import { INPUT_TYPES, PROBLEM_TYPES } from '../lib/constants.js';
import { SolverError, wrapError } from '../lib/errors.js';
import { parseMathInput, extractExpressions } from './parserService.js';
import { solve } from './solverService.js';
import { verify } from './verificationService.js';
import { recognise } from './ocrService.js';
import { recogniseHandwriting } from './handwritingService.js';
import { extractFromPDF, getTextFromPages } from './pdfService.js';
import { generateGraph } from './graphService.js';
import { initializeProviders } from './providerService.js';

const log = createLogger('Orchestrator');

/**
 * Main orchestration entry point.
 * Accepts any input type and routes it through the appropriate pipeline:
 *
 *   typed       -> parse -> solve -> verify -> format
 *   image       -> preprocess -> OCR -> parse -> solve -> verify -> format
 *   pdf         -> extract text -> OCR fallback -> parse -> solve -> verify -> format
 *   handwritten -> preprocess -> handwriting OCR -> parse -> solve -> verify -> format
 *
 * @param {object} params
 * @param {string} params.input - The raw input (text or base64 file data).
 * @param {string} params.inputType - One of INPUT_TYPES.
 * @param {object} [params.options] - Additional options.
 * @returns {Promise<object>} Unified result object.
 */
export async function orchestrate({ input, inputType, options = {} }) {
  const startTime = Date.now();

  // Ensure providers are registered
  initializeProviders();

  log.info(`Orchestrating: inputType=${inputType}, optionKeys=${Object.keys(options).join(',')}`);

  const result = {
    success: false,
    input: null,
    inputType,
    expression: null,
    problemType: PROBLEM_TYPES.UNKNOWN,
    answer: null,
    steps: [],
    latex: null,
    confidence: null,
    verification: null,
    graphs: [],
    warnings: [],
    executionTime: null,
    ocrResult: null,
    pdfResult: null,
  };

  try {
    // ---- Phase 1: Extract text from input ----
    let extractedText;
    let mimeType = options.mimeType || 'image/png';

    switch (inputType) {
      case INPUT_TYPES.TYPED:
        extractedText = input;
        result.input = input;
        break;

      case INPUT_TYPES.IMAGE:
        result.input = '[image data]';
        extractedText = await handleImageInput(input, mimeType, options, result);
        break;

      case INPUT_TYPES.PDF:
        result.input = '[PDF data]';
        extractedText = await handlePDFInput(input, options, result);
        break;

      case INPUT_TYPES.HANDWRITTEN:
        result.input = '[handwritten image]';
        extractedText = await handleHandwrittenInput(input, mimeType, options, result);
        break;

      default:
        throw new SolverError(`Unsupported input type: ${inputType}`);
    }

    if (!extractedText || extractedText.trim().length === 0) {
      throw new SolverError('No mathematical expression could be extracted from the input');
    }

    // ---- Phase 2: Parse the extracted text ----
    const parsed = parseMathInput(extractedText);
    result.expression = parsed.expression;
    result.problemType = parsed.problemType;

    if (parsed.normalized) {
      result.warnings.push('Expression was normalized from the original input');
    }

    // ---- Phase 3: Solve ----
    const solveResult = await solve(parsed.expression, parsed.problemType, options);
    result.answer = solveResult.answer;
    result.steps = solveResult.steps;
    result.latex = solveResult.latex;
    result.confidence = solveResult.confidence;

    if (solveResult.warnings && solveResult.warnings.length > 0) {
      result.warnings.push(...solveResult.warnings);
    }

    // Override problem type if the solver detected a more specific one
    if (solveResult.problemType && solveResult.problemType !== PROBLEM_TYPES.UNKNOWN) {
      result.problemType = solveResult.problemType;
    }

    // ---- Phase 4: Verify ----
    try {
      if (result.answer && options.verify !== false) {
        result.verification = await verify(
          parsed.expression,
          String(result.answer),
          result.problemType,
          { crossVerify: options.crossVerify }
        );

        if (result.verification && result.verification.confidence != null) {
          // Blend solver confidence with verification confidence
          const solverConf = result.confidence || 0.5;
          const verifyConf = result.verification.confidence || 0.5;
          result.confidence = Math.round(((solverConf + verifyConf) / 2) * 100) / 100;
        }
      }
    } catch (err) {
      log.warn('Verification phase failed (non-fatal)', err.message);
      result.warnings.push(`Verification skipped: ${err.message}`);
    }

    // ---- Phase 5: Optional graph generation ----
    if (options.generateGraph) {
      try {
        const graph = await generateGraph(
          parsed.expression,
          options.graphType || 'line',
          options.graphOptions || {}
        );
        result.graphs.push(graph);
      } catch (err) {
        log.warn('Graph generation failed (non-fatal)', err.message);
        result.warnings.push(`Graph generation skipped: ${err.message}`);
      }
    }

    // ---- Format final result ----
    result.success = true;
    result.executionTime = Date.now() - startTime;

    log.info(`Orchestration complete in ${result.executionTime}ms. Answer: "${String(result.answer).substring(0, 60)}"`);

    return result;
  } catch (err) {
    const wrapped = wrapError(err);
    result.success = false;
    result.executionTime = Date.now() - startTime;
    result.error = wrapped.toJSON();

    log.error(`Orchestration failed in ${result.executionTime}ms: ${wrapped.message}`);

    return result;
  }
}

// ---- Input-type handlers ----

/**
 * Handle image input: preprocess -> OCR -> return text.
 */
async function handleImageInput(imageData, mimeType, options, result) {
  const ocrResult = await recognise(imageData, mimeType, {
    preprocess: options.preprocess !== false,
    language: options.language,
  });

  result.ocrResult = {
    text: ocrResult.text,
    latex: ocrResult.latex,
    confidence: ocrResult.confidence,
  };

  // Prefer LaTeX if available, otherwise use plain text
  return ocrResult.latex || ocrResult.text;
}

/**
 * Handle PDF input: extract text -> OCR fallback -> return text.
 */
async function handlePDFInput(pdfData, options, result) {
  const pdfResult = await extractFromPDF(pdfData, {
    pages: options.pages,
    ocrFallback: options.ocrFallback !== false,
    language: options.language,
  });

  result.pdfResult = {
    totalPages: pdfResult.totalPages,
    pageCount: pdfResult.pages.length,
  };

  const text = getTextFromPages(pdfResult, options.pageNumbers);

  if (!text && pdfResult.pages.length > 0) {
    // All pages empty - likely scanned PDF. The Python service should have
    // already applied OCR fallback, but we report a warning.
    result.warnings.push('PDF pages appear to be scanned images. OCR fallback was applied.');
  }

  // If the PDF contained multiple expressions, we take the first one.
  // The caller can use extractExpressions() for batch processing.
  const expressions = extractExpressions(text || pdfResult.combinedText);
  if (expressions.length > 1) {
    result.warnings.push(`PDF contains ${expressions.length} expressions. Solving the first one.`);
  }

  return expressions[0] || text || pdfResult.combinedText;
}

/**
 * Handle handwritten input: preprocess -> handwriting OCR -> return text.
 */
async function handleHandwrittenInput(imageData, mimeType, options, result) {
  const ocrResult = await recogniseHandwriting(imageData, mimeType, {
    enhance: options.enhance !== false,
    language: options.language,
  });

  result.ocrResult = {
    text: ocrResult.text,
    latex: ocrResult.latex,
    confidence: ocrResult.confidence,
  };

  return ocrResult.latex || ocrResult.text;
}
