# Scheduler Service

## Purpose

The Scheduler Service determines the most appropriate cloud provider for deploying a machine learning application.

## Responsibilities

- Accept deployment requests.
- Evaluate cloud capabilities.
- Match GPU requirements.
- Match deployment region.
- Select the best cloud provider.

## Endpoint

POST /schedule

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
    "selected_cloud":"Azure",
    "reason":"Best matching cloud based on GPU availability, region and performance."
}
```