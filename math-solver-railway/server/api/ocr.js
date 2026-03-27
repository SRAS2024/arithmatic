import { createLogger } from '../lib/logger.js';
import { recognise } from '../services/ocrService.js';
import { wrapError } from '../lib/errors.js';

const log = createLogger('API:OCR');

/**
 * OCR endpoint handler.
 * Accepts base64 image data and returns extracted text.
 *
 * @param {object} params - { image (base64), mimeType, options }
 * @returns {Promise<object>}
 */
export async function handleOCR(params) {
  const { image, mimeType, options = {} } = params;

  try {
    if (!image) {
      throw new Error('Image data is required');
    }

    const result = await recognise(image, mimeType || 'image/png', options);

    return {
      success: true,
      text: result.text,
      latex: result.latex,
      confidence: result.confidence,
      regions: result.regions,
      language: result.language,
    };
  } catch (err) {
    const wrapped = wrapError(err);
    log.error(`OCR handler error: ${wrapped.message}`);
    return {
      success: false,
      error: wrapped.toJSON(),
    };
  }
}
