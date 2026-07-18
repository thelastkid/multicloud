from fastapi import FastAPI
from pydantic import BaseModel

from optimizer import estimate_cost

app = FastAPI(
    title="Cost Optimizer",
    description="Calculates estimated deployment cost across cloud providers.",
    version="1.0.0"
)


class DeploymentRequest(BaseModel):
    application: str
    cpu: int
    memory: int
    gpu: bool
    region: str


@app.post("/estimate")
def estimate(request: DeploymentRequest):

    return estimate_cost(request.model_dump())