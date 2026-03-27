// ui/components/ThemeToggle.js - Theme toggle component
import { Tracker } from 'meteor/tracker';
import { toggleTheme } from '../../lib/theme';

export function createThemeToggle(appState) {
  const wrapper = document.createElement('div');
  wrapper.className = 'theme-toggle-wrapper';

  const btn = document.createElement('button');
  btn.className = 'theme-toggle-btn';
  btn.setAttribute('aria-label', 'Toggle theme');
  btn.title = 'Toggle theme';

  const track = document.createElement('div');
  track.className = 'theme-toggle-track';

  const thumb = document.createElement('div');
  thumb.className = 'theme-toggle-thumb';

  const sunIcon = document.createElement('span');
  sunIcon.className = 'theme-icon theme-icon-sun';
  sunIcon.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="5"></circle>
    <line x1="12" y1="1" x2="12" y2="3"></line>
    <line x1="12" y1="21" x2="12" y2="23"></line>
    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
    <line x1="1" y1="12" x2="3" y2="12"></line>
    <line x1="21" y1="12" x2="23" y2="12"></line>
    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
  </svg>`;

  const moonIcon = document.createElement('span');
  moonIcon.className = 'theme-icon theme-icon-moon';
  moonIcon.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
  </svg>`;

  track.appendChild(sunIcon);
  track.appendChild(moonIcon);
  track.appendChild(thumb);
  btn.appendChild(track);
  wrapper.appendChild(btn);

  // Event handler
  btn.addEventListener('click', () => {
    toggleTheme();
  });

  // Reactive update
  Tracker.autorun(() => {
    const theme = appState.theme.get();
    const isDark = theme === 'dark';
    btn.classList.toggle('is-dark', isDark);
    btn.setAttribute('aria-pressed', isDark.toString());
  });

  return wrapper;
}
