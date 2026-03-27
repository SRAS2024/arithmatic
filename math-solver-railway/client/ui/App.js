// ui/App.js - Chat-based app assembly
import { Tracker } from 'meteor/tracker';
import { Meteor } from 'meteor/meteor';
import { toggleTheme, getTheme } from '../lib/theme';
import { renderLatex, expressionToLatex } from '../lib/mathPreview';

let _appState = null;
let _messagesContainer = null;
let _chatMessages = [];
let _msgIdCounter = 0;

// SVG Icons
const ICONS = {
  menu: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>',
  close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
  send: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>',
  plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>',
  pen: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 19l7-7 3 3-7 7-3-3z"/><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/><path d="M2 2l7.586 7.586"/><circle cx="11" cy="11" r="2"/></svg>',
  download: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>',
  steps: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>',
  sun: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>',
  moon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>',
  newChat: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>',
  copy: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>',
};

const SUGGESTIONS = [
  'Solve x^2 - 5x + 6 = 0',
  'Integrate sin(x) dx',
  'Factor x^3 - 8',
  'Plot y = cos(x)',
  'Derivative of x^3 + 2x',
  'Mean of 10, 20, 30, 40',
  'det [[1,2],[3,4]]',
  'Limit sin(x)/x as x->0',
];

function detectProblemType(text) {
  const t = text.toLowerCase();
  if (/\b(plot|graph|chart|bar|pie|histogram|scatter)\b/.test(t)) return 'Graphing';
  if (/\b(deriv|d\/d|differentiat)\b/.test(t)) return 'Calculus';
  if (/\b(integr|antideriv|int\()\b/.test(t)) return 'Calculus';
  if (/\b(limit|lim)\b/.test(t)) return 'Calculus';
  if (/\b(series|taylor|maclaurin|sum)\b/.test(t)) return 'Series';
  if (/\b(matrix|det|eigen|inverse)\b/.test(t)) return 'Linear Algebra';
  if (/\b(mean|median|std|variance|probability)\b/.test(t)) return 'Statistics';
  if (/\b(factor|expand|simplif)\b/.test(t)) return 'Algebra';
  if (/\b(solve|equation)\b/.test(t) || /[a-z]\s*=/.test(t)) return 'Algebra';
  if (/\b(sin|cos|tan|sec|csc|cot)\b/.test(t)) return 'Trigonometry';
  if (/\b(optimize|minimize|maximize)\b/.test(t)) return 'Optimization';
  if (/\b(diff.*eq|ode|pde)\b/.test(t)) return 'Diff. Equations';
  if (/^[\d\s+\-*/().^%]+$/.test(t.replace(/\s/g, ''))) return 'Arithmetic';
  return 'Math';
}

export function initApp(appState) {
  _appState = appState;
  const appRoot = document.getElementById('app');
  if (!appRoot) return;
  appRoot.innerHTML = '';

  // Build layout: sidebar + main
  const sidebar = buildSidebar(appState);
  const main = buildMainArea(appState);
  appRoot.appendChild(sidebar);
  appRoot.appendChild(main);
}

// ============ SIDEBAR ============

function buildSidebar(state) {
  const sidebar = document.createElement('div');
  sidebar.className = 'chat-sidebar collapsed';
  sidebar.id = 'chat-sidebar';

  // Header
  const header = document.createElement('div');
  header.className = 'sidebar-header';
  const logo = document.createElement('span');
  logo.className = 'sidebar-logo';
  logo.textContent = 'Arithmetic';
  const closeBtn = document.createElement('button');
  closeBtn.className = 'sidebar-close-btn';
  closeBtn.innerHTML = ICONS.close;
  closeBtn.addEventListener('click', () => {
    state.sidebarOpen.set(false);
  });
  header.appendChild(logo);
  header.appendChild(closeBtn);

  // New chat button
  const newChatBtn = document.createElement('button');
  newChatBtn.className = 'sidebar-new-chat';
  newChatBtn.innerHTML = `${ICONS.newChat}<span>New chat</span>`;
  newChatBtn.addEventListener('click', () => {
    _chatMessages = [];
    state.chatMessages.set([]);
    state.solverResult.set(null);
    state.graphData.set(null);
    state.error.set(null);
    state.sidebarOpen.set(false);
    renderMessages(state);
  });

  // History
  const historyLabel = document.createElement('div');
  historyLabel.className = 'sidebar-history-label';
  historyLabel.textContent = 'Recent';
  const historyList = document.createElement('div');
  historyList.className = 'sidebar-history';
  historyList.id = 'sidebar-history';
  historyList.appendChild(historyLabel);

  // Footer with theme toggle
  const footer = document.createElement('div');
  footer.className = 'sidebar-footer';
  const themeBtn = document.createElement('button');
  themeBtn.className = 'chat-input-icon-btn';
  themeBtn.id = 'theme-toggle-btn';
  themeBtn.innerHTML = getTheme() === 'dark' ? ICONS.sun : ICONS.moon;
  themeBtn.title = 'Toggle theme';
  themeBtn.addEventListener('click', () => {
    const next = toggleTheme();
    themeBtn.innerHTML = next === 'dark' ? ICONS.sun : ICONS.moon;
  });
  footer.appendChild(themeBtn);

  sidebar.appendChild(header);
  sidebar.appendChild(newChatBtn);
  sidebar.appendChild(historyList);
  sidebar.appendChild(footer);

  // Reactive open/close
  Tracker.autorun(() => {
    const open = state.sidebarOpen.get();
    sidebar.classList.toggle('collapsed', !open);
  });

  // Reactive history
  Tracker.autorun(() => {
    const msgs = state.chatMessages.get();
    updateSidebarHistory(historyList, msgs);
  });

  return sidebar;
}

function updateSidebarHistory(container, messages) {
  // Keep only the label
  const label = container.querySelector('.sidebar-history-label');
  container.innerHTML = '';
  if (label) container.appendChild(label);

  // Group user messages as sidebar items
  const userMsgs = messages.filter(m => m.role === 'user');
  userMsgs.reverse().forEach(msg => {
    const item = document.createElement('div');
    item.className = 'sidebar-item';
    const badge = document.createElement('span');
    badge.className = 'si-badge';
    badge.textContent = msg.problemType || 'Math';
    const text = document.createElement('span');
    text.className = 'si-text';
    text.textContent = msg.problem;
    item.appendChild(badge);
    item.appendChild(text);
    container.appendChild(item);
  });
}

// ============ MAIN AREA ============

function buildMainArea(state) {
  const main = document.createElement('div');
  main.className = 'chat-main';

  // Top bar
  const topbar = document.createElement('div');
  topbar.className = 'chat-topbar';

  const hamburger = document.createElement('button');
  hamburger.className = 'topbar-hamburger';
  hamburger.innerHTML = ICONS.menu;
  hamburger.addEventListener('click', () => {
    state.sidebarOpen.set(!state.sidebarOpen.get());
  });

  const title = document.createElement('div');
  title.className = 'topbar-title';
  title.textContent = 'Arithmetic';

  const actions = document.createElement('div');
  actions.className = 'topbar-actions';
  const themeBtn2 = document.createElement('button');
  themeBtn2.className = 'chat-input-icon-btn';
  themeBtn2.innerHTML = getTheme() === 'dark' ? ICONS.sun : ICONS.moon;
  themeBtn2.addEventListener('click', () => {
    const next = toggleTheme();
    themeBtn2.innerHTML = next === 'dark' ? ICONS.sun : ICONS.moon;
    const sidebarBtn = document.getElementById('theme-toggle-btn');
    if (sidebarBtn) sidebarBtn.innerHTML = next === 'dark' ? ICONS.sun : ICONS.moon;
  });
  actions.appendChild(themeBtn2);

  topbar.appendChild(hamburger);
  topbar.appendChild(title);
  topbar.appendChild(actions);

  // Messages area
  const messagesWrap = document.createElement('div');
  messagesWrap.className = 'chat-messages';
  messagesWrap.id = 'chat-messages';

  const messagesInner = document.createElement('div');
  messagesInner.className = 'chat-messages-inner';
  messagesInner.id = 'chat-messages-inner';
  messagesWrap.appendChild(messagesInner);
  _messagesContainer = messagesInner;

  // Input area
  const inputArea = buildInputArea(state);

  main.appendChild(topbar);
  main.appendChild(messagesWrap);
  main.appendChild(inputArea);

  // Render initial state (welcome screen)
  renderMessages(state);

  // React to messages
  Tracker.autorun(() => {
    const msgs = state.chatMessages.get();
    _chatMessages = msgs;
    renderMessages(state);
  });

  return main;
}

// ============ INPUT AREA ============

function buildInputArea(state) {
  const area = document.createElement('div');
  area.className = 'chat-input-area';

  const inner = document.createElement('div');
  inner.className = 'chat-input-area-inner';

  // File preview (hidden initially)
  const filePreview = document.createElement('div');
  filePreview.className = 'chat-file-preview';
  filePreview.style.display = 'none';
  filePreview.id = 'file-preview';

  // Handwriting canvas (hidden initially)
  const canvasWrap = document.createElement('div');
  canvasWrap.className = 'handwrite-canvas-wrap';
  canvasWrap.style.display = 'none';
  canvasWrap.id = 'handwrite-wrap';

  const canvas = document.createElement('canvas');
  canvas.className = 'handwrite-canvas';
  canvas.id = 'handwrite-canvas';

  const canvasToolbar = document.createElement('div');
  canvasToolbar.className = 'handwrite-toolbar';
  const clearCanvasBtn = document.createElement('button');
  clearCanvasBtn.textContent = 'Clear';
  const submitCanvasBtn = document.createElement('button');
  submitCanvasBtn.textContent = 'Submit Drawing';
  submitCanvasBtn.style.color = 'var(--accent-primary)';
  submitCanvasBtn.style.borderColor = 'var(--accent-primary)';
  canvasToolbar.appendChild(clearCanvasBtn);
  canvasToolbar.appendChild(submitCanvasBtn);
  canvasWrap.appendChild(canvas);
  canvasWrap.appendChild(canvasToolbar);

  // Input bar
  const inputBar = document.createElement('div');
  inputBar.className = 'chat-input-bar';

  // Left buttons: file upload + handwrite mode
  const leftBtns = document.createElement('div');
  leftBtns.className = 'chat-input-left-btns';

  const fileBtn = document.createElement('button');
  fileBtn.className = 'chat-input-icon-btn';
  fileBtn.innerHTML = ICONS.plus;
  fileBtn.title = 'Upload file';

  const fileInput = document.createElement('input');
  fileInput.type = 'file';
  fileInput.accept = 'image/*,.pdf';
  fileInput.style.display = 'none';

  const penBtn = document.createElement('button');
  penBtn.className = 'chat-input-icon-btn';
  penBtn.innerHTML = ICONS.pen;
  penBtn.title = 'Handwriting mode';
  penBtn.id = 'pen-mode-btn';

  leftBtns.appendChild(fileBtn);
  leftBtns.appendChild(penBtn);

  // Textarea
  const textarea = document.createElement('textarea');
  textarea.className = 'chat-textarea';
  textarea.id = 'chat-input';
  textarea.placeholder = 'Type a math problem...';
  textarea.rows = 1;

  // Send button
  const sendBtn = document.createElement('button');
  sendBtn.className = 'chat-send-btn';
  sendBtn.innerHTML = ICONS.send;
  sendBtn.id = 'chat-send-btn';

  inputBar.appendChild(leftBtns);
  inputBar.appendChild(fileInput);
  inputBar.appendChild(textarea);
  inputBar.appendChild(sendBtn);

  const hint = document.createElement('div');
  hint.className = 'chat-input-hint';
  hint.textContent = 'Press Enter to send, Shift+Enter for new line';

  inner.appendChild(filePreview);
  inner.appendChild(canvasWrap);
  inner.appendChild(inputBar);
  inner.appendChild(hint);
  area.appendChild(inner);

  // --- State ---
  let currentFile = null;
  let isDrawing = false;
  let drawCtx = null;

  // Auto-resize textarea
  textarea.addEventListener('input', () => {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 160) + 'px';
  });

  // Enter to send
  textarea.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      doSend();
    }
  });

  sendBtn.addEventListener('click', doSend);

  // File upload
  fileBtn.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      currentFile = { name: file.name, type: file.type, size: file.size, data: reader.result };
      filePreview.style.display = 'flex';
      filePreview.innerHTML = `
        <span class="file-icon">${ICONS.plus}</span>
        <span class="file-name">${file.name}</span>
        <button class="file-remove">${ICONS.close}</button>
      `;
      filePreview.querySelector('.file-remove').addEventListener('click', () => {
        currentFile = null;
        filePreview.style.display = 'none';
        fileInput.value = '';
      });
    };
    reader.readAsDataURL(file);
  });

  // Handwriting mode toggle
  penBtn.addEventListener('click', () => {
    const isHandwrite = canvasWrap.style.display !== 'none';
    if (isHandwrite) {
      canvasWrap.style.display = 'none';
      penBtn.classList.remove('active');
      textarea.placeholder = 'Type a math problem...';
    } else {
      canvasWrap.style.display = 'block';
      penBtn.classList.add('active');
      textarea.placeholder = 'Or type here alongside drawing...';
      initCanvas(canvas, canvasWrap);
    }
  });

  // Canvas: clear
  clearCanvasBtn.addEventListener('click', () => {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  });

  // Canvas: submit drawing
  submitCanvasBtn.addEventListener('click', () => {
    const dataUrl = canvas.toDataURL('image/png');
    currentFile = { name: 'handwritten.png', type: 'image/png', size: 0, data: dataUrl };
    doSend();
    // Clear canvas
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  });

  // --- Send logic ---
  function doSend() {
    const text = textarea.value.trim();
    if (!text && !currentFile) return;
    if (state.isLoading.get()) return;

    const problemType = detectProblemType(text || 'image upload');
    const msgs = state.chatMessages.get().slice();

    // Add user message
    const userMsg = {
      id: ++_msgIdCounter,
      role: 'user',
      problem: text || '(uploaded file)',
      problemType,
      file: currentFile ? { name: currentFile.name, type: currentFile.type } : null,
      timestamp: Date.now(),
    };
    msgs.push(userMsg);
    state.chatMessages.set(msgs);

    // Clear input
    textarea.value = '';
    textarea.style.height = 'auto';

    // Set loading
    state.isLoading.set(true);
    state.loadingMessage.set('Solving...');
    state.error.set(null);

    if (currentFile) {
      // Upload file first, then solve
      Meteor.call('upload', {
        fileName: currentFile.name,
        fileType: currentFile.type,
        fileData: currentFile.data,
      }, (err, ocrResult) => {
        if (err) {
          addBotError(state, err.reason || 'Upload failed');
          currentFile = null;
          filePreview.style.display = 'none';
          fileInput.value = '';
          return;
        }
        const extractedText = ocrResult?.text || ocrResult?.extractedText || text;
        doSolve(state, extractedText || text, problemType, ocrResult);
        currentFile = null;
        filePreview.style.display = 'none';
        fileInput.value = '';
      });
    } else {
      doSolve(state, text, problemType, null);
    }
  }

  return area;
}

