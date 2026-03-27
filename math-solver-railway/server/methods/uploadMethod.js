import { Meteor } from 'meteor/meteor';
import { createLogger } from '../lib/logger.js';
import { validateFile, isImageType, isPdfType } from '../lib/validators.js';
import { INPUT_TYPES } from '../lib/constants.js';
import { saveTempFile, getTempFileUrl } from '../services/fileService.js';
import { recognise } from '../services/ocrService.js';
import { recogniseHandwriting } from '../services/handwritingService.js';
import { extractFromPDF } from '../services/pdfService.js';
import { wrapError, UploadError } from '../lib/errors.js';

const log = createLogger('Method:Upload');

Meteor.methods({
  /**
   * Meteor method 'upload'.
   * Accepts file data (base64), validates it, processes through the appropriate
   * OCR pipeline, and returns extracted text.
   *
   * @param {object} params
   * @param {string} params.data - Base64 encoded file content.
   * @param {string} params.type - MIME type of the file.
   * @param {string} params.name - Original filename.
   * @param {number} [params.size] - Client-reported file size in bytes.
   * @param {string} [params.inputType] - Explicit input type override ('image', 'pdf', 'handwritten').
   * @param {object} [params.options] - OCR options.
   * @returns {object} { fileId, fileName, mimeType, size, url, extractedText, latex, confidence }
   */
  async upload(params) {
    const { data, type, name, size, inputType, options = {} } = params || {};

    try {
      // Validate the file
      validateFile({ data, type, name, size });

      // Save to temp storage
      const tempFile = saveTempFile(data, name, type);
      log.info(`File uploaded via method: ${name} (${tempFile.size} bytes), id=${tempFile.fileId}`);

      const result = {
        fileId: tempFile.fileId,
        fileName: name,
        mimeType: type,
        size: tempFile.size,
        url: getTempFileUrl(tempFile.fileId),
        extractedText: null,
        latex: null,
        confidence: null,
      };

      // Determine processing type
      const effectiveType = inputType || (isPdfType(type) ? INPUT_TYPES.PDF : INPUT_TYPES.IMAGE);

      if (isPdfType(type)) {
        const pdfResult = await extractFromPDF(data, options);
        result.extractedText = pdfResult.combinedText || '';
        result.pages = pdfResult.pages;
        result.totalPages = pdfResult.totalPages;
      } else if (isImageType(type)) {
        if (effectiveType === INPUT_TYPES.HANDWRITTEN) {
          const ocrResult = await recogniseHandwriting(data, type, options);
          result.extractedText = ocrResult.text || '';
          result.latex = ocrResult.latex || null;
          result.confidence = ocrResult.confidence;
        } else {
          const ocrResult = await recognise(data, type, options);
          result.extractedText = ocrResult.text || '';
          result.latex = ocrResult.latex || null;
          result.confidence = ocrResult.confidence;
        }
      } else {
        throw new UploadError(`Cannot process file type: ${type}`);
      }

      log.info(`Upload method complete: extracted ${(result.extractedText || '').length} chars`);
      return result;
    } catch (err) {
      if (err instanceof Meteor.Error) throw err;

      const wrapped = wrapError(err);
      log.error(`upload method error: ${wrapped.message}`);
      throw new Meteor.Error(wrapped.code, wrapped.message, wrapped.details);
    }
  },
});
