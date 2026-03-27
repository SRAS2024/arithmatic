import { createLogger } from '../lib/logger.js';
import { generateGraph } from '../services/graphService.js';
import { validateExpression } from '../lib/validators.js';
import { wrapError } from '../lib/errors.js';

const log = createLogger('API:Graph');

/**
 * Graph generation endpoint handler.
 *
 * @param {object} params - { expression, graphType, options }
 * @returns {Promise<object>}
 */
export async function handleGraph(params) {
  const { expression, graphType, options = {} } = params;

  try {
    validateExpression(expression);

    const result = await generateGraph(expression, graphType || 'line', options);

    return {
      success: true,
      image: result.image,
      format: result.format,
      mimeType: result.mimeType,
      metadata: result.metadata,
    };
  } catch (err) {
    const wrapped = wrapError(err);
    log.error(`Graph handler error: ${wrapped.message}`);
    return {
      success: false,
      error: wrapped.toJSON(),
    };
  }
}