function initCanvas(canvas, wrap) {
  const rect = wrap.getBoundingClientRect();
  canvas.width = rect.width;
  canvas.height = 180;
  const ctx = canvas.getContext('2d');
  ctx.strokeStyle = getComputedStyle(document.body).getPropertyValue('--text-primary').trim() || '#fff';
  ctx.lineWidth = 2.5;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';

  let drawing = false;
  let lastX = 0, lastY = 0;

  function getPos(e) {
    const r = canvas.getBoundingClientRect();
    const t = e.touches ? e.touches[0] : e;
    return [t.clientX - r.left, t.clientY - r.top];
  }

  canvas.addEventListener('mousedown', (e) => { drawing = true; [lastX, lastY] = getPos(e); });
  canvas.addEventListener('mousemove', (e) => {
    if (!drawing) return;
    const [x, y] = getPos(e);
    ctx.beginPath(); ctx.moveTo(lastX, lastY); ctx.lineTo(x, y); ctx.stroke();
    [lastX, lastY] = [x, y];
  });
  canvas.addEventListener('mouseup', () => { drawing = false; });
  canvas.addEventListener('mouseleave', () => { drawing = false; });

  canvas.addEventListener('touchstart', (e) => { e.preventDefault(); drawing = true; [lastX, lastY] = getPos(e); });
  canvas.addEventListener('touchmove', (e) => {
    e.preventDefault();
    if (!drawing) return;
    const [x, y] = getPos(e);
    ctx.beginPath(); ctx.moveTo(lastX, lastY); ctx.lineTo(x, y); ctx.stroke();
    [lastX, lastY] = [x, y];
  });
  canvas.addEventListener('touchend', () => { drawing = false; });
}

