# API Gateway

## Purpose

The API Gateway is the single entry point for deployment requests. It coordinates communication between the Policy Engine, Cost Optimizer, and Scheduler.

## Workflow

1. Validate request using the Policy Engine.
2. Estimate deployment costs using the Cost Optimizer.
3. Select the best cloud using the Scheduler.
4. Return the final deployment decision.

## Endpoint

POST /deploy

Example Request

```json
{
    "application":"plant-api",
    "cpu":2,
    "memory":4,
    "gpu":false,
    "region":"India",
    "priority":"medium"
}
```

Example Response

```json
{
    "status":"approved",
    "selected_cloud":"Azure",
    "reason":"Best matching cloud based on GPU availability, region and performance.",
    "cost_estimates":{
        "AWS":{"estimated_cost":9.8},
        "Azure":{"estimated_cost":9.0}
    }
}
```