from pydantic import BaseModel, Field
from typing import Optional, Any


class SolveResponse(BaseModel):
    answer: str = Field(..., description="Final answer")
    steps: list[str] = Field(default_factory=list, description="Step-by-step solution")
    latex: Optional[str] = Field(None, description="LaTeX representation of answer")
    simplified: Optional[str] = Field(None, description="Simplified form")
    decimal_approx: Optional[str] = Field(None, description="Decimal approximation")
    confidence: float = Field(1.0, description="Confidence score 0-1")
    graph_data: Optional[dict] = Field(None, description="Graph data if applicable")
    problem_type: Optional[str] = Field(None, description="Detected problem type")
    verification: Optional[str] = Field(None, description="Verification result")
    error: Optional[str] = Field(None, description="Error message if any")


class OCRResponse(BaseModel):
    text: str = Field(..., description="Recognized text")
    latex: Optional[str] = Field(None, description="LaTeX interpretation")
    confidence: float = Field(0.0, description="Confidence score 0-1")
    raw_text: Optional[str] = Field(None, description="Raw OCR output before cleaning")
    error: Optional[str] = Field(None, description="Error message if any")


class HandwritingResponse(BaseModel):
    text: str = Field(..., description="Recognized text")
    latex: Optional[str] = Field(None, description="LaTeX interpretation")
    confidence: float = Field(0.0, description="Confidence score 0-1")
    raw_text: Optional[str] = Field(None, description="Raw OCR output")
    error: Optional[str] = Field(None, description="Error message if any")


class PDFPageResult(BaseModel):
    page_num: int
    text: str
    has_math: bool = False
    ocr_text: Optional[str] = None


class PDFResponse(BaseModel):
    pages: list[PDFPageResult] = Field(default_factory=list)
    total_pages: int = 0
    error: Optional[str] = None


class GraphResponse(BaseModel):
    image_base64: str = Field(..., description="Base64 encoded PNG")
    width: int = 0
    height: int = 0
    error: Optional[str] = None


class ReportResponse(BaseModel):
    pdf_base64: str = Field(..., description="Base64 encoded PDF")
    filename: str = "report.pdf"
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = ""
    services: dict[str, str] = Field(default_factory=dict)
