from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import solve, ocr, handwriting, pdf, graph, report
from app.models.response_models import HealthResponse

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(solve.router, tags=["solve"])
app.include_router(ocr.router, tags=["ocr"])
app.include_router(handwriting.router, tags=["handwriting"])
app.include_router(pdf.router, tags=["pdf"])
app.include_router(graph.router, tags=["graph"])
app.include_router(report.router, tags=["report"])


@app.get("/health", response_model=HealthResponse)
async def health_check():
    services = {}
    try:
        import sympy
        services["sympy"] = "available"
    except ImportError:
        services["sympy"] = "unavailable"
    try:
        import numpy
        services["numpy"] = "available"
    except ImportError:
        services["numpy"] = "unavailable"
    try:
        import scipy
        services["scipy"] = "available"
    except ImportError:
        services["scipy"] = "unavailable"
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        services["tesseract"] = "available"
    except Exception:
        services["tesseract"] = "unavailable"
    try:
        import reportlab
        services["reportlab"] = "available"
    except ImportError:
        services["reportlab"] = "unavailable"

    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        services=services,
    )


@app.get("/")
async def root():
    return {"message": f"{settings.APP_NAME} v{settings.APP_VERSION}", "status": "running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
