import { VERSION, PROBLEM_TYPES, INPUT_TYPES, GRAPH_TYPES, REPORT_FORMATS, ALL_SUPPORTED_FORMATS, LIMITS } from '../lib/constants.js';
import { getProviderSummary, initializeProviders } from '../services/providerService.js';

/**
 * Returns system capabilities, version info, and provider availability.
 *
 * @returns {object}
 */
export function getCapabilities() {
  initializeProviders();

  return {
    version: VERSION,
    capabilities: {
      inputTypes: Object.values(INPUT_TYPES),
      problemTypes: Object.values(PROBLEM_TYPES),
      graphTypes: Object.values(GRAPH_TYPES),
      reportFormats: Object.values(REPORT_FORMATS),
      supportedFileFormats: ALL_SUPPORTED_FORMATS,
    },
    limits: {
      maxUploadSize: LIMITS.MAX_UPLOAD_SIZE,
      maxInputLength: LIMITS.MAX_INPUT_LENGTH,
      maxExpressionLength: LIMITS.MAX_EXPRESSION_LENGTH,
      solveTimeout: LIMITS.SOLVE_TIMEOUT_MS,
      ocrTimeout: LIMITS.OCR_TIMEOUT_MS,
    },
    providers: getProviderSummary(),
  };
}
