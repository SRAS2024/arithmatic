import {
  SUPPORTED_IMAGE_FORMATS,
  SUPPORTED_DOCUMENT_FORMATS,
  ALL_SUPPORTED_FORMATS,
  LIMITS,
  INPUT_TYPES,
} from './constants.js';
import { ValidationError, UploadError } from './errors.js';

/**
 * Validate a typed math input string.
 * @param {string} input - The math expression or problem text.
 * @returns {{ valid: true, sanitized: string }}
 * @throws {ValidationError}
 */
export function validateMathInput(input) {
  if (!input || typeof input !== 'string') {
    throw new ValidationError('Math input must be a non-empty string');
  }

  const trimmed = input.trim();

  if (trimmed.length === 0) {
    throw new ValidationError('Math input cannot be empty');
  }

  if (trimmed.length > LIMITS.MAX_INPUT_LENGTH) {
    throw new ValidationError(
      `Math input exceeds maximum length of ${LIMITS.MAX_INPUT_LENGTH} characters`
    );
  }

  // Basic sanitization: remove null bytes and control characters (keep newlines/tabs)
  const sanitized = trimmed.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');

  return { valid: true, sanitized };
}

/**
 * Validate a file for upload.
 * @param {{ data: string, type: string, name: string, size: number }} file
 * @returns {{ valid: true }}
 * @throws {UploadError}
 */
export function validateFile(file) {
  if (!file) {
    throw new UploadError('No file provided');
  }

  if (!file.data) {
    throw new UploadError('File data is missing');
  }

  if (!file.type) {
    throw new UploadError('File type (MIME type) is required');
  }

  if (!file.name) {
    throw new UploadError('File name is required');
  }

  validateFileType(file.type, file.name);
  validateUploadSize(file.data, file.size);

  return { valid: true };
}

/**
 * Validate that the file type is supported.
 * @param {string} mimeType
 * @param {string} [fileName]
 * @throws {UploadError}
 */
export function validateFileType(mimeType, fileName = '') {
  const normalizedType = mimeType.toLowerCase();

  if (!ALL_SUPPORTED_FORMATS.includes(normalizedType)) {
    // Attempt to infer from file extension
    const ext = fileName.split('.').pop().toLowerCase();
    const extMap = {
      png: 'image/png',
      jpg: 'image/jpeg',
      jpeg: 'image/jpeg',
      gif: 'image/gif',
      bmp: 'image/bmp',
      webp: 'image/webp',
      tiff: 'image/tiff',
      tif: 'image/tiff',
      pdf: 'application/pdf',
    };

    if (!extMap[ext] || !ALL_SUPPORTED_FORMATS.includes(extMap[ext])) {
      throw new UploadError(
        `Unsupported file type: ${mimeType}. Supported: ${ALL_SUPPORTED_FORMATS.join(', ')}`
      );
    }
  }

  return true;
}

/**
 * Validate file size against the upload limit.
 * @param {string} base64Data - Base64 encoded file data
 * @param {number} [reportedSize] - Client-reported file size in bytes
 * @throws {UploadError}
 */
export function validateUploadSize(base64Data, reportedSize) {
  // Calculate actual size from base64
  let actualSize;
  if (typeof base64Data === 'string') {
    // Remove data URL prefix if present
    const raw = base64Data.includes(',') ? base64Data.split(',')[1] : base64Data;
    // Base64 size: roughly 3/4 of string length
    actualSize = Math.ceil((raw.length * 3) / 4);
  } else {
    actualSize = reportedSize || 0;
  }

  const maxSize = parseInt(process.env.MAX_UPLOAD_SIZE, 10) || LIMITS.MAX_UPLOAD_SIZE;

  if (actualSize > maxSize) {
    const maxMB = (maxSize / (1024 * 1024)).toFixed(1);
    const actualMB = (actualSize / (1024 * 1024)).toFixed(1);
    throw new UploadError(
      `File size (${actualMB}MB) exceeds maximum allowed size (${maxMB}MB)`
    );
  }

  return true;
}

/**
 * Validate the input type parameter.
 * @param {string} inputType
 * @returns {string} Normalized input type.
 * @throws {ValidationError}
 */
export function validateInputType(inputType) {
  if (!inputType || typeof inputType !== 'string') {
    throw new ValidationError('inputType is required');
  }

  const normalized = inputType.toLowerCase().trim();
  const validTypes = Object.values(INPUT_TYPES);

  if (!validTypes.includes(normalized)) {
    throw new ValidationError(
      `Invalid input type: "${inputType}". Valid types: ${validTypes.join(', ')}`
    );
  }

  return normalized;
}

/**
 * Validate an expression for graph generation.
 * @param {string} expression
 * @returns {{ valid: true, sanitized: string }}
 * @throws {ValidationError}
 */
export function validateExpression(expression) {
  if (!expression || typeof expression !== 'string') {
    throw new ValidationError('Expression must be a non-empty string');
  }

  const trimmed = expression.trim();

  if (trimmed.length === 0) {
    throw new ValidationError('Expression cannot be empty');
  }

  if (trimmed.length > LIMITS.MAX_EXPRESSION_LENGTH) {
    throw new ValidationError(
      `Expression exceeds maximum length of ${LIMITS.MAX_EXPRESSION_LENGTH} characters`
    );
  }

  return { valid: true, sanitized: trimmed };
}

/**
 * Check whether a MIME type represents an image.
 * @param {string} mimeType
 * @returns {boolean}
 */
export function isImageType(mimeType) {
  return SUPPORTED_IMAGE_FORMATS.includes(mimeType.toLowerCase());
}

/**
 * Check whether a MIME type represents a PDF.
 * @param {string} mimeType
 * @returns {boolean}
 */
export function isPdfType(mimeType) {
  return SUPPORTED_DOCUMENT_FORMATS.includes(mimeType.toLowerCase());
}
