# Policy Engine API Documentation

## Overview

This is the REST API for the **MLOps Policy Engine** - a decision-making system that routes ML workloads across multi-cloud infrastructure based on intelligent policies.

### Key Features

✅ **Intelligent Task Routing** - Automatically routes training jobs to GPU clusters and inference to CPU clusters
✅ **Policy-Driven Decisions** - Makes decisions based on resource requirements, compliance, and cost optimization
✅ **Request Validation** - Comprehensive input validation for all requests
✅ **Deployment Integration** - Direct integration with deployment systems
✅ **Status Tracking** - Full job lifecycle tracking

---

## API Endpoints

### 1. Health Check
Check if the API is running and healthy.

**Endpoint:** `GET /health`

**Response:**
```json
{
    "status": "healthy",
    "service": "MLOps Policy Engine"
}
```

**cURL:**
```bash
curl -X GET http://localhost:5000/health
```

---

### 2. Submit Training Job
Submit a training workload to the policy engine. Training jobs are automatically routed to the **GPU-enabled training cluster**.

**Endpoint:** `POST /train`

**Request Body:**
```json
{
    "task_id": "train-gpu-001",
    "user_id": "data_scientist@company.com",
    "model_name": "resnet50_classifier",
    "dataset": "imagenet_2024",
    "epochs": 100,
    "batch_size": 64,
    "gpu_count": 2,
    "gpu_type": "a100",
    "memory_gb": 48,
    "priority": "high",
    "preferred_regions": ["us-east-1", "eu-west-1"],
    "budget_limit": 2000.0
}
```

**Required Fields:**
- `task_id` (string): Unique task identifier (alphanumeric, hyphens, underscores)
- `user_id` (string): User submitting the job
- `model_name` (string): Name of the model being trained
- `dataset` (string): Dataset being used
- `epochs` (integer): Number of training epochs (1-1000)
- `batch_size` (integer): Batch size (1-10000)

**Optional Fields:**
- `gpu_count` (integer): Number of GPUs needed (default: 1, max: 8)
- `gpu_type` (string): GPU type (default: "v100", options: "v100", "a100", "t4", "h100", "rtx_a6000")
- `memory_gb` (float): Memory required (default: 32, range: 4-256)
- `priority` (string): Job priority (default: "normal", options: "low", "normal", "high", "critical")
- `preferred_regions` (array): Preferred AWS regions (default: ["us-east-1"])
- `budget_limit` (float): Maximum budget for this job

**Response (Success - 201):**
```json
{
    "success": true,
    "task_id": "train-gpu-001",
    "message": "Training job submitted successfully",
    "policy_decision": {
        "cluster": "training_cluster",
        "cluster_description": "GPU-enabled training cluster optimized for ML model training",
        "cluster_type": "gpu",
        "compute_type": "gpu",
        "gpu_type": "a100",
        "gpu_count": 2,
        "memory_gb": 48,
        "recommendation": "Use 2x a100 GPU(s) with 48GB memory",
        "estimated_throughput": 200
    },
    "deployment": {
        "success": true,
        "task_id": "train-gpu-001",
        "cluster": "training_cluster",
        "status": "pending",
        "message": "Training job train-gpu-001 submitted to training cluster",
        "created_at": "2024-03-29T10:30:45.123456",
        "job_url": "http://training-cluster.local/jobs/train-gpu-001"
    }
}
```

**cURL Examples:**

Basic training job:
```bash
curl -X POST http://localhost:5000/train \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "train-001",
    "user_id": "user@company.com",
    "model_name": "my_model",
    "dataset": "training_data",
    "epochs": 50,
    "batch_size": 32,
    "gpu_count": 2,
    "memory_gb": 48
  }'
```

High-priority training with budget limit:
```bash
curl -X POST http://localhost:5000/train \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "train-hpe-001",
    "user_id": "lead_scientist@company.com",
    "model_name": "bert_large",
    "dataset": "wikipedia_dump",
    "epochs": 100,
    "batch_size": 64,
    "gpu_count": 8,
    "gpu_type": "h100",
    "memory_gb": 80,
    "priority": "critical",
    "budget_limit": 5000
  }'
```

---

### 3. Submit Model Deployment
Deploy a trained model to the inference cluster. Deployment jobs are automatically routed to the **CPU-optimized inference cluster**.

**Endpoint:** `POST /deploy`

**Request Body:**
```json
{
    "task_id": "deploy-inf-001",
    "user_id": "devops@company.com",
    "model_id": "resnet50_classifier",
    "model_version": "2.1.3",
    "target_platform": "kubernetes",
    "replicas": 3,
    "max_replicas": 10,
    "cpu_limit": "4",
    "memory_limit": "4Gi",
    "priority": "normal",
    "preferred_regions": ["us-east-1"]
}
```

