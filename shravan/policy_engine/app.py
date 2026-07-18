from fastapi import FastAPI
from pydantic import BaseModel

from policy import validate

app = FastAPI(
    title="Policy Engine",
    description="Validates deployment requests against predefined policies.",
    version="1.0.0"
)


class DeploymentRequest(BaseModel):
    application: str
    cpu: int
    memory: int
    gpu: bool
    region: str
    priority: str


@app.post("/validate")
def validate_request(request: DeploymentRequest):

    return validate(request.model_dump())