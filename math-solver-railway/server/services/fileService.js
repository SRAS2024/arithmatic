import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { createLogger } from '../lib/logger.js';
import { config } from '../startup/env.js';
import { UploadError } from '../lib/errors.js';

const log = createLogger('FileService');

/**
 * Ensure the temp directory exists and is writable.
 */
function ensureTempDir() {
  const dir = config.TEMP_DIR;
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  return dir;
}

/**
 * Save base64-encoded file data to a temporary file.
 *
 * @param {string} base64Data - File content in base64 (may include data URI prefix).
 * @param {string} originalName - Original filename for extension extraction.
 * @param {string} [mimeType] - MIME type.
 * @returns {{ filePath: string, fileId: string, size: number }}
 */
export function saveTempFile(base64Data, originalName, mimeType) {
  const tempDir = ensureTempDir();

  // Strip data URI prefix
  const raw = base64Data.includes(',') ? base64Data.split(',')[1] : base64Data;
  const buffer = Buffer.from(raw, 'base64');

  // Generate a unique ID
  const fileId = crypto.randomUUID();
  const ext = path.extname(originalName || '') || mimeToExt(mimeType);
  const fileName = `${fileId}${ext}`;
  const filePath = path.join(tempDir, fileName);

  try {
    fs.writeFileSync(filePath, buffer);
    log.debug(`Saved temp file: ${filePath} (${buffer.length} bytes)`);
  } catch (err) {
    throw new UploadError(`Failed to save temp file: ${err.message}`);
  }

  return { filePath, fileId, size: buffer.length };
}

/**
 * Read a temp file and return its base64 content.
 * @param {string} fileId - The file ID returned by saveTempFile.
 * @returns {string|null} Base64 encoded content, or null if not found.
 */
export function readTempFile(fileId) {
  const tempDir = config.TEMP_DIR;

  try {
    const entries = fs.readdirSync(tempDir);
    const match = entries.find((e) => e.startsWith(fileId));
    if (!match) return null;

    const filePath = path.join(tempDir, match);
    const buffer = fs.readFileSync(filePath);
    return buffer.toString('base64');
  } catch (err) {
    log.warn(`Failed to read temp file ${fileId}: ${err.message}`);
    return null;
  }
}

/**
 * Delete a temp file by ID.
 * @param {string} fileId
 * @returns {boolean} True if deleted, false otherwise.
 */
export function deleteTempFile(fileId) {
  const tempDir = config.TEMP_DIR;

  try {
    const entries = fs.readdirSync(tempDir);
    const match = entries.find((e) => e.startsWith(fileId));
    if (!match) return false;

    fs.unlinkSync(path.join(tempDir, match));
    log.debug(`Deleted temp file: ${match}`);
    return true;
  } catch (err) {
    log.warn(`Failed to delete temp file ${fileId}: ${err.message}`);
    return false;
  }
}

/**
 * Generate a temporary URL path for accessing a temp file.
 * In a real deployment this would generate a signed URL.
 * Here we return a relative path that the server can serve.
 *
 * @param {string} fileId
 * @returns {string} URL path
 */
export function getTempFileUrl(fileId) {
  return `/api/files/${fileId}`;
}

/**
 * List all temp files with metadata.
 * @returns {Array<{ fileId: string, name: string, size: number, age: number }>}
 */
export function listTempFiles() {
  const tempDir = config.TEMP_DIR;

  try {
    if (!fs.existsSync(tempDir)) return [];

    const entries = fs.readdirSync(tempDir);
    const now = Date.now();

    return entries
      .filter((e) => e !== '.gitkeep')
      .map((name) => {
        try {
          const stat = fs.statSync(path.join(tempDir, name));
          const fileId = path.parse(name).name;
          return {
            fileId,
            name,
            size: stat.size,
            age: now - stat.mtimeMs,
          };
        } catch {
          return null;
        }
      })
      .filter(Boolean);
  } catch (err) {
    log.warn(`Failed to list temp files: ${err.message}`);
    return [];
  }
}

/**
 * Map common MIME types to file extensions.
 */
function mimeToExt(mimeType) {
  const map = {
    'image/png': '.png',
    'image/jpeg': '.jpg',
    'image/jpg': '.jpg',
    'image/gif': '.gif',
    'image/bmp': '.bmp',
    'image/webp': '.webp',
    'image/tiff': '.tiff',
    'application/pdf': '.pdf',
  };
  return map[mimeType] || '.bin';
}
