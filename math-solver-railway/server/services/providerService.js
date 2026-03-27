import { createLogger } from '../lib/logger.js';
import { PROVIDERS } from '../lib/constants.js';
import registry from '../providers/providerRegistry.js';
import openaiProvider from '../providers/openaiProvider.js';
import wolframProvider from '../providers/wolframProvider.js';
import mathpixProvider from '../providers/mathpixProvider.js';
import genericOcrProvider from '../providers/genericOcrProvider.js';

const log = createLogger('ProviderService');

let _initialized = false;

/**
 * Initialize and register all providers with the registry.
 * Safe to call multiple times - only runs once.
 */
export function initializeProviders() {
  if (_initialized) return;

  log.info('Initializing providers...');

  registry.register(PROVIDERS.OPENAI, openaiProvider, ['solve', 'ocr', 'vision']);
  registry.register(PROVIDERS.WOLFRAM, wolframProvider, ['solve', 'verify']);
  registry.register(PROVIDERS.MATHPIX, mathpixProvider, ['ocr', 'handwriting']);
  registry.register(PROVIDERS.GENERIC_OCR, genericOcrProvider, ['ocr']);

  _initialized = true;
  log.info('All providers initialized');
}

/**
 * Get the best available OCR provider.
 * Priority: Mathpix > OpenAI > Generic
 * @returns {object|null}
 */
export function getOCRProvider() {
  initializeProviders();

  if (registry.isAvailable(PROVIDERS.MATHPIX)) {
    return registry.get(PROVIDERS.MATHPIX);
  }
  if (registry.isAvailable(PROVIDERS.OPENAI)) {
    return registry.get(PROVIDERS.OPENAI);
  }
  return registry.get(PROVIDERS.GENERIC_OCR);
}

/**
 * Get the best available solver provider (used as fallback / verification).
 * @returns {object|null}
 */
export function getSolverProvider() {
  initializeProviders();

  if (registry.isAvailable(PROVIDERS.OPENAI)) {
    return registry.get(PROVIDERS.OPENAI);
  }
  if (registry.isAvailable(PROVIDERS.WOLFRAM)) {
    return registry.get(PROVIDERS.WOLFRAM);
  }
  return null;
}

/**
 * Get the best available verification provider.
 * @returns {object|null}
 */
export function getVerificationProvider() {
  initializeProviders();

  if (registry.isAvailable(PROVIDERS.WOLFRAM)) {
    return registry.get(PROVIDERS.WOLFRAM);
  }
  if (registry.isAvailable(PROVIDERS.OPENAI)) {
    return registry.get(PROVIDERS.OPENAI);
  }
  return null;
}

/**
 * Get the best available handwriting OCR provider.
 * @returns {object|null}
 */
export function getHandwritingProvider() {
  initializeProviders();

  if (registry.isAvailable(PROVIDERS.MATHPIX)) {
    return registry.get(PROVIDERS.MATHPIX);
  }
  if (registry.isAvailable(PROVIDERS.OPENAI)) {
    return registry.get(PROVIDERS.OPENAI);
  }
  return null;
}

/**
 * Return a summary of provider availability for the capabilities endpoint.
 * @returns {object[]}
 */
export function getProviderSummary() {
  initializeProviders();
  return registry.listAll();
}
