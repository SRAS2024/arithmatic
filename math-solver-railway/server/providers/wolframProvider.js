import { createLogger } from '../lib/logger.js';
import { config } from '../startup/env.js';
import { LIMITS } from '../lib/constants.js';

const log = createLogger('Wolfram');

/**
 * Wolfram Alpha integration for verification and alternative solving.
 * Degrades gracefully if no App ID is configured.
 */
class WolframProvider {
  constructor() {
    this._appId = config.WOLFRAM_APP_ID;
    this._baseUrl = 'https://api.wolframalpha.com/v2';
  }

  /** @returns {boolean} */
  isAvailable() {
    return Boolean(this._appId);
  }

  /**
   * Query the Wolfram Alpha Full Results API.
   * @param {string} input - Math expression or question.
   * @param {object} [options]
   * @returns {Promise<object>} Parsed result with answer, pods, etc.
   */
  async query(input, options = {}) {
    if (!this.isAvailable()) {
      throw new Error('Wolfram Alpha App ID not configured');
    }

    log.debug(`Querying Wolfram Alpha: ${input}`);

    const params = new URLSearchParams({
      appid: this._appId,
      input,
      format: 'plaintext,mathml',
      output: 'json',
    });

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), options.timeout || LIMITS.REQUEST_TIMEOUT_MS);

    try {
      const res = await fetch(`${this._baseUrl}/query?${params.toString()}`, {
        method: 'GET',
        signal: controller.signal,
      });

      if (!res.ok) {
        throw new Error(`Wolfram API error: ${res.status}`);
      }

      const data = await res.json();
      return this._parseResponse(data);
    } finally {
      clearTimeout(timeout);
    }
  }

  /**
   * Use the Short Answers API for a quick result.
   * @param {string} input
   * @param {object} [options]
   * @returns {Promise<string>}
   */
  async shortAnswer(input, options = {}) {
    if (!this.isAvailable()) {
      throw new Error('Wolfram Alpha App ID not configured');
    }

    const params = new URLSearchParams({
      appid: this._appId,
      i: input,
    });

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), options.timeout || LIMITS.REQUEST_TIMEOUT_MS);

    try {
      const res = await fetch(
        `https://api.wolframalpha.com/v1/result?${params.toString()}`,
        { method: 'GET', signal: controller.signal }
      );

      if (!res.ok) {
        throw new Error(`Wolfram Short Answers API error: ${res.status}`);
      }

      return await res.text();
    } finally {
      clearTimeout(timeout);
    }
  }

  /**
   * Verify an answer using Wolfram Alpha.
   * @param {string} expression
   * @param {string} expectedAnswer
   * @returns {Promise<object>}
   */
  async verify(expression, expectedAnswer) {
    try {
      const result = await this.query(expression);

      const wolframAnswer = result.answer || '';
      const normalizedExpected = expectedAnswer.toString().trim().toLowerCase();
      const normalizedWolfram = wolframAnswer.toString().trim().toLowerCase();

      const matches =
        normalizedExpected === normalizedWolfram ||
        normalizedWolfram.includes(normalizedExpected) ||
        normalizedExpected.includes(normalizedWolfram);

      return {
        verified: matches,
        wolframAnswer: wolframAnswer,
        confidence: matches ? 0.95 : 0.5,
        method: 'wolfram-alpha',
        notes: matches
          ? 'Answer verified by Wolfram Alpha'
          : `Wolfram Alpha returned: "${wolframAnswer}"`,
      };
    } catch (err) {
      log.warn('Wolfram verification failed', err.message);
      return {
        verified: false,
        confidence: 0,
        method: 'wolfram-alpha',
        notes: `Verification unavailable: ${err.message}`,
      };
    }
  }

  /**
   * Parse the full results API response.
   * @param {object} data
   * @returns {object}
   */
  _parseResponse(data) {
    const queryResult = data.queryresult || {};
    const pods = queryResult.pods || [];

    let answer = '';
    const steps = [];

    for (const pod of pods) {
      const title = pod.title || '';
      const subpods = pod.subpods || [];
      const text = subpods.map((s) => s.plaintext).filter(Boolean).join('; ');

      if (title.toLowerCase().includes('result') || title.toLowerCase().includes('solution')) {
        answer = answer || text;
      }

      if (text) {
        steps.push({ title, text });
      }
    }

    return {
      success: queryResult.success !== false,
      answer,
      steps,
      numpods: queryResult.numpods || 0,
      timing: queryResult.timing || null,
    };
  }
}

const wolframProvider = new WolframProvider();
export default wolframProvider;
