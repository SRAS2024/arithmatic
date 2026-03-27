import { validateEnv } from './env.js';
import { configureSecurity } from './security.js';
import { startTempCleanup } from './tempCleanup.js';
import { createLogger } from '../lib/logger.js';

const log = createLogger('Startup');

/**
 * Run all startup tasks in sequence.
 */
export function runStartup() {
  log.info('=== Arithmetic Math Solver - Server Starting ===');

  // 1. Validate and log environment configuration
  const cfg = validateEnv();

  // 2. Configure rate limiting and security
  configureSecurity();

  // 3. Start periodic temp file cleanup
  startTempCleanup();

  log.info('=== Server startup complete ===');
  return cfg;
}
