# Arithmetic - Python Math Service

Python FastAPI backend providing mathematical computation, OCR, PDF processing, graphing, and report generation.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## System Dependencies

```bash
# Ubuntu/Debian
apt install tesseract-ocr poppler-utils
```

## Running

```bash
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check with service availability |
| `/solve` | POST | Solve math problems |
| `/ocr` | POST | Extract text from images |
| `/handwriting` | POST | Recognize handwritten math |
| `/pdf` | POST | Process PDF documents |
| `/graph` | POST | Generate graphs and charts |
| `/report` | POST | Generate PDF/HTML reports |

## Supported Math

- Arithmetic, Algebra, Calculus
- Linear Algebra, Statistics
- Differential Equations
- Optimization, Series
- Symbolic Manipulation