// ============ SOLVE LOGIC ============

function doSolve(state, text, problemType, ocrResult) {
  Meteor.call('solve', {
    problem: text,
    mode: state.solverMode.get(),
    detailedSteps: true,
    crossVerify: state.options.get().crossVerify,
  }, (err, result) => {
    state.isLoading.set(false);
    state.loadingMessage.set('');

    if (err) {
      addBotError(state, err.reason || err.message || 'Solving failed');
      return;
    }

    const msgs = state.chatMessages.get().slice();
    const botMsg = {
      id: ++_msgIdCounter,
      role: 'bot',
      answer: result?.answer || 'No answer found',
      steps: result?.steps || [],
      latex: result?.latex || null,
      simplified: result?.simplified || null,
      decimal: result?.decimal_approx || result?.decimal || null,
      confidence: result?.confidence || null,
      graph: result?.graph_data || null,
      ocrText: ocrResult?.text || null,
      problemType,
      problem: text,
      timestamp: Date.now(),
    };
    msgs.push(botMsg);
    state.chatMessages.set(msgs);
    state.solverResult.set(result);

    // Auto-generate graph if graph_data is present
    if (result?.graph_data) {
      Meteor.call('generateGraph', {
        problem: text,
        expression: result.graph_data.expression || text,
      }, (gErr, gResult) => {
        if (!gErr && gResult) {
          botMsg.graphImage = gResult.image || gResult.image_base64;
          state.chatMessages.set(state.chatMessages.get().slice());
          state.graphData.set(gResult);
        }
      });
    }
  });
}

