from fastapi import APIRouter, HTTPException
from app.models.request_models import GraphRequest
from app.models.response_models import GraphResponse
from app.services.graph_service import GraphService

router = APIRouter()
graph_service = GraphService()


@router.post("/graph", response_model=GraphResponse)
async def graph_endpoint(request: GraphRequest):
    try:
        if not request.expression or not request.expression.strip():
            raise HTTPException(status_code=400, detail="Expression cannot be empty")

        result = graph_service.generate_graph(
            expression=request.expression,
            graph_type=request.graph_type or "function",
            options=request.options or {},
        )
        return GraphResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        return GraphResponse(image_base64="", error=str(e))
