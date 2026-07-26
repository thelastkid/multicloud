import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CLOUDS_FILE = os.path.join(os.path.dirname(__file__), "clouds.json")

try:
    with open(CLOUDS_FILE, "r", encoding="utf-8") as file:
        clouds = json.load(file)
except FileNotFoundError:
    logger.error("clouds.json not found.")
    raise
except json.JSONDecodeError:
    logger.error("Invalid JSON format in clouds.json.")
    raise


def schedule(request: dict, cost_estimates: dict) -> dict:
    """Select the best cloud provider based on deployment priority."""

    gpu_required = request["gpu"]
    region = request["region"]
    priority = request["priority"]

    candidates = []

    for cloud, details in clouds.items():

        if cloud not in cost_estimates:
            logger.info(f"Skipping {cloud}: No cost estimate available.")
            continue

        if gpu_required and not details["gpu"]:
            logger.info(f"Skipping {cloud}: GPU not supported.")
            continue

        if region not in details["regions"]:
            logger.info(f"Skipping {cloud}: Region '{region}' not supported.")
            continue

        candidates.append({
            "cloud": cloud,
            "performance": details["performance_score"],
            "cost": cost_estimates[cloud]["estimated_cost"]
        })

    if not candidates:
        logger.warning("No suitable cloud provider found.")

        return {
            "selected_cloud": None,
            "reason": "No suitable cloud provider found."
        }

    # Scheduling based on priority
    if priority == "low":

        # Lowest cost first, then performance
        candidates.sort(
            key=lambda candidate: (
                candidate["cost"],
                -candidate["performance"]
            )
        )

        reason = (
            f"Selected {candidates[0]['cloud']} because Low priority "
            f"favours minimum deployment cost "
            f"(₹{candidates[0]['cost']})."
        )

    elif priority == "high":

        # Highest performance first, then cost
        candidates.sort(
            key=lambda candidate: (
                -candidate["performance"],
                candidate["cost"]
            )
        )

        reason = (
            f"Selected {candidates[0]['cloud']} because High priority "
            f"favours maximum performance "
            f"(Score: {candidates[0]['performance']})."
        )

    else:  # medium

        # Balanced score
        candidates.sort(
            key=lambda candidate: (
                candidate["cost"] * 0.4 - candidate["performance"] * 0.6
            )
        )

        reason = (
            f"Selected {candidates[0]['cloud']} because Medium priority "
            f"balances cost and performance."
        )

    best = candidates[0]

    logger.info(
        f"Selected {best['cloud']} "
        f"(Cost: {best['cost']}, Performance: {best['performance']})"
    )

    return {
        "selected_cloud": best["cloud"],
        "reason": reason
    }