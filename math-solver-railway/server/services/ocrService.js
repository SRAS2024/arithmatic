import { createLogger } from '../lib/logger.js';
import { config } from '../startup/env.js';
import { OCRError, ServiceUnavailableError } from '../lib/errors.js';
import { LIMITS } from '../lib/constants.js';
import { serializeOCRRequest, deserializeOCRResponse } from '../lib/serializers.js';
import { getOCRProvider } from './providerService.js';

const log = createLogger('OCRService');

/**
 * Send an image to the Python /ocr endpoint for text extraction.
 * Falls back to optional third-party providers if the Python service fails.
 *
 * @param {string} imageData - Base64 encoded image data.
 * @param {string} mimeType - Image MIME type.
 * @param {object} [options]
 * @returns {Promise<object>} { text, latex, confidence, regions, language }
 */
export async function recognise(imageData, mimeType, options = {}) {
  log.info(`OCR request: mimeType=${mimeType}, dataLength=${imageData.length}`);

  // Strip data URI prefix if present
  const rawData = imageData.includes(',') ? imageData.split(',')[1] : imageData;

  // 1. Try Python service first
  try {
    const result = await recogniseWithPython(rawData, mimeType, options);
    if (result && result.text) {
      log.info(`OCR successful via Python service (confidence: ${result.confidence})`);
      return result;
    }
    log.warn('Python OCR returned empty text, trying fallback');
  } catch (err) {
    log.warn(`Python OCR failed: ${err.message}, trying fallback providers`);
  }

  // 2. Try third-party provider fallback
  try {
    const provider = getOCRProvider();
    if (provider) {
      let result;
      if (typeof provider.recognise === 'function') {
        result = await provider.recognise(rawData, mimeType, options);
      } else if (typeof provider.ocrImage === 'function') {
        result = await provider.ocrImage(rawData, mimeType, options);
      }
      if (result && (result.text || result.latex)) {
        log.info(`OCR successful via fallback provider (${result.provider || 'external'})`);
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
    log.warn(`Fallback OCR provider failed: ${err.message}`);
  }

  throw new OCRError('All OCR methods failed. Could not extract text from image.');
}

/**
 * Call the Python /ocr endpoint.
 */
async function recogniseWithPython(imageData, mimeType, options = {}) {
  const body = serializeOCRRequest({ imageData, mimeType, options });
  const url = `${config.PYTHON_SERVICE_URL}/ocr`;

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
      throw new Error(`OCR endpoint returned ${res.status}: ${errBody}`);
    }

    const raw = await res.json();
    return deserializeOCRResponse(raw);
  } finally {
    clearTimeout(timeout);
  }
}
