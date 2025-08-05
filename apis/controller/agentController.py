from apis.service.agentService import Service
from fastapi.responses import JSONResponse
from apis.model.agentModel import GraphRequest

class Controller:
    
    def load_all_jobs() -> JSONResponse:
        result = Service.load_all_jobs()
        return JSONResponse(content=result, status_code=200)

    def load_top_candidates(job_id: str, top_n: int) -> JSONResponse:
        result = Service.load_top_candidates(job_id=job_id, top_n=top_n)
        return JSONResponse(content=result, status_code=200)
    
    def build_state_from_request(req: GraphRequest):
        return {
            "query": req.query,
            "job_id": req.job_id,
            "job_details": [jd.model_dump() for jd in req.job_details],
            "candidates": [c.model_dump() for c in req.candidates],
            "mode": "BEGIN"
        }

    def invoke_agents(request: GraphRequest) -> JSONResponse:
        state = Controller.build_state_from_request(req=request)
        result = Service.invoke_agents(state=state, thread_id=request.thread_id)
        return JSONResponse(content=result["messages"][-1].content, status_code=200)

