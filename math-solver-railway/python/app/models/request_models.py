from pydantic import BaseModel, Field
from typing import Optional


class SolveRequest(BaseModel):
    expression: str = Field(..., description="Math expression or problem to solve")
    problem_type: Optional[str] = Field(
        None,
        description="Type of problem: arithmetic, algebra, calculus, linear_algebra, stats, equation, system, differential_equation, optimization",
    )
    variables: Optional[list[str]] = Field(None, description="Variables in the expression")
    precision: Optional[int] = Field(15, description="Decimal precision for numeric results")
    show_steps: Optional[bool] = Field(True, description="Whether to show solution steps")
    verify: Optional[bool] = Field(True, description="Whether to verify the solution")


class GraphRequest(BaseModel):
    expression: str = Field(..., description="Expression to graph")
    graph_type: Optional[str] = Field(
        "function",
        description="Type: function, implicit, parametric, polar, scatter, bar, pie, histogram, line",
    )
    options: Optional[dict] = Field(default_factory=dict, description="Graph options")


class ReportRequest(BaseModel):
    problem: str = Field(..., description="Original problem statement")
    answer: str = Field(..., description="Final answer")
    steps: Optional[list[str]] = Field(default_factory=list, description="Solution steps")
    latex: Optional[str] = Field(None, description="LaTeX representation")
    graph_base64: Optional[str] = Field(None, description="Base64 encoded graph image")
    title: Optional[str] = Field("Math Solution Report", description="Report title")
    include_timestamp: Optional[bool] = Field(True, description="Include timestamp")


class OCRRequest(BaseModel):
    language: Optional[str] = Field("eng", description="OCR language")
    preprocess: Optional[bool] = Field(True, description="Apply preprocessing")


class HandwritingRequest(BaseModel):
    language: Optional[str] = Field("eng", description="OCR language")
    enhance: Optional[bool] = Field(True, description="Apply enhancement")
