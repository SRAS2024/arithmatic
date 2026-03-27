import { createLogger } from '../lib/logger.js';
import { LIMITS } from '../lib/constants.js';

const log = createLogger('Config');

/**
 * Application configuration derived from environment variables.
 */
export const config = {
  PORT: parseInt(process.env.PORT, 10) || 3000,
  ROOT_URL: process.env.ROOT_URL || `http://localhost:${parseInt(process.env.PORT, 10) || 3000}`,
  PYTHON_SERVICE_URL: process.env.PYTHON_SERVICE_URL || 'http://localhost:5000',
  MAX_UPLOAD_SIZE: parseInt(process.env.MAX_UPLOAD_SIZE, 10) || LIMITS.MAX_UPLOAD_SIZE,
  TEMP_DIR: process.env.TEMP_DIR || '/tmp/arithmetic-solver',
  CLEANUP_INTERVAL: parseInt(process.env.CLEANUP_INTERVAL, 10) || LIMITS.CLEANUP_INTERVAL_MS,

  // Optional provider API keys
  OPENAI_API_KEY: process.env.OPENAI_API_KEY || '',
  WOLFRAM_APP_ID: process.env.WOLFRAM_APP_ID || '',
  MATHPIX_APP_ID: process.env.MATHPIX_APP_ID || '',
  MATHPIX_APP_KEY: process.env.MATHPIX_APP_KEY || '',

  LOG_LEVEL: process.env.LOG_LEVEL || 'info',
};

/**
 * Validate and log environment configuration on startup.
 */
export function validateEnv() {
  log.info('--- Environment Configuration ---');
  log.info(`  PORT:               ${config.PORT}`);
  log.info(`  ROOT_URL:           ${config.ROOT_URL}`);
  log.info(`  PYTHON_SERVICE_URL: ${config.PYTHON_SERVICE_URL}`);
  log.info(`  MAX_UPLOAD_SIZE:    ${(config.MAX_UPLOAD_SIZE / (1024 * 1024)).toFixed(1)}MB`);
  log.info(`  TEMP_DIR:           ${config.TEMP_DIR}`);
  log.info(`  CLEANUP_INTERVAL:   ${(config.CLEANUP_INTERVAL / 1000).toFixed(0)}s`);
  log.info(`  LOG_LEVEL:          ${config.LOG_LEVEL}`);

  // Log provider availability
  log.info('--- Provider Availability ---');
  log.info(`  OpenAI:   ${config.OPENAI_API_KEY ? 'configured' : 'not configured (optional)'}`);
  log.info(`  Wolfram:  ${config.WOLFRAM_APP_ID ? 'configured' : 'not configured (optional)'}`);
  log.info(`  Mathpix:  ${config.MATHPIX_APP_ID && config.MATHPIX_APP_KEY ? 'configured' : 'not configured (optional)'}`);
  log.info('--- End Configuration ---');

  // Warn about critical settings
  if (!process.env.PYTHON_SERVICE_URL) {
    log.warn('PYTHON_SERVICE_URL not set, using default: http://localhost:5000');
  }

  return config;
}
