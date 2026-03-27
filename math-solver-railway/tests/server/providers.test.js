/**
 * Arithmetic - Provider Registry Tests
 */

if (Meteor.isServer) {
  import { Tinytest } from 'meteor/tinytest';

  Tinytest.add('Providers - registry initializes', function (test) {
    const { ProviderRegistry } = require('../../server/providers/providerRegistry');
    test.isNotNull(ProviderRegistry);
    test.isTrue(typeof ProviderRegistry.getAvailableProviders === 'function');
  });

  Tinytest.add('Providers - lists capabilities', function (test) {
    const { ProviderRegistry } = require('../../server/providers/providerRegistry');
    const providers = ProviderRegistry.getAvailableProviders();
    test.isTrue(Array.isArray(providers));
  });

  Tinytest.add('Providers - python provider always available', function (test) {
    const { ProviderRegistry } = require('../../server/providers/providerRegistry');
    const providers = ProviderRegistry.getAvailableProviders();
    const hasPython = providers.some(p => p.name === 'python');
    test.isTrue(hasPython, 'Python provider should always be available');
  });
}
