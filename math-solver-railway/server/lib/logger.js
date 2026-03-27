const LOG_LEVELS = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
};

const currentLevel = (process.env.LOG_LEVEL || 'info').toLowerCase();
const currentLevelValue = LOG_LEVELS[currentLevel] ?? LOG_LEVELS.info;

function formatTimestamp() {
  return new Date().toISOString();
}

function formatMessage(level, context, message, data) {
  const parts = [
    `[${formatTimestamp()}]`,
    `[${level.toUpperCase()}]`,
  ];
  if (context) {
    parts.push(`[${context}]`);
  }
  parts.push(message);
  return parts.join(' ');
}

function shouldLog(level) {
  return (LOG_LEVELS[level] ?? LOG_LEVELS.info) >= currentLevelValue;
}

/**
 * Create a logger instance with an optional context prefix.
 * @param {string} [context] - Context label (e.g. service name)
 * @returns {object} Logger with debug, info, warn, error methods.
 */
export function createLogger(context = '') {
  return {
    debug(message, data) {
      if (shouldLog('debug')) {
        const formatted = formatMessage('debug', context, message, data);
        if (data !== undefined) {
          console.log(formatted, data);
        } else {
          console.log(formatted);
        }
      }
    },

    info(message, data) {
      if (shouldLog('info')) {
        const formatted = formatMessage('info', context, message, data);
        if (data !== undefined) {
          console.info(formatted, data);
        } else {
          console.info(formatted);
        }
      }
    },

    warn(message, data) {
      if (shouldLog('warn')) {
        const formatted = formatMessage('warn', context, message, data);
        if (data !== undefined) {
          console.warn(formatted, data);
        } else {
          console.warn(formatted);
        }
      }
    },

    error(message, data) {
      if (shouldLog('error')) {
        const formatted = formatMessage('error', context, message, data);
        if (data !== undefined) {
          console.error(formatted, data);
        } else {
          console.error(formatted);
        }
      }
    },
  };
}

// Default logger
const logger = createLogger();

export default logger;
