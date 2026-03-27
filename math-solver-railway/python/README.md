# Arithmetic Math Solver -- Python Service

A FastAPI-based math-solving backend that provides symbolic computation, OCR, graph generation, and PDF report creation.

## Quick Start

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# (Optional) Install Tesseract for OCR features
# Ubuntu/Debian: sudo apt-get install tesseract-ocr
# macOS:         brew install tesseract

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Configuration

All settings are loaded from environment variables with sensible defaults. See `app/config.py` for the full list. Key variables:

| Variable | Default | Description |
|---|---|---|
| `PORT` | `8000` | HTTP listen port |
| `DEBUG` | `false` | Enable debug mode / hot-reload |
| `TESSERACT_CMD` | `tesseract` | Path to the Tesseract binary |
| `OPENAI_API_KEY` | *(empty)* | Optional -- enables GPT features |
| `WOLFRAM_APP_ID` | *(empty)* | Optional -- enables Wolfram Alpha |
| `MATHPIX_APP_ID` / `MATHPIX_APP_KEY` | *(empty)* | Optional -- enables Mathpix OCR |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Service info |
| `GET` | `/health` | Health check with dependency status |
| `POST` | `/solve` | Solve a math expression |
| `POST` | `/ocr` | Extract text/math from an image |
| `POST` | `/handwriting` | Recognize handwritten math |
| `POST` | `/pdf` | Extract text/math from a PDF |
| `POST` | `/graph` | Generate a graph image |
| `POST` | `/report` | Generate a PDF report |

## Project Structure

```
python/
  app/
    main.py              # FastAPI application
    config.py            # Environment-based settings
    models/              # Pydantic request/response models
    routes/              # API route handlers
    services/            # Business logic (solver, OCR, graph, etc.)
    providers/           # External API clients (OpenAI, Wolfram, Mathpix)
    utils/               # Shared utilities (image, pdf, latex, text)
  requirements.txt
```
