import { createLogger } from '../lib/logger.js';
import { config } from '../startup/env.js';
import { LIMITS } from '../lib/constants.js';

const log = createLogger('Mathpix');

/**
 * Mathpix OCR integration for extracting math from images.
 * Degrades gracefully if no credentials are configured.
 */
class MathpixProvider {
  constructor() {
    this._appId = config.MATHPIX_APP_ID;
    this._appKey = config.MATHPIX_APP_KEY;
    this._baseUrl = 'https://api.mathpix.com/v3';
  }

  /** @returns {boolean} */
  isAvailable() {
    return Boolean(this._appId && this._appKey);
  }

  /**
   * Extract math from an image using Mathpix OCR.
   * @param {string} base64Image - Base64 encoded image data (without data URI prefix).
   * @param {string} mimeType
   * @param {object} [options]
   * @returns {Promise<object>} { text, latex, confidence }
   */
  async recognise(base64Image, mimeType, options = {}) {
    if (!this.isAvailable()) {
      throw new Error('Mathpix credentials not configured');
    }

    log.debug('Performing OCR via Mathpix');

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), options.timeout || LIMITS.OCR_TIMEOUT_MS);

    try {
      const res = await fetch(`${this._baseUrl}/text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          app_id: this._appId,
          app_key: this._appKey,
        },
        body: JSON.stringify({
          src: `data:${mimeType};base64,${base64Image}`,
          formats: ['text', 'latex_styled', 'asciimath'],
          data_options: {
            include_asciimath: true,
            include_latex: true,
          },
        }),
        signal: controller.signal,
      });

      if (!res.ok) {
        const body = await res.text();
        throw new Error(`Mathpix API error ${res.status}: ${body}`);
      }

      const data = await res.json();

      return {
        text: data.text || '',
        latex: data.latex_styled || data.latex || null,
        asciimath: data.asciimath || null,
        confidence: data.confidence ?? data.confidence_rate ?? null,
        provider: 'mathpix',
      };
    } finally {
      clearTimeout(timeout);
    }
  }

  /**
   * Extract math from handwritten input using Mathpix.
   * Uses the same endpoint but with handwriting hints.
   * @param {string} base64Image
   * @param {string} mimeType
   * @param {object} [options]
   * @returns {Promise<object>}
   */
  async recogniseHandwriting(base64Image, mimeType, options = {}) {
    if (!this.isAvailable()) {
      throw new Error('Mathpix credentials not configured');
    }

    log.debug('Performing handwriting OCR via Mathpix');

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), options.timeout || LIMITS.OCR_TIMEOUT_MS);

    try {
      const res = await fetch(`${this._baseUrl}/text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          app_id: this._appId,
          app_key: this._appKey,
        },
        body: JSON.stringify({
          src: `data:${mimeType};base64,${base64Image}`,
          formats: ['text', 'latex_styled'],
          data_options: {
            include_latex: true,
          },
          // Mathpix handles handwriting automatically, but we can hint
          metadata: {
            type: 'handwriting',
          },
        }),
        signal: controller.signal,
      });

      if (!res.ok) {
        const body = await res.text();
        throw new Error(`Mathpix handwriting API error ${res.status}: ${body}`);
      }

      const data = await res.json();

      return {
        text: data.text || '',
        latex: data.latex_styled || data.latex || null,
        confidence: data.confidence ?? null,
        provider: 'mathpix',
      };
    } finally {
      clearTimeout(timeout);
    }
  }
}

const mathpixProvider = new MathpixProvider();
export default mathpixProvider;
