from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from apis.controller.agentController import Controller
from apis.model.agentModel import GraphRequest
from pydantic import ValidationError

router = APIRouter(prefix="/AgenticHR")

@router.get("/load-all-jobs")
def load_all_jobs() -> JSONResponse:
    return Controller.load_all_jobs()

@router.get("/get-candidates/{job_id}/{top_n}")
def load_top_candidates(job_id: str, top_n: int = 5) -> JSONResponse:
    return Controller.load_top_candidates(job_id=job_id, top_n=top_n)

@router.post("/invoke-agents")
def invoke_agents(request: GraphRequest):
    try:
        return Controller.invoke_agents(request=request)
    except ValidationError as e:
        print(e)
        raise HTTPException(status_code=422, detail=f"Validation error: {e}")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")