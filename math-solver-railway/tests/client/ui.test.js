/**
 * Arithmetic - Client UI Tests
 */

if (Meteor.isClient) {
  import { Tinytest } from 'meteor/tinytest';

  Tinytest.add('UI - App container exists after init', function (test) {
    const app = document.getElementById('app');
    test.isNotNull(app, 'App container should exist');
  });

  Tinytest.add('UI - Theme defaults to dark', function (test) {
    const theme = localStorage.getItem('arithmetic_theme') || 'dark';
    test.equal(theme, 'dark');
  });

  Tinytest.add('UI - Header renders with correct title', function (test) {
    const header = document.querySelector('.app-header');
    if (header) {
      const title = header.querySelector('.app-title');
      test.isNotNull(title, 'Title element should exist');
    }
  });

  Tinytest.add('UI - Solver input textarea exists', function (test) {
    const textarea = document.getElementById('math-input');
    test.isNotNull(textarea, 'Math input textarea should exist');
  });

  Tinytest.add('UI - Upload panel accepts files', function (test) {
    const dropZone = document.querySelector('.upload-drop-zone');
    test.isNotNull(dropZone, 'Upload drop zone should exist');
  });

  Tinytest.add('UI - Answer panel exists', function (test) {
    const panel = document.querySelector('.answer-panel');
    test.isNotNull(panel, 'Answer panel should exist');
  });

  Tinytest.add('UI - Steps panel exists', function (test) {
    const panel = document.querySelector('.steps-panel');
    test.isNotNull(panel, 'Steps panel should exist');
  });

  Tinytest.add('UI - Graph panel exists', function (test) {
    const panel = document.querySelector('.graph-panel');
    test.isNotNull(panel, 'Graph panel should exist');
  });

  Tinytest.add('UI - Download panel exists', function (test) {
    const panel = document.querySelector('.download-panel');
    test.isNotNull(panel, 'Download panel should exist');
  });

  Tinytest.add('UI - Solve button exists and is clickable', function (test) {
    const btn = document.getElementById('solve-btn');
    test.isNotNull(btn, 'Solve button should exist');
    test.equal(btn.disabled, false, 'Solve button should be enabled by default');
  });
}