**Required Fields:**
- `task_id` (string): Unique deployment identifier
- `user_id` (string): User performing the deployment
- `model_id` (string): ID of the model to deploy
- `model_version` (string): Semantic version (e.g., "1.0.0")
- `target_platform` (string): Platform for deployment (options: "kubernetes", "docker", "serverless", "edge")

**Optional Fields:**
- `replicas` (integer): Number of replicas (default: 1, range: 1-100)
- `max_replicas` (integer): Maximum replicas for autoscaling (default: replicas × 2)
- `cpu_limit` (string): CPU limit per replica (default: "2")
- `memory_limit` (string): Memory limit per replica (default: "2Gi")
- `priority` (string): Deployment priority (default: "normal")
- `preferred_regions` (array): Preferred regions

**Response (Success - 201):**
```json
{
    "success": true,
    "task_id": "deploy-inf-001",
    "message": "Deployment submitted successfully",
    "policy_decision": {
        "cluster": "inference_cluster",
        "cluster_description": "CPU-optimized inference cluster for model serving and inference",
        "cluster_type": "cpu",
        "compute_type": "cpu",
        "cpu_cores": 2,
        "memory_gb": 2,
        "recommendation": "Use CPU with 2 cores and 2GB memory"
    },
    "deployment": {
        "success": true,
        "task_id": "deploy-inf-001",
        "cluster": "inference_cluster",
        "platform": "kubernetes",
        "status": "pending",
        "message": "Deployment deploy-inf-001 submitted to inference cluster",
        "created_at": "2024-03-29T10:35:22.987654",
        "deployment_url": "http://inference-cluster.local/deployments/deploy-inf-001"
    }
}
```

**cURL Examples:**

Basic deployment:
```bash
curl -X POST http://localhost:5000/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "deploy-001",
    "user_id": "devops@company.com",
    "model_id": "my_model",
    "model_version": "1.0.0",
    "target_platform": "kubernetes",
    "replicas": 3
  }'
```

High-availability deployment with autoscaling:
```bash
curl -X POST http://localhost:5000/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "deploy-prod-001",
    "user_id": "platform_lead@company.com",
    "model_id": "recommendation_engine",
    "model_version": "3.2.1",
    "target_platform": "kubernetes",
    "replicas": 10,
    "max_replicas": 50,
    "cpu_limit": "8",
    "memory_limit": "8Gi",
    "priority": "high"
  }'
```

---

### 4. Check Job Status
Get the current status of a training job or deployment.

**Endpoint:** `GET /status/<task_id>` or `POST /status`

**GET Variant:**
```bash
GET /status/train-gpu-001
```

**POST Variant Request Body:**
```json
{
    "task_id": "train-gpu-001"
}
```

**Response:**
```json
{
    "success": true,
    "task_id": "train-gpu-001",
    "status": "running",
    "cluster": "training_cluster",
    "platform": "kubernetes",
    "user_id": "data_scientist@company.com",
    "model_id": "resnet50_classifier",
    "created_at": "2024-03-29T10:30:45.123456",
    "updated_at": "2024-03-29T10:35:12.654321",
    "metadata": {
        "gpu_count": 2,
        "gpu_type": "a100",
        "memory_gb": 48,
        "epochs": 100,
        "batch_size": 64,
        "dataset": "imagenet_2024",
        "priority": "high"
    },
    "progress": 50,
    "logs": [
        "[RUNNING] Job train-gpu-001 is processing",
        "[INFO] Allocated resources on training_cluster",
        "[INFO] Model: resnet50_classifier"
    ]
}
```

**Possible Status Values:**
- `pending` - Job is queued, waiting to start
- `running` - Job is currently executing
- `completed` - Job finished successfully
- `failed` - Job encountered an error
- `cancelled` - Job was cancelled

**cURL Examples:**

Check status via GET:
```bash
curl -X GET http://localhost:5000/status/train-gpu-001
```

Check status via POST:
```bash
curl -X POST http://localhost:5000/status \
  -H "Content-Type: application/json" \
  -d '{"task_id": "deploy-inf-001"}'
```

---

### 5. List All Policies
Retrieve all defined policies.

**Endpoint:** `GET /api/v1/policies`

**Response:**
```json
{
    "policies": [
        "resource_optimization",
        "cost_management",
        "compliance_enforcement",
        "priority_scheduling"
    ]
}
```

**cURL:**
```bash
curl -X GET http://localhost:5000/api/v1/policies
```

---

### 6. Get Specific Policy
Retrieve details of a specific policy.

**Endpoint:** `GET /api/v1/policies/<policy_name>`

**Response:**
```json
{
    "policy": {
        "name": "resource_optimization",
        "description": "Optimize resource allocation for different task types",
        "rules": [...]
    }
}
```

**cURL:**
```bash
curl -X GET http://localhost:5000/api/v1/policies/resource_optimization
```

---

### 7. Get Metrics
Retrieve engine metrics and statistics.

**Endpoint:** `GET /api/v1/metrics`

