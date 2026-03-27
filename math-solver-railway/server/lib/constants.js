// Problem type constants
export const PROBLEM_TYPES = {
  ARITHMETIC: 'arithmetic',
  ALGEBRA: 'algebra',
  CALCULUS: 'calculus',
  TRIGONOMETRY: 'trigonometry',
  STATISTICS: 'statistics',
  LINEAR_ALGEBRA: 'linear_algebra',
  GEOMETRY: 'geometry',
  NUMBER_THEORY: 'number_theory',
  DIFFERENTIAL_EQUATIONS: 'differential_equations',
  UNKNOWN: 'unknown',
};

// Input type constants
export const INPUT_TYPES = {
  TYPED: 'typed',
  IMAGE: 'image',
  PDF: 'pdf',
  HANDWRITTEN: 'handwritten',
};

// Error codes
export const ERROR_CODES = {
  PARSE_ERROR: 'PARSE_ERROR',
  SOLVE_ERROR: 'SOLVE_ERROR',
  OCR_ERROR: 'OCR_ERROR',
  UPLOAD_ERROR: 'UPLOAD_ERROR',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  SERVICE_UNAVAILABLE: 'SERVICE_UNAVAILABLE',
  PROVIDER_ERROR: 'PROVIDER_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',
  RATE_LIMIT_ERROR: 'RATE_LIMIT_ERROR',
  FILE_TOO_LARGE: 'FILE_TOO_LARGE',
  UNSUPPORTED_FORMAT: 'UNSUPPORTED_FORMAT',
};

// Supported file formats
export const SUPPORTED_IMAGE_FORMATS = [
  'image/png',
  'image/jpeg',
  'image/jpg',
  'image/gif',
  'image/bmp',
  'image/webp',
  'image/tiff',
];

export const SUPPORTED_DOCUMENT_FORMATS = [
  'application/pdf',
];

export const ALL_SUPPORTED_FORMATS = [
  ...SUPPORTED_IMAGE_FORMATS,
  ...SUPPORTED_DOCUMENT_FORMATS,
];

// Limits
export const LIMITS = {
  MAX_UPLOAD_SIZE: 20 * 1024 * 1024, // 20MB
  MAX_INPUT_LENGTH: 10000,
  MAX_EXPRESSION_LENGTH: 5000,
  MAX_FILE_AGE_MS: 60 * 60 * 1000, // 1 hour
  CLEANUP_INTERVAL_MS: 10 * 60 * 1000, // 10 minutes
  REQUEST_TIMEOUT_MS: 60000, // 60 seconds
  OCR_TIMEOUT_MS: 30000, // 30 seconds
  SOLVE_TIMEOUT_MS: 120000, // 120 seconds
};

// Provider names
export const PROVIDERS = {
  OPENAI: 'openai',
  WOLFRAM: 'wolfram',
  MATHPIX: 'mathpix',
  GENERIC_OCR: 'generic_ocr',
  PYTHON_SERVICE: 'python_service',
};

// Report formats
export const REPORT_FORMATS = {
  PDF: 'pdf',
  HTML: 'html',
};

// Graph types
export const GRAPH_TYPES = {
  LINE: 'line',
  SCATTER: 'scatter',
  BAR: 'bar',
  POLAR: 'polar',
  PARAMETRIC: 'parametric',
  IMPLICIT: 'implicit',
};

// Version info
export const VERSION = {
  server: '1.0.0',
  api: '1.0.0',
  name: 'Arithmetic Math Solver',
};
