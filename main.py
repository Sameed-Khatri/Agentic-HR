from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
from apis.routes.agentRoute import router
from pipeline.runner import PipelineRunner
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    should_run_pipeline = True

    if os.path.exists("pipeline.lock"):
        with open("pipeline.lock", "r") as f:
            content = f.read().strip()
            if content == "done":
                should_run_pipeline = False
    
    if should_run_pipeline:
        print("Starting up, running pipeline...")
        PipelineRunner.run()

        with open("pipeline.lock", "w") as f:
            f.write("done")
        print("Pipeline completed.")
    else:
        print("Pipeline already marked as done. Skipping...")
        
    yield

    print("Shutting down...")

app = FastAPI(lifespan=lifespan, title="AgenticHR API")

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)