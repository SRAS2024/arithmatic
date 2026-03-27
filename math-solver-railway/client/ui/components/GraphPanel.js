// ui/components/GraphPanel.js - Interactive graph display
import { Tracker } from 'meteor/tracker';
import { createPlotlyConfig, getDefaultLayout } from '../../lib/chartHelpers';

export function createGraphPanel(appState) {
  const panel = document.createElement('div');
  panel.className = 'card graph-panel';
  panel.style.display = 'none';

  const titleRow = document.createElement('div');
  titleRow.className = 'graph-title-row';

  const title = document.createElement('div');
  title.className = 'card-title';
  title.textContent = 'Graph';

  const graphActions = document.createElement('div');
  graphActions.className = 'graph-actions';

  const fullscreenBtn = document.createElement('button');
  fullscreenBtn.className = 'btn-icon';
  fullscreenBtn.title = 'Fullscreen';
  fullscreenBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 3 21 3 21 9"></polyline><polyline points="9 21 3 21 3 15"></polyline><line x1="21" y1="3" x2="14" y2="10"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>`;

  const downloadPngBtn = document.createElement('button');
  downloadPngBtn.className = 'btn-icon';
  downloadPngBtn.title = 'Download PNG';
  downloadPngBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>`;

  graphActions.appendChild(fullscreenBtn);
  graphActions.appendChild(downloadPngBtn);
  titleRow.appendChild(title);
  titleRow.appendChild(graphActions);

  // Chart container
  const chartContainer = document.createElement('div');
  chartContainer.className = 'graph-chart-container';
  chartContainer.id = 'plotly-chart-' + Math.random().toString(36).slice(2, 8);

  // Server image fallback
  const serverImage = document.createElement('img');
  serverImage.className = 'graph-server-image';
  serverImage.style.display = 'none';

  // Assemble
  panel.appendChild(titleRow);
  panel.appendChild(chartContainer);
  panel.appendChild(serverImage);

  let isFullscreen = false;

  // --- Events ---

  fullscreenBtn.addEventListener('click', () => {
    isFullscreen = !isFullscreen;
    panel.classList.toggle('graph-fullscreen', isFullscreen);

    if (isFullscreen) {
      document.body.style.overflow = 'hidden';
      fullscreenBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 14 10 14 10 20"></polyline><polyline points="20 10 14 10 14 4"></polyline><line x1="14" y1="10" x2="21" y2="3"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>`;
    } else {
      document.body.style.overflow = '';
      fullscreenBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 3 21 3 21 9"></polyline><polyline points="9 21 3 21 3 15"></polyline><line x1="21" y1="3" x2="14" y2="10"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>`;
    }

    // Resize plotly chart
    if (typeof Plotly !== 'undefined') {
      setTimeout(() => {
        Plotly.Plots.resize(chartContainer);
      }, 100);
    }
  });

  downloadPngBtn.addEventListener('click', () => {
    // Try downloading from Plotly first
    if (typeof Plotly !== 'undefined') {
      Plotly.downloadImage(chartContainer, {
        format: 'png',
        width: 1200,
        height: 800,
        filename: 'arithmetic-graph',
      }).catch(() => {
        // Fallback: download server image
        downloadServerImage();
      });
    } else {
      downloadServerImage();
    }
  });

  function downloadServerImage() {
    const graphData = appState.graphData.get();
    if (graphData && graphData.image) {
      const link = document.createElement('a');
      link.href = graphData.image;
      link.download = 'arithmetic-graph.png';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  }

  // Escape key to exit fullscreen
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isFullscreen) {
      fullscreenBtn.click();
    }
  });

  // --- Reactive updates ---

  Tracker.autorun(() => {
    const graphData = appState.graphData.get();
    if (!graphData) return;

    // Option 1: Plotly data from server
    if (graphData.plotly && typeof Plotly !== 'undefined') {
      const config = createPlotlyConfig(graphData.plotly);
      const layout = {
        ...getDefaultLayout(),
        ...(graphData.plotly.layout || {}),
      };

      chartContainer.style.display = 'block';
      serverImage.style.display = 'none';

      Plotly.newPlot(chartContainer, config.data, layout, {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['lasso2d', 'select2d'],
        displaylogo: false,
      });
    }
    // Option 2: Chart spec for client-side generation
    else if (graphData.spec && typeof Plotly !== 'undefined') {
      const config = createPlotlyConfig(graphData.spec);
      const layout = {
        ...getDefaultLayout(),
        ...(graphData.spec.layout || {}),
      };

      chartContainer.style.display = 'block';
      serverImage.style.display = 'none';

      Plotly.newPlot(chartContainer, config.data, layout, {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['lasso2d', 'select2d'],
        displaylogo: false,
      });
    }
    // Option 3: Base64 image from server
    else if (graphData.image) {
      chartContainer.style.display = 'none';
      serverImage.style.display = 'block';
      serverImage.src = graphData.image;
      serverImage.alt = 'Graph result';
    }
    // Option 4: Function expression for client-side plotting
    else if (graphData.expression && typeof Plotly !== 'undefined') {
      plotExpression(chartContainer, graphData.expression, graphData.range);
    }
  });

  return panel;
}

function plotExpression(container, expression, range) {
  const xMin = (range && range.min) || -10;
  const xMax = (range && range.max) || 10;
  const numPoints = 500;
  const step = (xMax - xMin) / numPoints;

  const xVals = [];
  const yVals = [];

  for (let i = 0; i <= numPoints; i++) {
    const x = xMin + i * step;
    xVals.push(x);
    try {
      if (typeof math !== 'undefined') {
        const y = math.evaluate(expression, { x });
        yVals.push(isFinite(y) ? y : null);
      } else {
        yVals.push(null);
      }
    } catch {
      yVals.push(null);
    }
  }

  const trace = {
    x: xVals,
    y: yVals,
    type: 'scatter',
    mode: 'lines',
    line: { color: '#6366f1', width: 2.5 },
    name: expression,
    connectgaps: false,
  };

  const layout = {
    ...getDefaultLayout(),
    title: { text: `y = ${expression}`, font: { size: 14 } },
    xaxis: { title: 'x', zeroline: true, gridcolor: 'rgba(128,128,128,0.15)' },
    yaxis: { title: 'y', zeroline: true, gridcolor: 'rgba(128,128,128,0.15)' },
  };

  container.style.display = 'block';
  Plotly.newPlot(container, [trace], layout, {
    responsive: true,
    displayModeBar: true,
    displaylogo: false,
  });
}
