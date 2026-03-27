import { createLogger } from '../lib/logger.js';
import { config } from '../startup/env.js';
import { SolverError, ServiceUnavailableError } from '../lib/errors.js';
import { LIMITS } from '../lib/constants.js';
import { serializeGraphRequest, deserializeGraphResponse } from '../lib/serializers.js';

const log = createLogger('GraphService');

/**
 * Request a graph from the Python /graph endpoint.
 *
 * @param {string} expression - The mathematical expression to graph.
 * @param {string} graphType - Graph type (line, scatter, polar, etc.)
 * @param {object} [options] - { xRange, yRange, width, height, title, format }
 * @returns {Promise<object>} { image (base64), format, mimeType, metadata }
 */
export async function generateGraph(expression, graphType, options = {}) {
  log.info(`Graph request: type=${graphType}, expression="${expression.substring(0, 60)}"`);

  const body = serializeGraphRequest({ expression, graphType, options });
  const url = `${config.PYTHON_SERVICE_URL}/graph`;

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeout || LIMITS.REQUEST_TIMEOUT_MS);

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: controller.signal,
    });

    if (!res.ok) {
      const errBody = await res.text().catch(() => '');
      throw new SolverError(
        `Graph service returned ${res.status}: ${errBody}`,
        { statusCode: res.status }
      );
    }

    const raw = await res.json();
    const result = deserializeGraphResponse(raw);

    if (!result || !result.image) {
      throw new SolverError('Graph service returned an empty image');
    }

    log.info(`Graph generated: format=${result.format}`);
    return result;
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new SolverError('Graph generation timed out');
    }
    if (err instanceof SolverError) throw err;

    throw new ServiceUnavailableError(
      `Graph service unreachable: ${err.message}`,
      { url, originalError: err.message }
    );
  } finally {
    clearTimeout(timeout);
  }
}
