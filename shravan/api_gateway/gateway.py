import json
import os
import requests

SERVICES_FILE = os.path.join(os.path.dirname(__file__), "services.json")

with open(SERVICES_FILE, "r") as file:
    services = json.load(file)


def process_request(request):

    # Step 1 - Policy Validation
    policy_response = requests.post(
        f"{services['policy_engine']}/validate",
        json=request
    )

    policy_result = policy_response.json()

    if policy_result["status"] == "rejected":
        return policy_result

    # Step 2 - Cost Estimation
    cost_response = requests.post(
        f"{services['cost_optimizer']}/estimate",
        json=request
    )

    cost_result = cost_response.json()

    # Step 3 - Scheduling
    scheduler_payload = {
        "request": request,
        "cost_estimates": cost_result
    }

    scheduler_response = requests.post(
        f"{services['scheduler']}/schedule",
        json=scheduler_payload
    )

    scheduler_result = scheduler_response.json()

    return {
        "status": "approved",
        "selected_cloud": scheduler_result["selected_cloud"],
        "reason": scheduler_result["reason"],
        "cost_estimates": cost_result
    }