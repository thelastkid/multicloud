from fastapi import FastAPI
from pydantic import BaseModel

from gateway import process_request

app = FastAPI(
    title="API Gateway",
    description="Entry point for the Multi-Cloud Infrastructure platform.",
    version="1.0.0"
)


class DeploymentRequest(BaseModel):
    application: str
    cpu: int
    memory: int
    gpu: bool
    region: str
    priority: str


@app.post("/deploy")
def deploy(request: DeploymentRequest):

    return process_request(request.model_dump())