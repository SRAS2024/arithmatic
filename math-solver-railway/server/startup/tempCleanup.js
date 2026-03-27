import fs from 'fs';
import path from 'path';
import { config } from './env.js';
import { createLogger } from '../lib/logger.js';
import { LIMITS } from '../lib/constants.js';

const log = createLogger('TempCleanup');

/**
 * Remove files from the temp directory that are older than MAX_FILE_AGE_MS.
 */
function cleanupOldFiles() {
  const tempDir = config.TEMP_DIR;

  try {
    if (!fs.existsSync(tempDir)) {
      return;
    }

    const entries = fs.readdirSync(tempDir);
    const now = Date.now();
    let removedCount = 0;

    for (const entry of entries) {
      if (entry === '.gitkeep') continue;

      const fullPath = path.join(tempDir, entry);

      try {
        const stat = fs.statSync(fullPath);
        const ageMs = now - stat.mtimeMs;

        if (ageMs > LIMITS.MAX_FILE_AGE_MS) {
          if (stat.isDirectory()) {
            fs.rmSync(fullPath, { recursive: true, force: true });
          } else {
            fs.unlinkSync(fullPath);
          }
          removedCount++;
        }
      } catch (err) {
        log.warn(`Failed to process temp entry: ${entry}`, err.message);
      }
    }

    if (removedCount > 0) {
      log.info(`Cleaned up ${removedCount} expired temp file(s)`);
    }
  } catch (err) {
    log.error('Error during temp cleanup', err.message);
  }
}

/**
 * Start the periodic temp file cleanup process.
 */
export function startTempCleanup() {
  const tempDir = config.TEMP_DIR;

  // Ensure temp directory exists
  try {
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
      log.info(`Created temp directory: ${tempDir}`);
    }
  } catch (err) {
    log.error(`Failed to create temp directory: ${tempDir}`, err.message);
  }

  // Run an initial cleanup
  cleanupOldFiles();

  // Schedule periodic cleanup
  const intervalMs = config.CLEANUP_INTERVAL || LIMITS.CLEANUP_INTERVAL_MS;
  const intervalId = setInterval(cleanupOldFiles, intervalMs);

  log.info(
    `Temp cleanup scheduled every ${(intervalMs / 1000).toFixed(0)}s for ${tempDir}`
  );

  // Return the interval ID so it can be cleared if needed
  return intervalId;
}
