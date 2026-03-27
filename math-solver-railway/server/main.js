import { Meteor } from 'meteor/meteor';
import { runStartup } from './startup/index.js';

// Import all Meteor methods (side-effect: registers them)
import './methods/solveMethod.js';
import './methods/uploadMethod.js';
import './methods/reportMethod.js';
import './methods/graphMethod.js';

// Import API handlers (available for HTTP routes if needed)
import './api/index.js';

Meteor.startup(() => {
  runStartup();
});
