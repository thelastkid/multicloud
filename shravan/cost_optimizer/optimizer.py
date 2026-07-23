import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PRICING_FILE = os.path.join(os.path.dirname(__file__), "pricing.json")

try:
    with open(PRICING_FILE, "r", encoding="utf-8") as file:
        pricing = json.load(file)
except FileNotFoundError:
    logger.error("pricing.json not found.")
    raise
except json.JSONDecodeError:
    logger.error("Invalid JSON format in pricing.json.")
    raise


def estimate_cost(request: dict) -> dict:
    """Estimate deployment cost for all eligible cloud providers."""

    cpu = request["cpu"]
    memory = request["memory"]
    gpu = request["gpu"]
    region = request["region"]

    results = {}

    for cloud, details in pricing.items():

        if region not in details["regions"]:
            logger.info(f"Skipping {cloud}: Region '{region}' not supported.")
            continue

        if gpu and details["gpu_cost"] == 0:
            logger.info(f"Skipping {cloud}: GPU not supported.")
            continue

        total_cost = (
            cpu * details["cpu_cost"] +
            memory * details["memory_cost"]
        )

        if gpu:
            total_cost += details["gpu_cost"]

        results[cloud] = {
            "estimated_cost": round(total_cost, 2)
        }

    logger.info(f"Cost estimation completed for {len(results)} cloud provider(s).")

    return results