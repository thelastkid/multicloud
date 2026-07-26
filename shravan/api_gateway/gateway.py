import logging

from policy import validate
from optimizer import estimate_cost
from scheduler import schedule

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_request(request: dict) -> dict:
    """Process a deployment request through all modules."""

    logger.info("Starting deployment workflow.")

    try:
        # Step 1 - Policy Validation
        policy_result = validate(request)

        if policy_result["status"] == "rejected":
            logger.warning(
                f"Deployment rejected: {policy_result['reason']}"
            )
            return policy_result

        logger.info("Policy validation successful.")

        # Step 2 - Cost Estimation
        cost_result = estimate_cost(request)

        logger.info("Cost estimation completed.")

        # Step 3 - Scheduling
        scheduler_result = schedule(request, cost_result)

        logger.info(
            f"Deployment scheduled on "
            f"{scheduler_result['selected_cloud']}."
        )

        return {
            "status": "approved",
            "selected_cloud": scheduler_result["selected_cloud"],
            "reason": scheduler_result["reason"],
            "cost_estimates": cost_result
        }

    except Exception as e:
        logger.exception("Deployment failed.")

        return {
            "status": "failed",
            "reason": str(e)
        }