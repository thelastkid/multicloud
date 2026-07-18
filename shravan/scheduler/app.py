from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

from scheduler import schedule

app = FastAPI(
    title="Resource Scheduler",
    description="Selects the most suitable cloud provider for deployment.",
    version="1.0.0"
)


class DeploymentRequest(BaseModel):
    application: str
    cpu: int
    memory: int
    gpu: bool
    region: str
    priority: str


class SchedulerRequest(BaseModel):
    request: DeploymentRequest
    cost_estimates: Dict


@app.post("/schedule")
def schedule_request(data: SchedulerRequest):

    result = schedule(
        data.request.model_dump(),
        data.cost_estimates
    )

    return result