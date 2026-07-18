# Policy Engine

## Purpose

The Policy Engine validates deployment requests before they are processed by the Scheduler.

## Responsibilities

- Validate CPU requests
- Validate memory requests
- Validate deployment region
- Validate deployment priority
- Reject invalid requests

## Endpoint

POST /validate

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
    "message":"Deployment request approved."
}
```