function addBotError(state, message) {
  state.isLoading.set(false);
  state.loadingMessage.set('');
  const msgs = state.chatMessages.get().slice();
  msgs.push({
    id: ++_msgIdCounter,
    role: 'bot',
    answer: message,
    isError: true,
    timestamp: Date.now(),
  });
  state.chatMessages.set(msgs);
}

// ============ RENDER MESSAGES ============

function renderMessages(state) {
  const container = _messagesContainer;
  if (!container) return;

  const msgs = _chatMessages;
  const isLoading = state.isLoading.get();

  container.innerHTML = '';

  // Show welcome if no messages
  if (msgs.length === 0 && !isLoading) {
    const welcome = document.createElement('div');
    welcome.className = 'chat-welcome';
    welcome.innerHTML = `
      <div class="welcome-logo">Arithmetic</div>
      <div class="welcome-subtitle">Premium Mathematical Intelligence Platform. Type a problem, upload an image, or draw an equation.</div>
      <div class="welcome-suggestions" id="welcome-suggestions"></div>
    `;
    container.appendChild(welcome);

    const sugContainer = welcome.querySelector('#welcome-suggestions');
    SUGGESTIONS.forEach(s => {
      const btn = document.createElement('button');
      btn.className = 'welcome-suggestion';
      btn.textContent = s;
      btn.addEventListener('click', () => {
        const input = document.getElementById('chat-input');
        if (input) { input.value = s; input.dispatchEvent(new Event('input')); }
        // Auto-send
        state.currentProblem.set(s);
        const sendBtn = document.getElementById('chat-send-btn');
        if (sendBtn) sendBtn.click();
      });
      sugContainer.appendChild(btn);
    });
    return;
  }

  // Render each message
  msgs.forEach(msg => {
    const el = createMessageElement(msg, state);
    container.appendChild(el);
  });

  // Loading indicator
  if (isLoading) {
    const loadEl = document.createElement('div');
    loadEl.className = 'chat-msg bot';
    loadEl.innerHTML = `
      <div class="msg-bubble msg-loading">
        <div class="msg-loading-dot"></div>
        <div class="msg-loading-dot"></div>
        <div class="msg-loading-dot"></div>
      </div>
    `;
    container.appendChild(loadEl);
  }

  // Scroll to bottom
  const scrollParent = container.parentElement;
  if (scrollParent) {
    requestAnimationFrame(() => {
      scrollParent.scrollTop = scrollParent.scrollHeight;
    });
  }
}

