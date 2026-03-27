import { Meteor } from 'meteor/meteor';
import { createLogger } from '../lib/logger.js';
import { generateGraph } from '../services/graphService.js';
import { validateExpression } from '../lib/validators.js';
import { wrapError } from '../lib/errors.js';

const log = createLogger('Method:Graph');

Meteor.methods({
  /**
   * Meteor method 'generateGraph'.
   * Accepts an expression and options, returns a base64 encoded graph image.
   *
   * @param {object} params
   * @param {string} params.expression - The math expression to graph.
   * @param {string} [params.graphType] - Graph type: 'line', 'scatter', 'bar', 'polar', 'parametric', 'implicit'.
   * @param {object} [params.options] - Graph options:
   *   - xRange {number[]} - X axis range [min, max] (default [-10, 10]).
   *   - yRange {number[]} - Y axis range [min, max] (default [-10, 10]).
   *   - width {number} - Image width in px (default 800).
   *   - height {number} - Image height in px (default 600).
   *   - title {string} - Graph title.
   *   - format {string} - Image format ('png' or 'svg').
   * @returns {object} { image (base64), format, mimeType, metadata }
   */
  async generateGraph(params) {
    const { expression, graphType, options = {} } = params || {};

    try {
      // Validate expression
      const { sanitized } = validateExpression(expression);

      const result = await generateGraph(sanitized, graphType || 'line', options);

      log.info(`Graph generated for: "${sanitized.substring(0, 40)}"`);

      return {
        image: result.image,
        format: result.format,
        mimeType: result.mimeType,
        metadata: result.metadata,
      };
    } catch (err) {
      if (err instanceof Meteor.Error) throw err;

      const wrapped = wrapError(err);
      log.error(`generateGraph method error: ${wrapped.message}`);
      throw new Meteor.Error(wrapped.code, wrapped.message, wrapped.details);
    }
  },
});
