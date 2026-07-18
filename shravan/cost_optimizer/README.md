# Cost Optimizer

## Purpose

The Cost Optimizer estimates deployment costs for each available cloud provider based on the requested resources.

## Responsibilities

- Calculate CPU cost
- Calculate memory cost
- Include GPU cost if required
- Filter unsupported regions
- Return estimated cost for each cloud

## Endpoint

POST /estimate

Example Request

```json
{
    "application":"plant-api",
    "cpu":2,
    "memory":4,
    "gpu":false,
    "region":"India"
}
```

Example Response

```json
{
    "AWS":{
        "estimated_cost":9.8
    },
    "Azure":{
        "estimated_cost":9.0
    }
}
```