// ui/components/Header.js - Hero header component
import { Tracker } from 'meteor/tracker';
import { createThemeToggle } from './ThemeToggle';

const FEATURE_PILLS = [
  { label: 'OCR', icon: '\u{1F4F7}' },
  { label: 'Graphing', icon: '\u{1F4C8}' },
  { label: 'Step-by-Step', icon: '\u{1F4DD}' },
  { label: 'PDF Reports', icon: '\u{1F4C4}' },
  { label: 'Handwriting', icon: '\u270D\uFE0F' },
];

export function createHeader(appState) {
  const header = document.createElement('header');
  header.className = 'header';

  const container = document.createElement('div');
  container.className = 'header-container';

  // Left section: branding
  const branding = document.createElement('div');
  branding.className = 'header-branding';

  const title = document.createElement('h1');
  title.className = 'header-title';
  title.textContent = 'Arithmetic';

  const subtitle = document.createElement('p');
  subtitle.className = 'header-subtitle';
  subtitle.textContent = 'Premium Mathematical Intelligence Platform';

  branding.appendChild(title);
  branding.appendChild(subtitle);

  // Feature pills
  const pills = document.createElement('div');
  pills.className = 'header-pills';

  FEATURE_PILLS.forEach(({ label, icon }) => {
    const pill = document.createElement('span');
    pill.className = 'feature-pill';
    pill.innerHTML = `<span class="pill-icon">${icon}</span><span class="pill-label">${label}</span>`;
    pills.appendChild(pill);
  });

  // Right section: theme toggle
  const actions = document.createElement('div');
  actions.className = 'header-actions';

  const themeToggle = createThemeToggle(appState);
  actions.appendChild(themeToggle);

  // Assemble
  container.appendChild(branding);
  container.appendChild(pills);
  container.appendChild(actions);
  header.appendChild(container);

  return header;
}
