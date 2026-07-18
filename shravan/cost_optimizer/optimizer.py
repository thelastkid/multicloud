import json
import os

PRICING_FILE = os.path.join(os.path.dirname(__file__), "pricing.json")

with open(PRICING_FILE, "r") as file:
    pricing = json.load(file)


def estimate_cost(request):

    cpu = request["cpu"]
    memory = request["memory"]
    gpu = request["gpu"]
    region = request["region"]

    results = {}

    for cloud, details in pricing.items():

        if region not in details["regions"]:
            continue

        if gpu and details["gpu_cost"] == 0:
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

    return results