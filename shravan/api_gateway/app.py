import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from gateway import process_request
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Gateway",
    description="Entry point for the Multi-Cloud Infrastructure platform.",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","https://multicloud-eight.vercel.app"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
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
        "service": "api-gateway"
    }


@app.post("/deploy")
def deploy(request: DeploymentRequest):

    logger.info("Received deployment request.")

    try:
        result = process_request(request.model_dump())

        logger.info("Deployment request processed successfully.")

        return result

    except Exception as e:
        logger.exception("Deployment request failed.")

        raise HTTPException(
            status_code=500,
            detail=f"Deployment failed: {str(e)}"
        )