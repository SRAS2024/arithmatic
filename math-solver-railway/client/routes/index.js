// routes/index.js - Simple client-side routing (single page app)
// Structure for future route expansion

const routes = {
  '/': { name: 'home', title: 'Arithmetic' },
  '/solver': { name: 'solver', title: 'Solver - Arithmetic' },
  '/history': { name: 'history', title: 'History - Arithmetic' },
};

let currentRoute = '/';

export function initRouter() {
  // Handle browser back/forward
  window.addEventListener('popstate', (e) => {
    const path = window.location.pathname;
    if (routes[path]) {
      currentRoute = path;
      document.title = routes[path].title;
    }
  });

  // Set initial route
  const path = window.location.pathname;
  if (routes[path]) {
    currentRoute = path;
    document.title = routes[path].title;
  } else {
    currentRoute = '/';
    document.title = routes['/'].title;
  }
}

export function navigate(path) {
  if (routes[path]) {
    currentRoute = path;
    window.history.pushState({}, routes[path].title, path);
    document.title = routes[path].title;
  }
}

export function getCurrentRoute() {
  return currentRoute;
}
