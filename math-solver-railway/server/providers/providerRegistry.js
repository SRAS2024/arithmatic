import { createLogger } from '../lib/logger.js';
import { PROVIDERS } from '../lib/constants.js';

const log = createLogger('ProviderRegistry');

/**
 * Central registry for all optional service providers.
 * Providers register themselves with a name, capabilities, and a health-check.
 */
class ProviderRegistry {
  constructor() {
    /** @type {Map<string, { name: string, provider: object, capabilities: string[], available: boolean }>} */
    this._providers = new Map();
  }

  /**
   * Register a provider instance.
   * @param {string} name - Unique provider name (use PROVIDERS constants).
   * @param {object} provider - Provider instance with an `isAvailable()` method.
   * @param {string[]} capabilities - List of capability tags (e.g. 'solve', 'ocr').
   */
  register(name, provider, capabilities = []) {
    const available = typeof provider.isAvailable === 'function'
      ? provider.isAvailable()
      : false;

    this._providers.set(name, {
      name,
      provider,
      capabilities,
      available,
    });

    log.info(`Provider registered: ${name} (available: ${available}, capabilities: ${capabilities.join(', ') || 'none'})`);
  }

  /**
   * Get a provider by name.
   * @param {string} name
   * @returns {object|null} The provider instance, or null if not found / unavailable.
   */
  get(name) {
    const entry = this._providers.get(name);
    if (!entry || !entry.available) return null;
    return entry.provider;
  }

  /**
   * Check whether a specific provider is available.
   * @param {string} name
   * @returns {boolean}
   */
  isAvailable(name) {
    const entry = this._providers.get(name);
    return entry ? entry.available : false;
  }

  /**
   * Get all providers that advertise a given capability.
   * @param {string} capability
   * @returns {object[]} Array of provider instances.
   */
  getByCapability(capability) {
    const results = [];
    for (const entry of this._providers.values()) {
      if (entry.available && entry.capabilities.includes(capability)) {
        results.push(entry.provider);
      }
    }
    return results;
  }

  /**
   * Return a summary of all registered providers and their status.
   * @returns {object[]}
   */
  listAll() {
    const list = [];
    for (const entry of this._providers.values()) {
      list.push({
        name: entry.name,
        available: entry.available,
        capabilities: entry.capabilities,
      });
    }
    return list;
  }

  /**
   * Re-check availability for all providers (e.g. if keys change at runtime).
   */
  refresh() {
    for (const entry of this._providers.values()) {
      if (typeof entry.provider.isAvailable === 'function') {
        entry.available = entry.provider.isAvailable();
      }
    }
    log.info('Provider availability refreshed');
  }
}

// Singleton
const registry = new ProviderRegistry();
export default registry;
