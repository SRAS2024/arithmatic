import { createLogger } from '../lib/logger.js';
import { config } from '../startup/env.js';
import { OCRError, ServiceUnavailableError } from '../lib/errors.js';
import { LIMITS } from '../lib/constants.js';
import { serializePDFRequest, deserializePDFResponse } from '../lib/serializers.js';

const log = createLogger('PDFService');

/**
 * Send a PDF to the Python /pdf endpoint for text extraction.
 * Handles multi-page results and OCR fallback for scanned pages.
 *
 * @param {string} pdfData - Base64 encoded PDF data.
 * @param {object} [options] - { pages, ocrFallback, language }
 * @returns {Promise<object>} { pages: [...], totalPages, combinedText }
 */
export async function extractFromPDF(pdfData, options = {}) {
  log.info(`PDF extraction request: dataLength=${pdfData.length}`);

  const rawData = pdfData.includes(',') ? pdfData.split(',')[1] : pdfData;

  const body = serializePDFRequest({ pdfData: rawData, options });
  const url = `${config.PYTHON_SERVICE_URL}/pdf`;

  const controller = new AbortController();
  const timeout = setTimeout(
    () => controller.abort(),
    options.timeout || LIMITS.SOLVE_TIMEOUT_MS // PDFs may be large
  );

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: controller.signal,
    });

    if (!res.ok) {
      const errBody = await res.text().catch(() => '');
      throw new Error(`PDF endpoint returned ${res.status}: ${errBody}`);
    }

    const raw = await res.json();
    const result = deserializePDFResponse(raw);

    log.info(`PDF extraction complete: ${result.totalPages} page(s), text length: ${result.combinedText.length}`);

    // If combined text is empty, all pages may be scanned images
    if (!result.combinedText && result.pages.length > 0) {
      log.warn('PDF text extraction returned empty text - pages may be scanned images');
    }

    return result;
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new OCRError('PDF extraction timed out', {
        timeout: options.timeout || LIMITS.SOLVE_TIMEOUT_MS,
      });
    }
    if (err instanceof OCRError) throw err;

    throw new ServiceUnavailableError(
      `PDF extraction service unreachable: ${err.message}`,
      { url, originalError: err.message }
    );
  } finally {
    clearTimeout(timeout);
  }
}

/**
 * Extract and merge text from specific pages of a PDF extraction result.
 * @param {object} pdfResult - Result from extractFromPDF.
 * @param {number[]} [pageNumbers] - Page numbers to include (1-based). If empty, all pages.
 * @returns {string} Merged text.
 */
export function getTextFromPages(pdfResult, pageNumbers = []) {
  if (!pdfResult || !pdfResult.pages) return '';

  const pages = pageNumbers.length > 0
    ? pdfResult.pages.filter((p) => pageNumbers.includes(p.pageNumber))
    : pdfResult.pages;

  return pages.map((p) => p.text).filter(Boolean).join('\n\n');
}
