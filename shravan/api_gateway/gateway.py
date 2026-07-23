import json
import logging
import os

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVICES_FILE = os.path.join(os.path.dirname(__file__), "services.json")

try:
    with open(SERVICES_FILE, "r", encoding="utf-8") as file:
        services = json.load(file)
except FileNotFoundError:
    logger.error("services.json not found.")
    raise
except json.JSONDecodeError:
    logger.error("Invalid JSON format in services.json.")
    raise


def process_request(request: dict) -> dict:
    """Process a deployment request through all microservices."""

    logger.info("Starting deployment workflow.")

    try:
        # Step 1 - Policy Validation
        policy_response = requests.post(
            f"{services['policy_engine']}/validate",
            json=request,
            timeout=10
        )
        policy_response.raise_for_status()

        policy_result = policy_response.json()

        if policy_result["status"] == "rejected":
            logger.warning(f"Deployment rejected: {policy_result['reason']}")
            return policy_result

        logger.info("Policy validation successful.")

        # Step 2 - Cost Estimation
        cost_response = requests.post(
            f"{services['cost_optimizer']}/estimate",
            json=request,
            timeout=10
        )
        cost_response.raise_for_status()

        cost_result = cost_response.json()

        logger.info("Cost estimation completed.")

        # Step 3 - Scheduling
        scheduler_payload = {
            "request": request,
            "cost_estimates": cost_result
        }

        scheduler_response = requests.post(
            f"{services['scheduler']}/schedule",
            json=scheduler_payload,
            timeout=10
        )
        scheduler_response.raise_for_status()

        scheduler_result = scheduler_response.json()

        logger.info(
            f"Deployment scheduled on {scheduler_result['selected_cloud']}."
        )

        return {
            "status": "approved",
            "selected_cloud": scheduler_result["selected_cloud"],
            "reason": scheduler_result["reason"],
            "cost_estimates": cost_result
        }

    except requests.exceptions.RequestException as e:
        logger.exception("Microservice communication failed.")

        return {
            "status": "failed",
            "reason": f"Gateway communication error: {str(e)}"
        }