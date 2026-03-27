import { DDPRateLimiter } from 'meteor/ddp-rate-limiter';
import { createLogger } from '../lib/logger.js';

const log = createLogger('Security');

/**
 * Configure rate limiting for Meteor methods to prevent abuse.
 */
export function configureSecurity() {
  log.info('Configuring rate limiting for Meteor methods');

  // Rate limit all Meteor methods: max 30 calls per 10 seconds per connection
  const generalRule = {
    type: 'method',
    name(name) {
      // Apply to all defined methods
      return [
        'solve',
        'upload',
        'generateReport',
        'generateGraph',
      ].includes(name);
    },
    connectionId() {
      return true;
    },
  };

  DDPRateLimiter.addRule(generalRule, 30, 10000);

  // Stricter limit for solve: 10 per 10 seconds per connection
  DDPRateLimiter.addRule(
    {
      type: 'method',
      name: 'solve',
      connectionId() { return true; },
    },
    10,
    10000
  );

  // Stricter limit for upload: 5 per 10 seconds per connection
  DDPRateLimiter.addRule(
    {
      type: 'method',
      name: 'upload',
      connectionId() { return true; },
    },
    5,
    10000
  );

  // Report generation: 3 per 10 seconds per connection
  DDPRateLimiter.addRule(
    {
      type: 'method',
      name: 'generateReport',
      connectionId() { return true; },
    },
    3,
    10000
  );

  // Graph generation: 5 per 10 seconds per connection
  DDPRateLimiter.addRule(
    {
      type: 'method',
      name: 'generateGraph',
      connectionId() { return true; },
    },
    5,
    10000
  );

  log.info('Rate limiting configured successfully');
}