**Response:**
```json
{
    "metrics": {
        "total_tasks_evaluated": 245,
        "training_tasks": 120,
        "inference_tasks": 125,
        "avg_decision_time_ms": 45,
        "policy_engine_uptime_hours": 168
    }
}
```

**cURL:**
```bash
curl -X GET http://localhost:5000/api/v1/metrics
```

---

## Error Handling

### Common Error Responses

**400 Bad Request** - Invalid input or validation error:
```json
{
    "error": "Missing required field: task_id"
}
```

**404 Not Found** - Resource not found:
```json
{
    "success": false,
    "error": "Task train-nonexistent not found",
    "status": null
}
```

**500 Internal Server Error** - Server error:
```json
{
    "error": "Internal server error"
}
```

---

## Validation Rules

### Task ID Validation
- Format: alphanumeric with hyphens and underscores (e.g., `train-gpu-001`, `deploy_prod_v2`)
- Required for all job submissions and status checks

### GPU Configuration
- `gpu_count`: 0-8 (0 means CPU-only)
- `gpu_type`: Must be one of `[v100, a100, t4, h100, rtx_a6000]`
- `memory_gb`: 4-256 GB

### Training Job Validation
- `epochs`: 1-1000
- `batch_size`: 1-10000
- All required fields must be present

### Deployment Validation
- `model_version`: Must follow semantic versioning (X.Y.Z)
- `target_platform`: Must be one of `[kubernetes, docker, serverless, edge]`
- `replicas`: 1-100

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│         REST API Layer                      │
│  /train  |  /deploy  |  /status            │
└──────────────────────────────────────────┬──┘
                                           │
┌──────────────────────────────────────────▼──┐
│    Request Validator                        │
│  - Validates input data                     │
│  - Enforces validation rules                │
└──────────────────────────────────────────┬──┘
                                           │
┌──────────────────────────────────────────▼──┐
│    Policy Engine Core                       │
│  - Evaluates policies                       │
│  - Routes to GPU or CPU cluster             │
│  - Resource optimization                    │
└──────────────────────────────────────────┬──┘
                                           │
┌──────────────────────────────────────────▼──┐
│    Deployment Connector                     │
│  - Submits to training_cluster (GPU)        │
│  - Submits to inference_cluster (CPU)       │
│  - Tracks job status                        │
└─────────────────────────────────────────────┘
```

---

## Routing Logic

### Training Jobs → GPU Cluster
- **When:** `GPU required = true` OR `task_type = training`
- **Cluster:** `training_cluster` (GPU-enabled)
- **Optimization:** Maximize throughput with GPU parallelization

### Inference Jobs → CPU Cluster
- **When:** `GPU required = false` OR `task_type = inference`
- **Cluster:** `inference_cluster` (CPU-optimized)
- **Optimization:** Cost-effective CPU serving with horizontal scaling

---

## Getting Started

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# or with poetry
poetry install
```

### Running the API

```bash
# Run directly
python -m policy_engine.api.rest_api

# or using Flask
flask --app policy_engine.api.rest_api run

# with custom port
python -m policy_engine.api.rest_api --port 8000
```

### Running Tests

```bash
# Run comprehensive test suite
python test_api.py

# Run specific tests
pytest tests/ -v
```

---

## Example Workflow

### Complete Training Pipeline

```bash
# 1. Submit training job
curl -X POST http://localhost:5000/train \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "train-cifar10-001",
    "user_id": "alice@company.com",
    "model_name": "vgg16",
    "dataset": "cifar10",
    "epochs": 50,
    "batch_size": 128,
    "gpu_count": 2,
    "gpu_type": "a100",
    "memory_gb": 48
  }'

# Response contains: task_id (save this for status checks)

# 2. Check status (repeat as needed)
curl -X GET http://localhost:5000/status/train-cifar10-001

# 3. Once training complete, deploy model
curl -X POST http://localhost:5000/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "deploy-cifar10-001",
    "user_id": "devops@company.com",
    "model_id": "vgg16",
    "model_version": "1.0.0",
    "target_platform": "kubernetes",
    "replicas": 5
  }'

# 4. Check deployment status
curl -X GET http://localhost:5000/status/deploy-cifar10-001
```

---

## Support & Troubleshooting

### Common Issues

**Cannot connect to API:**
- Ensure API is running: `curl http://localhost:5000/health`
- Check port is correct (default: 5000)
- Verify firewall allows connections

**Validation errors:**
- Review the exact error message
- Ensure all required fields are present
- Check field formats match requirements

**Job stuck in pending:**
- Check cluster resources availability
- Review priority queue
- Check logs for errors

---

## Performance & Limits

- Maximum concurrent tasks: 1000
- Maximum request size: 10MB
- Request timeout: 30 seconds
- Task history retention: 30 days

---

For more information, see [README.md](README.md) and [BUILD_SUMMARY.md](BUILD_SUMMARY.md)
