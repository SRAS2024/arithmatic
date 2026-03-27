import { createLogger } from '../lib/logger.js';
import { orchestrate } from '../services/orchestrator.js';
import { validateMathInput, validateInputType } from '../lib/validators.js';
import { INPUT_TYPES } from '../lib/constants.js';
import { wrapError } from '../lib/errors.js';

const log = createLogger('API:Solve');

/**
 * HTTP endpoint handler for the solve route.
 * Validates input, delegates to the orchestrator, and returns results.
 *
 * @param {object} params - { input, inputType, options }
 * @returns {Promise<object>} Solve result.
 */
export async function handleSolve(params) {
  const { input, inputType, options = {} } = params;

  try {
    // Validate input type
    const normalizedType = validateInputType(inputType);

    // Validate typed input (file inputs are validated by the upload handler)
    if (normalizedType === INPUT_TYPES.TYPED) {
      validateMathInput(input);
    }

    // Delegate to orchestrator
    const result = await orchestrate({
      input,
      inputType: normalizedType,
      options,
    });

    return result;
  } catch (err) {
    const wrapped = wrapError(err);
    log.error(`Solve handler error: ${wrapped.message}`);
    return {
      success: false,
      error: wrapped.toJSON(),
    };
  }
}
