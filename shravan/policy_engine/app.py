from fastapi import FastAPI
from pydantic import BaseModel
import logging

from policy import validate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "policy-engine"
    }


@app.post("/validate")
def validate_request(request: DeploymentRequest):

    logger.info("Received deployment validation request.")

    result = validate(request.model_dump())

    if result["status"] == "approved":
        logger.info("Deployment request approved.")
    else:
        logger.warning(f"Deployment request rejected: {result['reason']}")

    return result