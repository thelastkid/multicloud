import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

POLICIES_FILE = os.path.join(os.path.dirname(__file__), "policies.json")

try:
    with open(POLICIES_FILE, "r", encoding="utf-8") as file:
        policies = json.load(file)
except FileNotFoundError:
    logger.error("policies.json not found.")
    raise
except json.JSONDecodeError:
    logger.error("Invalid JSON format in policies.json.")
    raise


def reject(reason: str) -> dict:
    return {
        "status": "rejected",
        "reason": reason
    }


def validate(request: dict) -> dict:
    """Validate deployment request against configured policies."""

    if not request["application"].strip():
        return reject("Application name cannot be empty.")

    if request["cpu"] <= 0:
        return reject("CPU must be greater than 0.")

    if request["memory"] <= 0:
        return reject("Memory must be greater than 0.")

    if request["cpu"] > policies["limits"]["max_cpu"]:
        return reject("CPU request exceeds allowed limit.")

    if request["memory"] > policies["limits"]["max_memory"]:
        return reject("Memory request exceeds allowed limit.")

    if request["region"] not in policies["supported_regions"]:
        return reject("Unsupported deployment region.")

    if request["priority"] not in policies["supported_priorities"]:
        return reject("Invalid deployment priority.")

    logger.info("Deployment request passed all policy checks.")

    return {
        "status": "approved",
        "message": "Deployment request approved."
    }