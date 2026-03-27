import { createLogger } from '../lib/logger.js';
import { config } from '../startup/env.js';
import { VERSION } from '../lib/constants.js';

const log = createLogger('Health');

/**
 * Health check handler.
 * Pings the Python service and returns overall system health.
 *
 * @returns {Promise<object>}
 */
export async function healthCheck() {
  const result = {
    status: 'ok',
    timestamp: new Date().toISOString(),
    version: VERSION,
    services: {
      meteor: { status: 'ok' },
      python: { status: 'unknown' },
    },
  };

  // Ping the Python service
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);

    const res = await fetch(`${config.PYTHON_SERVICE_URL}/health`, {
      method: 'GET',
      signal: controller.signal,
    });

    clearTimeout(timeout);

    if (res.ok) {
      const data = await res.json().catch(() => ({}));
      result.services.python = {
        status: 'ok',
        responseTime: data.response_time || null,
        version: data.version || null,
      };
    } else {
      result.services.python = {
        status: 'degraded',
        statusCode: res.status,
      };
      result.status = 'degraded';
    }
  } catch (err) {
    result.services.python = {
      status: 'unavailable',
      error: err.message,
    };
    result.status = 'degraded';
    log.warn('Python service health check failed', err.message);
  }

  return result;
}
