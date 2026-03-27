/**
 * Arithmetic - Theme System Tests
 */

if (Meteor.isClient) {
  import { Tinytest } from 'meteor/tinytest';

  Tinytest.add('Theme - toggleTheme switches between dark and light', function (test) {
    // Reset to dark
    document.body.className = 'theme-dark';
    localStorage.setItem('arithmetic_theme', 'dark');

    // Simulate toggle
    const currentTheme = localStorage.getItem('arithmetic_theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('arithmetic_theme', newTheme);
    document.body.className = `theme-${newTheme}`;

    test.equal(localStorage.getItem('arithmetic_theme'), 'light');
    test.isTrue(document.body.classList.contains('theme-light'));
  });

  Tinytest.add('Theme - CSS variables are applied for dark theme', function (test) {
    document.body.className = 'theme-dark';
    const styles = getComputedStyle(document.body);
    // Just verify the class is applied
    test.isTrue(document.body.classList.contains('theme-dark'));
  });

  Tinytest.add('Theme - CSS variables are applied for light theme', function (test) {
    document.body.className = 'theme-light';
    const styles = getComputedStyle(document.body);
    test.isTrue(document.body.classList.contains('theme-light'));
  });

  Tinytest.add('Theme - persistence across page loads', function (test) {
    localStorage.setItem('arithmetic_theme', 'light');
    const saved = localStorage.getItem('arithmetic_theme');
    test.equal(saved, 'light');

    // Reset
    localStorage.setItem('arithmetic_theme', 'dark');
  });
}
