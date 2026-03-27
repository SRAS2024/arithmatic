import { createLogger } from '../lib/logger.js';
import { config } from '../startup/env.js';
import { LIMITS } from '../lib/constants.js';

const log = createLogger('OpenAI');

/**
 * OpenAI API integration for math solving and OCR assistance.
 * Degrades gracefully if no API key is configured.
 */
class OpenAIProvider {
  constructor() {
    this._apiKey = config.OPENAI_API_KEY;
    this._baseUrl = 'https://api.openai.com/v1';
  }

  /** @returns {boolean} */
  isAvailable() {
    return Boolean(this._apiKey);
  }

  /**
   * Send a chat completion request to OpenAI.
   * @param {string} systemPrompt
   * @param {string} userMessage
   * @param {object} [options]
   * @returns {Promise<string>} The assistant reply text.
   */
  async _chatCompletion(systemPrompt, userMessage, options = {}) {
    if (!this.isAvailable()) {
      throw new Error('OpenAI API key not configured');
    }

    const model = options.model || 'gpt-4o';
    const temperature = options.temperature ?? 0.1;

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), options.timeout || LIMITS.REQUEST_TIMEOUT_MS);

    try {
      const res = await fetch(`${this._baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${this._apiKey}`,
        },
        body: JSON.stringify({
          model,
          temperature,
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userMessage },
          ],
          max_tokens: options.maxTokens || 2048,
        }),
        signal: controller.signal,
      });

      if (!res.ok) {
        const body = await res.text();
        throw new Error(`OpenAI API error ${res.status}: ${body}`);
      }

      const data = await res.json();
      return data.choices?.[0]?.message?.content ?? '';
    } finally {
      clearTimeout(timeout);
    }
  }

  /**
   * Use OpenAI to solve a math expression with step-by-step reasoning.
   * @param {string} expression
   * @param {object} [options]
   * @returns {Promise<object>}
   */
  async solve(expression, options = {}) {
    log.debug(`Solving via OpenAI: ${expression}`);

    const systemPrompt = `You are a precise mathematics solver. Given a math problem, return a JSON object with:
{
  "answer": "<final answer>",
  "steps": ["step 1", "step 2", ...],
  "latex": "<LaTeX representation of the answer>",
  "problem_type": "<type>",
  "confidence": <0.0-1.0>,
  "method": "<method used>"
}
Return ONLY valid JSON, no markdown fences.`;

    const reply = await this._chatCompletion(systemPrompt, expression, options);

    try {
      return JSON.parse(reply);
    } catch {
      log.warn('OpenAI response was not valid JSON, returning raw text');
      return {
        answer: reply.trim(),
        steps: [],
        latex: null,
        problem_type: 'unknown',
        confidence: 0.5,
        method: 'openai-raw',
      };
    }
  }

  /**
   * Use OpenAI vision to extract math from an image.
   * @param {string} base64Image - Base64 encoded image data
   * @param {string} mimeType
   * @param {object} [options]
   * @returns {Promise<object>}
   */
  async ocrImage(base64Image, mimeType, options = {}) {
    if (!this.isAvailable()) {
      throw new Error('OpenAI API key not configured');
    }

    log.debug('Performing OCR via OpenAI Vision');

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), options.timeout || LIMITS.OCR_TIMEOUT_MS);

    try {
      const res = await fetch(`${this._baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${this._apiKey}`,
        },
        body: JSON.stringify({
          model: 'gpt-4o',
          temperature: 0,
          messages: [
            {
              role: 'system',
              content: 'Extract all mathematical expressions and text from this image. Return JSON: {"text": "<plain text>", "latex": "<LaTeX>", "confidence": <0-1>}. Return ONLY valid JSON.',
            },
            {
              role: 'user',
              content: [
                {
                  type: 'image_url',
                  image_url: {
                    url: `data:${mimeType};base64,${base64Image}`,
                  },
                },
              ],
            },
          ],
          max_tokens: 1024,
        }),
        signal: controller.signal,
      });

      if (!res.ok) {
        const body = await res.text();
        throw new Error(`OpenAI Vision API error ${res.status}: ${body}`);
      }

      const data = await res.json();
      const content = data.choices?.[0]?.message?.content ?? '';

      try {
        return JSON.parse(content);
      } catch {
        return { text: content.trim(), latex: null, confidence: 0.5 };
      }
    } finally {
      clearTimeout(timeout);
    }
  }
}

const openaiProvider = new OpenAIProvider();
export default openaiProvider;
