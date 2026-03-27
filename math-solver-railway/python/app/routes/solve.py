from fastapi import APIRouter, HTTPException
from app.models.request_models import SolveRequest
from app.models.response_models import SolveResponse
from app.services.solve_service import SolveService

router = APIRouter()
solver = SolveService()


@router.post("/solve", response_model=SolveResponse)
async def solve(request: SolveRequest):
    try:
        if not request.expression or not request.expression.strip():
            raise HTTPException(status_code=400, detail="Expression cannot be empty")

        if len(request.expression) > 10000:
            raise HTTPException(status_code=400, detail="Expression too long (max 10000 chars)")

        result = solver.solve(
            expression=request.expression,
            problem_type=request.problem_type,
            variables=request.variables,
            precision=request.precision or 15,
            show_steps=request.show_steps if request.show_steps is not None else True,
            verify=request.verify if request.verify is not None else True,
        )
        return SolveResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        return SolveResponse(
            answer="Error",
            error=str(e),
            confidence=0.0,
        )
