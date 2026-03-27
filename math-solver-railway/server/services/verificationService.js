import { createLogger } from '../lib/logger.js';
import { config } from '../startup/env.js';
import { LIMITS } from '../lib/constants.js';
import {
  serializeVerificationRequest,
  deserializeVerificationResponse,
} from '../lib/serializers.js';
import { getVerificationProvider } from './providerService.js';

const log = createLogger('VerificationService');

/**
 * Verify a math solution by calling the Python /verify endpoint.
 * Optionally cross-checks with an external provider (Wolfram, OpenAI).
 *
 * @param {string} expression - Original math expression.
 * @param {string} answer - The answer to verify.
 * @param {string} problemType
 * @param {object} [options]
 * @returns {Promise<object>} { verified, confidence, method, notes, alternativeAnswer }
 */
export async function verify(expression, answer, problemType, options = {}) {
  log.info(`Verifying answer for: "${expression.substring(0, 60)}..."`);

  const results = {
    pythonVerification: null,
    providerVerification: null,
    combined: null,
  };

  // 1. Try the Python service first
  try {
    results.pythonVerification = await verifyWithPython(expression, answer, problemType, options);
  } catch (err) {
    log.warn('Python verification failed', err.message);
    results.pythonVerification = {
      verified: false,
      confidence: 0,
      method: 'python-service',
      notes: `Python verification unavailable: ${err.message}`,
    };
  }

  // 2. Try an external provider for cross-verification (if available and requested)
  if (options.crossVerify !== false) {
    try {
      const provider = getVerificationProvider();
      if (provider && typeof provider.verify === 'function') {
        results.providerVerification = await provider.verify(expression, answer);
      }
    } catch (err) {
      log.warn('Provider cross-verification failed', err.message);
    }
  }

  // 3. Combine results
  results.combined = combineVerification(results.pythonVerification, results.providerVerification);

  log.info(`Verification result: verified=${results.combined.verified}, confidence=${results.combined.confidence}`);

  return results.combined;
}

/**
 * Call the Python /verify endpoint.
 */
async function verifyWithPython(expression, answer, problemType, options = {}) {
  const body = serializeVerificationRequest({ expression, answer, problemType });
  const url = `${config.PYTHON_SERVICE_URL}/verify`;

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeout || LIMITS.REQUEST_TIMEOUT_MS);

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: controller.signal,
    });

    if (!res.ok) {
      const errBody = await res.text().catch(() => '');
      throw new Error(`Verify endpoint returned ${res.status}: ${errBody}`);
    }

    const raw = await res.json();
    return deserializeVerificationResponse(raw);
  } finally {
    clearTimeout(timeout);
  }
}

/**
 * Combine Python and external provider verification results into a single
 * unified result. Uses the higher confidence source as primary.
 */
function combineVerification(pythonResult, providerResult) {
  // Only Python result available
  if (!providerResult) {
    return formatResult(pythonResult);
  }

  // Only provider result available
  if (!pythonResult || pythonResult.confidence === 0) {
    return formatResult(providerResult);
  }

  // Both available - combine
  const pyConf = pythonResult.confidence || 0;
  const provConf = providerResult.confidence || 0;

  const bothAgree = pythonResult.verified === providerResult.verified;

  let combinedConfidence;
  let verified;
  let notes;

  if (bothAgree) {
    combinedConfidence = Math.min(1, (pyConf + provConf) / 2 + 0.1);
    verified = pythonResult.verified;
    notes = `Verified by multiple sources (Python service + ${providerResult.method || 'external provider'})`;
  } else {
    // Disagreement - trust the higher-confidence source
    if (pyConf >= provConf) {
      verified = pythonResult.verified;
      combinedConfidence = pyConf * 0.7;
      notes = `Sources disagree. Primary (Python, conf=${pyConf.toFixed(2)}) says ${verified}. Secondary says ${providerResult.verified}.`;
    } else {
      verified = providerResult.verified;
      combinedConfidence = provConf * 0.7;
      notes = `Sources disagree. Primary (${providerResult.method}, conf=${provConf.toFixed(2)}) says ${verified}. Python says ${pythonResult.verified}.`;
    }
  }

  return {
    verified,
    confidence: Math.round(combinedConfidence * 100) / 100,
    method: 'combined',
    notes,
    alternativeAnswer: providerResult.alternativeAnswer || pythonResult.alternativeAnswer || null,
  };
}

/**
 * Ensure a result object has all expected fields.
 */
function formatResult(result) {
  if (!result) {
    return {
      verified: false,
      confidence: 0,
      method: 'none',
      notes: 'No verification available',
      alternativeAnswer: null,
    };
  }
  return {
    verified: result.verified ?? false,
    confidence: result.confidence ?? 0,
    method: result.method ?? 'unknown',
    notes: result.notes ?? '',
    alternativeAnswer: result.alternativeAnswer ?? null,
  };
}
