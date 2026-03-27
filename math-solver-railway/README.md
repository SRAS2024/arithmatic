# Arithmetic

**Premium Mathematical Intelligence Platform**

A full-stack math solving application with OCR, handwritten recognition, graphing, step-by-step solutions, and beautiful PDF report generation. Built with Meteor and Python, designed for Railway deployment.

## Features

- **Multi-Engine Math Solving** — Arithmetic through postgraduate mathematics using SymPy, NumPy, SciPy
- **OCR Pipeline** — Extract math from screenshots, photos, and scanned documents
- **Handwritten Math Recognition** — Interpret handwritten equations from uploaded images
- **PDF Processing** — Extract and solve problems from PDF documents
- **Interactive Graphing** — Function plots, charts, parametric curves, statistical visualizations
- **Step-by-Step Solutions** — Detailed explanations with LaTeX rendering
- **Report Generation** — Download professional PDF and HTML solution reports
- **Beautiful UI** — Premium dark/light themes with responsive design
- **Verification Layer** — Cross-checks solutions for accuracy and confidence

## Architecture

```
┌─────────────┐    Meteor Methods    ┌──────────────┐    HTTP/REST    ┌─────────────┐
│   Browser    │ ◄──────────────────► │  Meteor      │ ◄────────────► │  Python      │
│   Client     │                      │  Server      │                │  FastAPI     │
│              │                      │  (Node.js)   │                │  Service     │
│  - KaTeX     │                      │              │                │              │
│  - Plotly    │                      │  - Orchestr. │                │  - SymPy     │
│  - Theme     │                      │  - Upload    │                │  - NumPy     │
│  - UI        │                      │  - Reports   │                │  - OCR       │
└─────────────┘                      └──────────────┘                │  - PDF       │
                                                                      │  - Graphs    │
                                                                      └─────────────┘
```

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.10+
- Meteor 3.x
- Tesseract OCR (`apt install tesseract-ocr`)
- Poppler utils (`apt install poppler-utils`)

### Development

```bash
# Install Meteor
curl https://install.meteor.com/ | sh

# Install Node dependencies
cd math-solver-railway
meteor npm install

# Setup Python environment
cd python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Start development (runs both Meteor and Python)
bash scripts/start.sh
```

### Railway Deployment

```bash
# Uses Dockerfile for build
# Configure environment variables in Railway dashboard
# Deploy with: railway up
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `3000` | Application port |
| `ROOT_URL` | `http://localhost:3000` | Meteor root URL |
| `PYTHON_SERVICE_URL` | `http://localhost:5000` | Python service URL |
| `MAX_UPLOAD_SIZE` | `20971520` | Max upload size (bytes) |
| `ENABLE_OCR` | `true` | Enable OCR features |
| `ENABLE_GRAPHING` | `true` | Enable graphing |

## Supported Math Topics

- Arithmetic & Pre-Algebra
- Algebra & Systems of Equations
- Polynomials & Factoring
- Trigonometry
- Analytic Geometry
- Matrices & Linear Algebra
- Calculus (Derivatives, Integrals, Limits)
- Differential Equations
- Series & Sequences
- Probability & Statistics
- Discrete Mathematics
- Optimization
- Symbolic Manipulation

## Testing

```bash
# Server and client tests
meteor test --driver-package meteortesting:mocha

# Python tests
cd python && pytest ../tests/python/ -v
```

## License

MIT
