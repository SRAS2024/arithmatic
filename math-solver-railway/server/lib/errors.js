import { ERROR_CODES } from './constants.js';

/**
 * Base error class for the math solver application.
 */
export class AppError extends Error {
  constructor(message, code = ERROR_CODES.UNKNOWN_ERROR, details = null) {
    super(message);
    this.name = 'AppError';
    this.code = code;
    this.details = details;
    this.timestamp = new Date().toISOString();
  }

  toJSON() {
    return {
      error: true,
      name: this.name,
      code: this.code,
      message: this.message,
      details: this.details,
      timestamp: this.timestamp,
    };
  }
}

/**
 * Error thrown when math solving fails.
 */
export class SolverError extends AppError {
  constructor(message, details = null) {
    super(message, ERROR_CODES.SOLVE_ERROR, details);
    this.name = 'SolverError';
  }
}

/**
 * Error thrown when OCR processing fails.
 */
export class OCRError extends AppError {
  constructor(message, details = null) {
    super(message, ERROR_CODES.OCR_ERROR, details);
    this.name = 'OCRError';
  }
}

/**
 * Error thrown when file upload fails.
 */
export class UploadError extends AppError {
  constructor(message, details = null) {
    super(message, ERROR_CODES.UPLOAD_ERROR, details);
    this.name = 'UploadError';
  }
}

/**
 * Error thrown when parsing math expressions fails.
 */
export class ParseError extends AppError {
  constructor(message, details = null) {
    super(message, ERROR_CODES.PARSE_ERROR, details);
    this.name = 'ParseError';
  }
}

/**
 * Error thrown when a request times out.
 */
export class TimeoutError extends AppError {
  constructor(message = 'Request timed out', details = null) {
    super(message, ERROR_CODES.TIMEOUT_ERROR, details);
    this.name = 'TimeoutError';
  }
}

/**
 * Error thrown when input validation fails.
 */
export class ValidationError extends AppError {
  constructor(message, details = null) {
    super(message, ERROR_CODES.VALIDATION_ERROR, details);
    this.name = 'ValidationError';
  }
}

/**
 * Error thrown when an external service is unavailable.
 */
export class ServiceUnavailableError extends AppError {
  constructor(message = 'Service unavailable', details = null) {
    super(message, ERROR_CODES.SERVICE_UNAVAILABLE, details);
    this.name = 'ServiceUnavailableError';
  }
}

/**
 * Wrap an unknown error into an AppError.
 */
export function wrapError(err) {
  if (err instanceof AppError) {
    return err;
  }
  return new AppError(
    err.message || 'An unexpected error occurred',
    ERROR_CODES.UNKNOWN_ERROR,
    { originalError: err.name, stack: err.stack }
  );
}
