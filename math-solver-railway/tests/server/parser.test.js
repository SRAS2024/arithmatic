/**
 * Arithmetic - Parser Service Tests
 */

if (Meteor.isServer) {
  import { Tinytest } from 'meteor/tinytest';

  const { detectProblemType, normalizeExpression, extractMathFromText } = require('../../server/services/parserService');

  Tinytest.add('Parser - detects arithmetic', function (test) {
    const result = detectProblemType('2 + 3');
    test.equal(result, 'arithmetic');
  });

  Tinytest.add('Parser - detects algebra', function (test) {
    const result = detectProblemType('2x + 5 = 17');
    test.equal(result, 'algebra');
  });

  Tinytest.add('Parser - detects calculus derivative', function (test) {
    const result = detectProblemType('differentiate x^2 + 3x');
    test.equal(result, 'calculus');
  });

  Tinytest.add('Parser - detects calculus integral', function (test) {
    const result = detectProblemType('integrate sin(x) dx');
    test.equal(result, 'calculus');
  });

  Tinytest.add('Parser - detects system of equations', function (test) {
    const result = detectProblemType('x + y = 5, 2x - y = 1');
    test.equal(result, 'system');
  });

  Tinytest.add('Parser - detects matrix operation', function (test) {
    const result = detectProblemType('det [[1,2],[3,4]]');
    test.equal(result, 'linear_algebra');
  });

  Tinytest.add('Parser - detects graphing request', function (test) {
    const result = detectProblemType('plot sin(x)');
    test.equal(result, 'graphing');
  });

  Tinytest.add('Parser - detects statistics', function (test) {
    const result = detectProblemType('mean of 1, 2, 3, 4, 5');
    test.equal(result, 'statistics');
  });

  Tinytest.add('Parser - normalizes multiplication symbol', function (test) {
    const result = normalizeExpression('2 × 3');
    test.equal(result, '2 * 3');
  });

  Tinytest.add('Parser - normalizes division symbol', function (test) {
    const result = normalizeExpression('6 ÷ 2');
    test.equal(result, '6 / 2');
  });

  Tinytest.add('Parser - normalizes Unicode superscripts', function (test) {
    const result = normalizeExpression('x²');
    test.equal(result, 'x^2');
  });

  Tinytest.add('Parser - extracts math from text with instructions', function (test) {
    const result = extractMathFromText('Solve the following equation: 2x + 5 = 17');
    test.equal(result.expression, '2x + 5 = 17');
    test.isTrue(result.instructions.length > 0);
  });
}
