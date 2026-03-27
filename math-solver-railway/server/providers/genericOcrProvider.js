import { createLogger } from '../lib/logger.js';
import { config } from '../startup/env.js';
import { LIMITS } from '../lib/constants.js';

const log = createLogger('GenericOCR');

/**
 * Generic OCR provider wrapper.
 * Delegates to the Python service's built-in OCR capabilities,
 * which may use Tesseract or other open-source engines.
 * Always available as long as the Python service is reachable.
 */
class GenericOCRProvider {
  constructor() {
    this._baseUrl = config.PYTHON_SERVICE_URL;
  }

  /** @returns {boolean} Always true - relies on the Python service. */
  isAvailable() {
    return true;
  }

  /**
   * Send an image to the Python service's generic OCR endpoint.
   * @param {string} base64Image - Base64 encoded image data.
   * @param {string} mimeType
   * @param {object} [options]
   * @returns {Promise<object>} { text, latex, confidence }
   */
  async recognise(base64Image, mimeType, options = {}) {
    log.debug('Performing OCR via generic Python OCR service');

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), options.timeout || LIMITS.OCR_TIMEOUT_MS);

    try {
      const res = await fetch(`${this._baseUrl}/ocr`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image: base64Image,
          mime_type: mimeType,
          preprocess: options.preprocess !== false,
          language: options.language || 'en',
          provider: 'generic',
        }),
        signal: controller.signal,
      });

      if (!res.ok) {
        const body = await res.text();
        throw new Error(`Generic OCR service error ${res.status}: ${body}`);
      }

      const data = await res.json();

      return {
        text: data.text || data.extracted_text || '',
        latex: data.latex || null,
        confidence: data.confidence ?? null,
        provider: 'generic_ocr',
      };
    } finally {
      clearTimeout(timeout);
    }
  }
}

const genericOcrProvider = new GenericOCRProvider();
export default genericOcrProvider;
