import { createLogger } from '../lib/logger.js';
import { config } from '../startup/env.js';
import { OCRError } from '../lib/errors.js';
import { LIMITS } from '../lib/constants.js';
import { serializeHandwritingRequest, deserializeOCRResponse } from '../lib/serializers.js';
import { getHandwritingProvider } from './providerService.js';

const log = createLogger('HandwritingService');

/**
 * Send a handwriting image to the Python /handwriting endpoint.
 * Falls back to Mathpix or OpenAI providers if available.
 *
 * @param {string} imageData - Base64 encoded image data.
 * @param {string} mimeType - Image MIME type.
 * @param {object} [options]
 * @returns {Promise<object>} { text, latex, confidence }
 */
export async function recogniseHandwriting(imageData, mimeType, options = {}) {
  log.info(`Handwriting OCR request: mimeType=${mimeType}`);

  const rawData = imageData.includes(',') ? imageData.split(',')[1] : imageData;

  // 1. Try Python service handwriting endpoint
  try {
    const result = await recogniseWithPython(rawData, mimeType, options);
    if (result && result.text) {
      log.info(`Handwriting OCR successful via Python service`);
      return result;
    }
    log.warn('Python handwriting OCR returned empty text, trying fallback');
  } catch (err) {
    log.warn(`Python handwriting OCR failed: ${err.message}`);
  }

  // 2. Try Mathpix or OpenAI fallback
  try {
    const provider = getHandwritingProvider();
    if (provider) {
      let result;
      if (typeof provider.recogniseHandwriting === 'function') {
        result = await provider.recogniseHandwriting(rawData, mimeType, options);
      } else if (typeof provider.ocrImage === 'function') {
        result = await provider.ocrImage(rawData, mimeType, options);
      }
      if (result && (result.text || result.latex)) {
        log.info(`Handwriting OCR successful via fallback provider`);
        return {
          text: result.text || '',
          latex: result.latex || null,
          confidence: result.confidence || null,
          regions: [],
          language: 'en',
        };
      }
    }
  } catch (err) {
    log.warn(`Fallback handwriting provider failed: ${err.message}`);
  }

  throw new OCRError('Handwriting recognition failed across all providers.');
}

/**
 * Call the Python /handwriting endpoint.
 */
async function recogniseWithPython(imageData, mimeType, options = {}) {
  const body = serializeHandwritingRequest({ imageData, mimeType, options });
  const url = `${config.PYTHON_SERVICE_URL}/handwriting`;

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeout || LIMITS.OCR_TIMEOUT_MS);

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: controller.signal,
    });

    if (!res.ok) {
      const errBody = await res.text().catch(() => '');
      throw new Error(`Handwriting endpoint returned ${res.status}: ${errBody}`);
    }

    const raw = await res.json();
    return deserializeOCRResponse(raw);
  } finally {
    clearTimeout(timeout);
  }
}
