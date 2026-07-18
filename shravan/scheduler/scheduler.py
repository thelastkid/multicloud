import json
import os

CLOUDS_FILE = os.path.join(os.path.dirname(__file__), "clouds.json")

with open(CLOUDS_FILE, "r") as file:
    clouds = json.load(file)


def schedule(request, cost_estimates):

    gpu_required = request["gpu"]
    region = request["region"]

    candidates = []

    for cloud, details in clouds.items():

        if cloud not in cost_estimates:
            continue

        if gpu_required and not details["gpu"]:
            continue

        if region not in details["regions"]:
            continue

        candidates.append({
            "cloud": cloud,
            "performance": details["performance_score"],
            "cost": cost_estimates[cloud]["estimated_cost"]
        })

    if not candidates:
        return {
            "selected_cloud": None,
            "reason": "No suitable cloud provider found."
        }

    candidates.sort(
        key=lambda x: (
            x["cost"],
            -x["performance"]
        )
    )

    best = candidates[0]

    return {
        "selected_cloud": best["cloud"],
        "reason": (
            f"Selected based on lowest estimated cost "
            f"({best['cost']}) and performance score."
        )
    }