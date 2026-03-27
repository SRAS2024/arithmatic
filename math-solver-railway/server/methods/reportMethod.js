import { Meteor } from 'meteor/meteor';
import { createLogger } from '../lib/logger.js';
import { generateReport } from '../services/reportService.js';
import { wrapError } from '../lib/errors.js';

const log = createLogger('Method:Report');

Meteor.methods({
  /**
   * Meteor method 'generateReport'.
   * Accepts solution data and returns a base64 encoded PDF or HTML report.
   *
   * @param {object} params
   * @param {object} params.solution - The solution object containing:
   *   - input {string} - Original problem text.
   *   - answer {string|number} - The answer.
   *   - steps {Array} - Step-by-step solution.
   *   - latex {string} - LaTeX representation.
   *   - problemType {string} - Problem type.
   *   - confidence {number} - Confidence score.
   *   - graphs {Array} - Any generated graphs.
   * @param {string} [params.format] - 'pdf' or 'html' (default 'pdf').
   * @param {object} [params.options] - Report options:
   *   - includeGraphs {boolean} - Include graphs (default true).
   *   - includeSteps {boolean} - Include steps (default true).
   *   - title {string} - Report title.
   * @returns {object} { data (base64), format, mimeType, filename }
   */
  async generateReport(params) {
    const { solution, format, options = {} } = params || {};

    try {
      if (!solution || !solution.answer) {
        throw new Meteor.Error(
          'invalid-input',
          'A solution object with at least an answer is required'
        );
      }

      const result = await generateReport(solution, format || 'pdf', options);

      log.info(`Report generated: format=${result.format}, filename=${result.filename}`);

      return {
        data: result.data,
        format: result.format,
        mimeType: result.mimeType,
        filename: result.filename,
      };
    } catch (err) {
      if (err instanceof Meteor.Error) throw err;

      const wrapped = wrapError(err);
      log.error(`generateReport method error: ${wrapped.message}`);
      throw new Meteor.Error(wrapped.code, wrapped.message, wrapped.details);
    }
  },
});
