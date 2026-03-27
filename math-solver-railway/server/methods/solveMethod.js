import { Meteor } from 'meteor/meteor';
import { createLogger } from '../lib/logger.js';
import { orchestrate } from '../services/orchestrator.js';
import { validateMathInput, validateInputType } from '../lib/validators.js';
import { INPUT_TYPES } from '../lib/constants.js';
import { wrapError } from '../lib/errors.js';

const log = createLogger('Method:Solve');

Meteor.methods({
  /**
   * Meteor method 'solve'.
   * Accepts { input, inputType, options } and runs the full solving pipeline.
   *
   * @param {object} params
   * @param {string} params.input - Math expression (typed) or base64 file data.
   * @param {string} params.inputType - One of: 'typed', 'image', 'pdf', 'handwritten'.
   * @param {object} [params.options] - Additional options:
   *   - stepByStep {boolean} - Include step-by-step solution (default true).
   *   - verify {boolean} - Verify the answer (default true).
   *   - crossVerify {boolean} - Use external provider for verification.
   *   - generateGraph {boolean} - Generate a graph of the expression.
   *   - graphType {string} - Type of graph to generate.
   *   - mimeType {string} - MIME type for image/pdf uploads.
   *   - language {string} - OCR language hint.
   * @returns {object} Unified result from the orchestrator.
   */
  async solve(params) {
    const { input, inputType, options = {} } = params || {};

    try {
      // Validate
      const normalizedType = validateInputType(inputType);

      if (normalizedType === INPUT_TYPES.TYPED) {
        const { sanitized } = validateMathInput(input);
        return await orchestrate({
          input: sanitized,
          inputType: normalizedType,
          options,
        });
      }

      // For file-based inputs, input should be base64 data
      if (!input || typeof input !== 'string' || input.length === 0) {
        throw new Meteor.Error('invalid-input', 'Input data is required for file-based solving');
      }

      return await orchestrate({
        input,
        inputType: normalizedType,
        options,
      });
    } catch (err) {
      if (err instanceof Meteor.Error) throw err;

      const wrapped = wrapError(err);
      log.error(`solve method error: ${wrapped.message}`);
      throw new Meteor.Error(wrapped.code, wrapped.message, wrapped.details);
    }
  },
});
