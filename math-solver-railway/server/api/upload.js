import { createLogger } from '../lib/logger.js';
import { validateFile, isImageType, isPdfType } from '../lib/validators.js';
import { INPUT_TYPES } from '../lib/constants.js';
import { saveTempFile, deleteTempFile, getTempFileUrl } from '../services/fileService.js';
import { recognise } from '../services/ocrService.js';
import { recogniseHandwriting } from '../services/handwritingService.js';
import { extractFromPDF } from '../services/pdfService.js';
import { wrapError, UploadError } from '../lib/errors.js';

const log = createLogger('API:Upload');

/**
 * HTTP endpoint handler for file uploads.
 * Validates the file, saves it temporarily, and runs OCR if applicable.
 *
 * @param {object} params - { data (base64), type (mimeType), name, size, inputType }
 * @returns {Promise<object>}
 */
export async function handleUpload(params) {
  const { data, type, name, size, inputType } = params;

  try {
    // Validate file
    validateFile({ data, type, name, size });

    // Save temp file
    const { filePath, fileId, size: actualSize } = saveTempFile(data, name, type);
    log.info(`File uploaded: ${name} (${actualSize} bytes), id=${fileId}`);

    const result = {
      fileId,
      fileName: name,
      mimeType: type,
      size: actualSize,
      url: getTempFileUrl(fileId),
      extractedText: null,
      latex: null,
      confidence: null,
    };

    // Determine processing approach based on file type and explicit input type
    const effectiveType = inputType || (isPdfType(type) ? INPUT_TYPES.PDF : INPUT_TYPES.IMAGE);

    if (isPdfType(type)) {
      // PDF extraction
      const pdfResult = await extractFromPDF(data, {});
      result.extractedText = pdfResult.combinedText || '';
      result.pages = pdfResult.pages;
      result.totalPages = pdfResult.totalPages;
    } else if (isImageType(type)) {
      if (effectiveType === INPUT_TYPES.HANDWRITTEN) {
        // Handwriting OCR
        const ocrResult = await recogniseHandwriting(data, type, {});
        result.extractedText = ocrResult.text || '';
        result.latex = ocrResult.latex || null;
        result.confidence = ocrResult.confidence;
      } else {
        // Standard image OCR
        const ocrResult = await recognise(data, type, {});
        result.extractedText = ocrResult.text || '';
        result.latex = ocrResult.latex || null;
        result.confidence = ocrResult.confidence;
      }
    } else {
      throw new UploadError(`Cannot process file type: ${type}`);
    }

    log.info(`Upload processed: extracted ${(result.extractedText || '').length} chars`);
    return result;
  } catch (err) {
    const wrapped = wrapError(err);
    log.error(`Upload handler error: ${wrapped.message}`);
    return {
      success: false,
      error: wrapped.toJSON(),
    };
  }
}
