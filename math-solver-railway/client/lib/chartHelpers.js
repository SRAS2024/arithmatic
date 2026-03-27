// chartHelpers.js - Plotly chart configuration helpers
export const ChartHelpers = {
  getDefaultLayout(title, theme) {
    const isDark = theme === 'dark';
    return {
      title: { text: title || '', font: { family: 'Inter, sans-serif', size: 16, color: isDark ? '#f4f7fb' : '#1a1a2e' } },
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: { family: 'Inter, sans-serif', color: isDark ? '#aab4c3' : '#526172' },
      xaxis: {
        gridcolor: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)',
        zerolinecolor: isDark ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.15)',
        color: isDark ? '#aab4c3' : '#526172'
      },
      yaxis: {
        gridcolor: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)',
        zerolinecolor: isDark ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.15)',
        color: isDark ? '#aab4c3' : '#526172'
      },
      margin: { t: 50, r: 30, b: 50, l: 60 },
      showlegend: true,
      legend: { font: { color: isDark ? '#aab4c3' : '#526172' } }
    };
  },

  createFunctionPlot(expression, xRange, theme) {
    const x = [];
    const y = [];
    const start = xRange ? xRange[0] : -10;
    const end = xRange ? xRange[1] : 10;
    const step = (end - start) / 500;
    for (let xi = start; xi <= end; xi += step) {
      x.push(xi);
      try {
        const val = math.evaluate(expression.replace(/x/g, `(${xi})`));
        y.push(typeof val === 'number' && isFinite(val) ? val : null);
      } catch { y.push(null); }
    }
    return {
      data: [{ x, y, type: 'scatter', mode: 'lines', name: expression,
        line: { color: '#5e6ad2', width: 2.5 } }],
      layout: this.getDefaultLayout(`y = ${expression}`, theme)
    };
  },

  createBarChart(x, y, title, theme) {
    return {
      data: [{ x, y, type: 'bar', marker: {
        color: ['#5e6ad2', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899'].slice(0, x.length)
      }}],
      layout: this.getDefaultLayout(title, theme)
    };
  },

  createPieChart(labels, values, title, theme) {
    return {
      data: [{ labels, values, type: 'pie', hole: 0.35,
        marker: { colors: ['#5e6ad2', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899'] },
        textfont: { color: '#ffffff' } }],
      layout: this.getDefaultLayout(title, theme)
    };
  },

  createScatterPlot(x, y, title, theme) {
    return {
      data: [{ x, y, type: 'scatter', mode: 'markers',
        marker: { color: '#5e6ad2', size: 8, opacity: 0.8 } }],
      layout: this.getDefaultLayout(title, theme)
    };
  },

  createHistogram(data, title, theme) {
    return {
      data: [{ x: data, type: 'histogram', marker: { color: '#5e6ad2', opacity: 0.8 } }],
      layout: this.getDefaultLayout(title, theme)
    };
  },

  createLinePlot(x, y, title, theme) {
    return {
      data: [{ x, y, type: 'scatter', mode: 'lines+markers',
        line: { color: '#5e6ad2', width: 2 }, marker: { size: 5 } }],
      layout: this.getDefaultLayout(title, theme)
    };
  },

  parseChartSpec(spec) {
    if (typeof spec === 'string') {
      try { return JSON.parse(spec); } catch { return null; }
    }
    return spec;
  }
};
