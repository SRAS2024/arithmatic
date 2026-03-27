import os
from pathlib import Path


class Settings:
    """Application configuration loaded from environment variables with defaults."""

    APP_NAME: str = os.getenv("APP_NAME", "Arithmetic Math Solver")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "*"
    ).split(",")

    TEMP_DIR: str = os.getenv("TEMP_DIR", "/tmp/arithmetic")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", str(50 * 1024 * 1024)))

    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "tesseract")
    TESSERACT_LANG: str = os.getenv("TESSERACT_LANG", "eng")

    GRAPH_DPI: int = int(os.getenv("GRAPH_DPI", "150"))
    GRAPH_DEFAULT_WIDTH: int = int(os.getenv("GRAPH_DEFAULT_WIDTH", "800"))
    GRAPH_DEFAULT_HEIGHT: int = int(os.getenv("GRAPH_DEFAULT_HEIGHT", "600"))

    PDF_AUTHOR: str = os.getenv("PDF_AUTHOR", "Arithmetic Math Solver")
    PDF_FONT_SIZE: int = int(os.getenv("PDF_FONT_SIZE", "12"))

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    SOLVER_TIMEOUT: int = int(os.getenv("SOLVER_TIMEOUT", "30"))
    MAX_EXPRESSION_LENGTH: int = int(os.getenv("MAX_EXPRESSION_LENGTH", "10000"))

    def __init__(self):
        Path(self.TEMP_DIR).mkdir(parents=True, exist_ok=True)


settings = Settings()
