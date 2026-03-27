from fastapi import APIRouter, HTTPException
from app.models.request_models import ReportRequest
from app.models.response_models import ReportResponse
from app.services.report_service import ReportService

router = APIRouter()
report_service = ReportService()


@router.post("/report", response_model=ReportResponse)
async def report_endpoint(request: ReportRequest):
    try:
        if not request.problem or not request.problem.strip():
            raise HTTPException(status_code=400, detail="Problem statement cannot be empty")

        result = report_service.generate_report(
            problem=request.problem,
            answer=request.answer,
            steps=request.steps or [],
            latex=request.latex,
            graph_base64=request.graph_base64,
            title=request.title or "Math Solution Report",
            include_timestamp=request.include_timestamp if request.include_timestamp is not None else True,
        )
        return ReportResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        return ReportResponse(pdf_base64="", error=str(e))
