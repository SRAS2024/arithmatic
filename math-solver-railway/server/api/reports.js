import { createLogger } from '../lib/logger.js';
import { generateReport } from '../services/reportService.js';
import { wrapError } from '../lib/errors.js';

const log = createLogger('API:Reports');

/**
 * Report generation endpoint handler.
 *
 * @param {object} params - { solution, format, options }
 * @returns {Promise<object>}
 */
export async function handleReport(params) {
  const { solution, format, options = {} } = params;

  try {
    if (!solution || !solution.answer) {
      throw new Error('A solution with at least an answer is required to generate a report');
    }

    const result = await generateReport(solution, format || 'pdf', options);

    return {
      success: true,
      data: result.data,
      format: result.format,
      mimeType: result.mimeType,
      filename: result.filename,
    };
  } catch (err) {
    const wrapped = wrapError(err);
    log.error(`Report handler error: ${wrapped.message}`);
    return {
      success: false,
      error: wrapped.toJSON(),
    };
  }
}
