import json
import os

POLICIES_FILE = os.path.join(os.path.dirname(__file__), "policies.json")

with open(POLICIES_FILE, "r") as file:
    policies = json.load(file)


def validate(request):

    if not request["application"].strip():
        return {
            "status": "rejected",
            "reason": "Application name cannot be empty."
        }

    if request["cpu"] <= 0:
        return {
            "status": "rejected",
            "reason": "CPU must be greater than 0."
        }

    if request["memory"] <= 0:
        return {
            "status": "rejected",
            "reason": "Memory must be greater than 0."
        }

    if request["cpu"] > policies["limits"]["max_cpu"]:
        return {
            "status": "rejected",
            "reason": "CPU request exceeds allowed limit."
        }

    if request["memory"] > policies["limits"]["max_memory"]:
        return {
            "status": "rejected",
            "reason": "Memory request exceeds allowed limit."
        }

    if request["region"] not in policies["supported_regions"]:
        return {
            "status": "rejected",
            "reason": "Unsupported deployment region."
        }

    if request["priority"] not in policies["supported_priorities"]:
        return {
            "status": "rejected",
            "reason": "Invalid deployment priority."
        }

    return {
        "status": "approved",
        "message": "Deployment request approved."
    }