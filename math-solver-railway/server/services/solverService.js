import { createLogger } from '../lib/logger.js';
import { config } from '../startup/env.js';
import { SolverError, ServiceUnavailableError } from '../lib/errors.js';
import { LIMITS } from '../lib/constants.js';
import {
  serializeSolveRequest,
  deserializeSolveResponse,
} from '../lib/serializers.js';

const log = createLogger('SolverService');

/**
 * Send a math expression to the Python /solve endpoint.
 * @param {string} expression - The math expression to solve.
 * @param {string} problemType - Detected or specified problem type.
 * @param {object} [options] - Additional options (stepByStep, simplify, etc.)
 * @returns {Promise<object>} Deserialized solve result.
 */
export async function solve(expression, problemType, options = {}) {
  log.info(`Solving: "${expression.substring(0, 80)}..." (type: ${problemType})`);

  const body = serializeSolveRequest({ expression, problemType, options });
  const url = `${config.PYTHON_SERVICE_URL}/solve`;

  const controller = new AbortController();
  const timeout = setTimeout(
    () => controller.abort(),
    options.timeout || LIMITS.SOLVE_TIMEOUT_MS
  );

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: controller.signal,
    });

    if (!res.ok) {
      const errBody = await res.text().catch(() => 'Unknown error');
      throw new SolverError(
        `Python solve service returned ${res.status}: ${errBody}`,
        { statusCode: res.status, response: errBody }
      );
    }

    const raw = await res.json();
    const result = deserializeSolveResponse(raw);

    log.info(`Solve completed. Answer: "${(result.answer || '').substring(0, 80)}"`);
    return result;
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new SolverError('Solve request timed out', {
        timeout: options.timeout || LIMITS.SOLVE_TIMEOUT_MS,
      });
    }
    if (err instanceof SolverError) {
      throw err;
    }
    // Network error - service likely unreachable
    throw new ServiceUnavailableError(
      `Python solve service unreachable: ${err.message}`,
      { url, originalError: err.message }
    );
  } finally {
    clearTimeout(timeout);
  }
}