function createMessageElement(msg, state) {
  const wrapper = document.createElement('div');
  wrapper.className = `chat-msg ${msg.role}`;

  if (msg.role === 'user') {
    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    bubble.textContent = msg.problem;
    if (msg.file) {
      bubble.textContent += ` [${msg.file.name}]`;
    }
    wrapper.appendChild(bubble);
    return wrapper;
  }

  // Bot message
  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';

  if (msg.isError) {
    bubble.style.borderColor = 'var(--error)';
    bubble.innerHTML = `<div style="color: var(--error);">${escapeHtml(msg.answer)}</div>`;
    wrapper.appendChild(bubble);
    return wrapper;
  }

  // Answer
  const answerDiv = document.createElement('div');
  answerDiv.className = 'msg-answer';

  // Try to render LaTeX
  if (msg.latex && typeof katex !== 'undefined') {
    try {
      katex.render(msg.latex, answerDiv, { throwOnError: false, displayMode: false });
    } catch {
      answerDiv.textContent = msg.answer;
    }
  } else {
    answerDiv.textContent = msg.answer;
  }

  // Confidence badge
  if (msg.confidence && msg.confidence > 0) {
    const badge = document.createElement('span');
    const level = msg.confidence >= 0.8 ? 'high' : msg.confidence >= 0.5 ? 'medium' : 'low';
    badge.className = `msg-confidence ${level}`;
    badge.textContent = level === 'high' ? 'High confidence' : level === 'medium' ? 'Medium' : 'Low confidence';
    answerDiv.appendChild(badge);
  }

  bubble.appendChild(answerDiv);

  // Show simplified/decimal below answer
  if (msg.simplified && msg.simplified !== msg.answer) {
    const simpDiv = document.createElement('div');
    simpDiv.style.cssText = 'font-size: 0.85rem; color: var(--text-secondary); margin-top: 4px;';
    simpDiv.textContent = `Simplified: ${msg.simplified}`;
    bubble.appendChild(simpDiv);
  }
  if (msg.decimal) {
    const decDiv = document.createElement('div');
    decDiv.style.cssText = 'font-size: 0.85rem; color: var(--text-secondary);';
    decDiv.textContent = `\u2248 ${msg.decimal}`;
    bubble.appendChild(decDiv);
  }

  // Graph (show immediately if available)
  if (msg.graphImage) {
    const graphDiv = document.createElement('div');
    graphDiv.className = 'msg-graph';
    const img = document.createElement('img');
    img.src = msg.graphImage.startsWith('data:') ? msg.graphImage : `data:image/png;base64,${msg.graphImage}`;
    img.alt = 'Graph';
    graphDiv.appendChild(img);
    bubble.appendChild(graphDiv);
  }

  // Steps container (hidden by default)
  const stepsDiv = document.createElement('div');
  stepsDiv.className = 'msg-steps';
  stepsDiv.style.display = 'none';
  stepsDiv.id = `steps-${msg.id}`;

  if (msg.steps && msg.steps.length > 0) {
    const stepsTitle = document.createElement('div');
    stepsTitle.className = 'msg-steps-title';
    stepsTitle.textContent = 'Solution Steps';
    stepsDiv.appendChild(stepsTitle);

    msg.steps.forEach((step, i) => {
      const stepEl = document.createElement('div');
      stepEl.className = 'msg-step';
      stepEl.innerHTML = `<span class="msg-step-num">${i + 1}</span><span class="msg-step-text"></span>`;
      const textEl = stepEl.querySelector('.msg-step-text');

      // Try KaTeX rendering for step
      if (typeof katex !== 'undefined' && /[\\^_{}]/.test(String(step))) {
        try {
          katex.render(String(step), textEl, { throwOnError: false, displayMode: false });
        } catch {
          textEl.textContent = step;
        }
      } else {
        textEl.textContent = step;
      }
      stepsDiv.appendChild(stepEl);
    });
  }
  bubble.appendChild(stepsDiv);

  // Action buttons
  const actions = document.createElement('div');
  actions.className = 'msg-actions';

  // Show Work button
  if (msg.steps && msg.steps.length > 0) {
    const showWorkBtn = document.createElement('button');
    showWorkBtn.className = 'msg-action-btn';
    showWorkBtn.innerHTML = `${ICONS.steps} <span>Show Work</span>`;
    let stepsVisible = false;
    showWorkBtn.addEventListener('click', () => {
      stepsVisible = !stepsVisible;
      stepsDiv.style.display = stepsVisible ? 'block' : 'none';
      showWorkBtn.querySelector('span').textContent = stepsVisible ? 'Hide Work' : 'Show Work';
    });
    actions.appendChild(showWorkBtn);
  }

  // Download button
  const downloadBtn = document.createElement('button');
  downloadBtn.className = 'msg-action-btn';
  downloadBtn.innerHTML = `${ICONS.download} <span>Download</span>`;
  downloadBtn.addEventListener('click', () => {
    // Generate and download PDF report
    Meteor.call('generateReport', {
      format: 'pdf',
      problem: msg.problem || '',
      result: {
        answer: msg.answer,
        steps: msg.steps,
        latex: msg.latex,
        simplified: msg.simplified,
        decimal: msg.decimal,
      },
    }, (err, reportData) => {
      if (err) {
        console.error('Report generation failed:', err);
        return;
      }
      if (reportData && reportData.data) {
        downloadBase64(reportData.data, reportData.filename || 'arithmetic-report.pdf', 'application/pdf');
      }
    });
  });
  actions.appendChild(downloadBtn);

  // Copy button
  const copyBtn = document.createElement('button');
  copyBtn.className = 'msg-action-btn';
  copyBtn.innerHTML = `${ICONS.copy} <span>Copy</span>`;
  copyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(msg.answer).then(() => {
      copyBtn.querySelector('span').textContent = 'Copied!';
      setTimeout(() => { copyBtn.querySelector('span').textContent = 'Copy'; }, 1500);
    });
  });
  actions.appendChild(copyBtn);

  bubble.appendChild(actions);
  wrapper.appendChild(bubble);
  return wrapper;
}

// ============ HELPERS ============

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function downloadBase64(base64Data, filename, mimeType) {
  let data = base64Data;
  if (!data.startsWith('data:')) {
    data = `data:${mimeType};base64,${data}`;
  }
  const link = document.createElement('a');
  link.href = data;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

export function getAppState() {
  return _appState;
}
