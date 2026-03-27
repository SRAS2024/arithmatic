// lib/theme.js - Theme management
import { Tracker } from 'meteor/tracker';

let _appState = null;

export function initTheme(appState) {
  _appState = appState;

  // Apply saved theme on load
  const saved = localStorage.getItem('arithmetic-theme') || 'light';
  applyTheme(saved);

  // React to theme changes
  Tracker.autorun(() => {
    const theme = appState.theme.get();
    applyTheme(theme);
  });
}

export function applyTheme(theme) {
  document.body.classList.remove('theme-light', 'theme-dark');
  document.body.classList.add(`theme-${theme}`);
  localStorage.setItem('arithmetic-theme', theme);

  // Update meta theme-color for mobile browsers
  let meta = document.querySelector('meta[name="theme-color"]');
  if (!meta) {
    meta = document.createElement('meta');
    meta.name = 'theme-color';
    document.head.appendChild(meta);
  }
  meta.content = theme === 'dark' ? '#0f1117' : '#f8f9fc';
}

export function getTheme() {
  if (_appState) return _appState.theme.get();
  return localStorage.getItem('arithmetic-theme') || 'light';
}

export function setTheme(theme) {
  if (_appState) _appState.theme.set(theme);
  applyTheme(theme);
}

export function toggleTheme() {
  const current = getTheme();
  const next = current === 'light' ? 'dark' : 'light';
  setTheme(next);
  return next;
}
