# Policy Engine: Complete Step-by-Step Walkthrough

## Overview

The **Policy Engine** is a decision-making backend that intelligently routes ML workloads to different cloud clusters based on resource requirements, validates all requests, and tracks job status throughout their lifecycle.

**Main Goal:** Route training jobs → GPU cluster | Deploy jobs → CPU cluster

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    INCOMING REQUEST                           │
│         (Train job or Deployment request from user)           │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
         ┌──────────────────────────────┐
         │  REQUEST VALIDATOR MODULE    │
         │  (Validate input constraints)│
         └──────────────┬───────────────┘
                        │
        ┌───────────────┴───────────────┐
        │  VALID?                       │
        │                               │
  ┌─────▼─────┐                  ┌─────▼──────┐
  │   YES     │                  │    NO      │
  └─────┬─────┘                  └─────┬──────┘
        │                              │
        ▼                              ▼
  ┌────────────────┐           [REJECT + ERROR MSG]
  │ POLICY ENGINE  │
  │ (Make Decision)│
  └────────┬───────┘
           │
    ┌──────┴──────┐
    │  CLUSTER?   │
    │             │
┌───▼──┐     ┌───▼───┐
│Training    │Inference
│_Cluster   │_Cluster
└───┬──┐     └───┬───┘
    │ │         │ │
    ▼ ▼         ▼ ▼
  GPU  │      CPU │
        │         │
        ▼         ▼
┌──────────────────────────────────────┐
│ DEPLOYMENT CONNECTOR MODULE          │
│ (Submit & track job status)          │
└──────────────┬───────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
[SUBMITTED]         [STATUS TRACKING]
Job ID returned      Job progress updated
```

---

## Step-by-Step Flow

### Step 1: User Submits Training Request

**Request comes in with training job details:**

```json
{
  "task_id": "train-001",
  "user_id": "alice@company.com",
  "model_name": "ResNet50",
  "dataset": "MNIST",
  "epochs": 50,
  "batch_size": 32,
  "gpu_count": 2,
  "gpu_type": "v100",
  "memory_gb": 32,
  "priority": "high"
}
```

---

### Step 2: Request Validator Module (Validation Layer)

The **Request Validator** checks if ALL requirements are met:

#### ✅ VALIDATION CHECKS:

| Check | Rule | Value | Result |
|-------|------|-------|--------|
| Epochs valid? | 1-1000 range | 50 | ✅ PASS |
| Batch size valid? | 1-10000 range | 32 | ✅ PASS |
| GPU count valid? | 0-8 range | 2 | ✅ PASS |
| Memory valid? | 4-256 GB range | 32 | ✅ PASS |
| GPU type valid? | v100/a100/t4/h100/rtx_a6000 | v100 | ✅ PASS |
| Task ID valid? | Must exist | train-001 | ✅ PASS |
| User ID valid? | Must exist | alice@company.com | ✅ PASS |

**Validator Result:**
```
✅ VALID - All constraints satisfied
Return: {
  "is_valid": true,
  "error": null,
  "cleaned_data": {
    "task_id": "train-001",
    "epochs": 50,
    "batch_size": 32,
    "gpu_count": 2,
    "gpu_type": "v100",
    "memory_gb": 32,
    ...
  }
}
```

---

### Step 3: Example - INVALID Request (Rejection Case)

**What if someone tried epochs = 5000?**

```json
{
  "epochs": 5000,  // EXCEEDS MAX OF 1000
  "batch_size": 32,
  "gpu_count": 2,
  "memory_gb": 32
}
```

**Validator checks:**
```
Epochs: 5000 > 1000? → YES, INVALID! ❌
```

**Result:**
```json
{
  "is_valid": false,
  "error": "Epochs must be between 1 and 1000. Got 5000.",
  "cleaned_data": null
}
```

**Response to user:** `❌ REJECTED - Error: Epochs must be between 1 and 1000`

---

### Step 4: Policy Engine Decision Making

Once validation passes, the **Policy Engine** evaluates policies:

#### THE KEY DECISION: Which cluster?

```
RULE:
  IF gpu_count > 0 THEN
    Route to: training_cluster (optimized for GPU throughput)
  ELSE
    Route to: inference_cluster (optimized for cost)
```

#### Example Analysis:

**train-001** (ResNet50):
```
gpu_count = 2 (> 0)
→ DECISION: training_cluster
Reason: GPU-intensive training workload
```

**train-002** (BERT):
```
gpu_count = 4 (> 0)
→ DECISION: training_cluster
Reason: Multi-GPU distributed training
```

**train-003** (XGBoost):
```
gpu_count = 0 (NO GPU NEEDED)
→ DECISION: inference_cluster
Reason: CPU-only workload, optimize for cost
```

---

### Step 5: Deployment Connector - Job Submission

After decision, the **Deployment Connector** submits to the chosen cluster:

#### For train-001 (GPU → training_cluster):

```
SUBMISSION FLOW:

1. Extract config from cleaned_data:
   ├─ task_id: train-001
   ├─ model: ResNet50
   ├─ epochs: 50
   ├─ gpus: 2x v100
   └─ memory: 32GB

2. Generate job ID:
   └─ job_uuid = "a7f3-2891-4c9d"

3. Submit to training_cluster:
   ├─ Cluster receives config
   ├─ Allocates 2x V100 GPUs
   ├─ Provisions 32GB memory
   └─ Starts training

4. Return confirmation:
   {
     "success": true,
     "task_id": "train-001",
     "job_url": "https://training-cluster/jobs/a7f3-2891-4c9d",
     "cluster": "training_cluster",
     "status": "submitted",
     "eta": "12 hours"
   }
```

#### For deploy-001 (Kubernetes → inference_cluster):

```
SUBMISSION FLOW:

1. Extract config from cleaned_data:
   ├─ task_id: deploy-001
   ├─ model_id: ResNet50
   ├─ version: 1.5.0
   ├─ platform: kubernetes
   └─ replicas: 3

2. Submit to inference_cluster:
   ├─ Cluster validates version format
   ├─ Creates Kubernetes deployment
   ├─ Spins up 3 replicas
   └─ Exposes endpoint

3. Return confirmation:
   {
     "success": true,
     "task_id": "deploy-001",
     "deployment_url": "https://inference-cluster/deploy/resnet50-v1.5.0",
     "cluster": "inference_cluster",
     "status": "deployed",
     "endpoint": "http://resnet50-api.inference-cluster.svc"
   }
```

---

### Step 6: Status Tracking

User can query job status at any time:

#### For train-001:
```
API Call: GET /status/train-001

Response after 2 hours:
{
  "task_id": "train-001",
  "status": "running",
  "progress": "35%",
  "current_epoch": "18/50",
  "estimated_time_remaining": "10 hours",
  "logs": "Epoch 18: loss=0.312, acc=0.89"
}
```

#### For train-002:
```
API Call: GET /status/train-002

Response when complete:
{
  "task_id": "train-002",
  "status": "completed",
  "final_accuracy": 0.92,
  "total_time": "48 hours",
  "model_checkpoint": "s3://models/bert/v1.2.0/checkpoint-best.pt",
  "logs": "Training complete - Ready for deployment"
}
```

#### For deploy-001:
```
API Call: GET /status/deploy-001

Response after deployment:
{
  "task_id": "deploy-001",
  "status": "deployed",
  "replicas_ready": 3,
  "replicas_total": 3,
  "service_endpoint": "http://resnet50-api.example.com",
  "requests_per_minute": 1250,
  "average_latency_ms": 45
}
```

---

## Complete Example Journey: train-001

### Timeline:

```
TIME 0:00 - USER SUBMITS REQUEST
┌─────────────────────────────────────────────────────┐
│ POST /train                                         │
│ {                                                   │
│   "task_id": "train-001",                           │
│   "model_name": "ResNet50",                         │
│   "epochs": 50,                                     │
│   "gpu_count": 2,                                   │
│   "gpu_type": "v100",                               │
│   "memory_gb": 32                                   │
│ }                                                   │
└─────────────────────────────────────────────────────┘

TIME 0:01 - VALIDATION PHASE
┌─────────────────────────────────────────────────────┐
│ REQUEST VALIDATOR                                   │
│ ✅ epochs: 50 (valid: 1-1000)                       │
│ ✅ batch_size: 32 (valid: 1-10000)                  │
│ ✅ gpu_count: 2 (valid: 0-8)                        │
│ ✅ memory_gb: 32 (valid: 4-256)                     │
│ ✅ gpu_type: v100 (valid type)                      │
│ Result: VALIDATES ✅                                │
└─────────────────────────────────────────────────────┘

TIME 0:02 - POLICY DECISION
┌─────────────────────────────────────────────────────┐
│ POLICY ENGINE ANALYSIS                              │
│ gpu_count = 2 (> 0)                                │
│ → Route to: training_cluster                        │
│ → Priority: high                                    │
│ → Allocate: 2x V100 GPUs, 32GB RAM                 │
│ Decision: APPROVED FOR GPU TRAINING ✅             │
└─────────────────────────────────────────────────────┘

TIME 0:03 - SUBMISSION
┌─────────────────────────────────────────────────────┐
│ DEPLOYMENT CONNECTOR                                │
│ Submit config to training_cluster:                  │
│   - Generate job_id: a7f3-2891                      │
│   - Reserve 2x V100 GPUs                            │
│   - Allocate 32GB GPU memory                        │
│   - Prepare training container                      │
│ Result: SUBMITTED ✅                                │
└─────────────────────────────────────────────────────┘

RESPONSE TO USER (TIME 0:04):
┌─────────────────────────────────────────────────────┐
│ HTTP 200 OK                                         │
│ {                                                   │
│   "success": true,                                  │
│   "task_id": "train-001",                           │
│   "cluster": "training_cluster",                    │
│   "job_url": "https://cluster/jobs/a7f3-2891",     │
│   "status": "submitted",                            │
│   "eta": "12 hours"                                 │
│ }                                                   │
│                                                     │
│ MESSAGE: "Training job submitted. Check status     │
│ with: GET /status/train-001"                        │
└─────────────────────────────────────────────────────┘

TIME +2 HOURS - USER CHECKS PROGRESS
┌─────────────────────────────────────────────────────┐
│ GET /status/train-001                               │
│ Response:                                           │
│ {                                                   │
│   "status": "running",                              │
│   "progress": "35%",                                │
│   "current_epoch": "18/50",                         │
│   "elapsed_time": "2 hours",                        │
│   "eta": "10 hours"                                 │
│ }                                                   │
└─────────────────────────────────────────────────────┘

TIME +12 HOURS - TRAINING COMPLETE
┌─────────────────────────────────────────────────────┐
│ Job Complete! Status: GET /status/train-001         │
│ {                                                   │
│   "status": "completed",                            │
│   "final_accuracy": 0.89,                           │
│   "final_loss": 0.21,                               │
│   "total_epochs": 50,                               │
│   "total_time": "12 hours",                         │
│   "checkpoint_url": "s3://models/resnet50-v1.0"    │
│ }                                                   │
└─────────────────────────────────────────────────────┘
```

---

## Comparison: Three Different Scenarios

### SCENARIO 1: train-001 (GPU Training - ResNet50)

```
INPUT:
├─ epochs: 50
├─ gpu_count: 2
├─ gpu_type: v100
└─ memory: 32GB

VALIDATION: ✅ PASS
POLICY: gpu_count=2 > 0 → training_cluster
CLUSTER ASSIGNMENT: training_cluster (with GPU)
STATUS: Submitted for GPU-intensive training
```

### SCENARIO 2: train-003 (CPU Only - XGBoost)

```
INPUT:
├─ epochs: 10
├─ gpu_count: 0  ← NO GPU
├─ gpu_type: null
└─ memory: 16GB

VALIDATION: ✅ PASS (CPU workload valid)
POLICY: gpu_count=0 (no GPU needed) → inference_cluster  
CLUSTER ASSIGNMENT: inference_cluster (CPU optimized)
STATUS: Submitted for cost-optimized CPU inference
```

### SCENARIO 3: Invalid Request (epochs=5000)

```
INPUT:
├─ epochs: 5000  ← EXCEEDS LIMIT
├─ gpu_count: 4
├─ gpu_type: a100
└─ memory: 64GB

VALIDATION: ❌ FAIL
ERROR: "Epochs must be between 1 and 1000. Got 5000."
POLICY: NOT REACHED (rejected at validation)
CLUSTER ASSIGNMENT: None
STATUS: Request rejected, not submitted
```

---

## Validation Rules Summary

### Training Jobs - All Must Pass:

```
CONSTRAINT                    RULE              EXAMPLE PASS        EXAMPLE FAIL
─────────────────────────────────────────────────────────────────────────────────
Epochs                        1-1000            ✅ 50 epochs        ❌ 5000 epochs
Batch Size                    1-10,000          ✅ 32               ❌ 50,000
GPU Count                     0-8               ✅ 2 GPUs           ❌ 16 GPUs
Memory GB                     4-256             ✅ 32GB             ❌ 1024GB
GPU Type (if used)            Approved list     ✅ v100             ❌ invalid_gpu
Task ID                       Must exist        ✅ train-001        ❌ (empty)
User ID                       Must exist        ✅ alice@...        ❌ (empty)
```

### Deployment Jobs - All Must Pass:

```
CONSTRAINT                    RULE              EXAMPLE PASS        EXAMPLE FAIL
─────────────────────────────────────────────────────────────────────────────────
Model Version                 X.Y.Z format      ✅ 1.5.0            ❌ latest, 1.2
Platform                      Approved list     ✅ kubernetes       ❌ unknown_platform
Replicas                      1-100             ✅ 3 replicas       ❌ 500 replicas
Task ID                       Must exist        ✅ deploy-001       ❌ (empty)
User ID                       Must exist        ✅ devops@...       ❌ (empty)
```

---

## REST API Endpoints

### 1. Submit Training Job

```
POST /train
Content-Type: application/json

Request:
{
  "task_id": "train-001",
  "user_id": "alice@company.com",
  "model_name": "ResNet50",
  "dataset": "MNIST",
  "epochs": 50,
  "batch_size": 32,
  "gpu_count": 2,
  "gpu_type": "v100",
  "memory_gb": 32,
  "priority": "high"
}

Response (200 OK):
{
  "success": true,
  "task_id": "train-001",
  "cluster": "training_cluster",
  "job_url": "https://training-cluster/jobs/...",
  "status": "submitted"
}
```

### 2. Submit Deployment

```
POST /deploy
Content-Type: application/json

Request:
{
  "task_id": "deploy-001",
  "user_id": "devops@company.com",
  "model_id": "ResNet50",
  "model_version": "1.5.0",
  "target_platform": "kubernetes",
  "replicas": 3,
  "cpu_limit": "4",
  "memory_limit": "4Gi"
}

Response (200 OK):
{
  "success": true,
  "task_id": "deploy-001",
  "cluster": "inference_cluster",
  "deployment_url": "https://inference-cluster/...",
  "status": "deployed",
  "endpoint": "http://resnet50-api.svc"
}
```

### 3. Check Job Status

```
GET /status/train-001

Response (running):
{
  "success": true,
  "task_id": "train-001",
  "status": "running",
  "progress": "35%",
  "current_epoch": "18/50",
  "eta": "10 hours"
}

Response (completed):
{
  "success": true,
  "task_id": "train-001",
  "status": "completed",
  "final_accuracy": 0.89,
  "checkpoint": "s3://models/..."
}
```

---

## Key Decision Points

### ❓ Question 1: Is this a valid training job?

**Decision Tree:**
```
Validate epochs [1-1000]?
├─ YES → Next check
└─ NO → REJECT

Validate batch_size [1-10,000]?
├─ YES → Next check
└─ NO → REJECT

Validate gpu_count [0-8]?
├─ YES → Next check
└─ NO → REJECT

Validate memory_gb [4-256]?
├─ YES → ACCEPT ✅
└─ NO → REJECT ❌
```

### ❓ Question 2: Which cluster should handle this?

**Decision Tree:**
```
Does the job need GPU? (gpu_count > 0)
├─ YES → Send to: training_cluster
│        (Optimized for GPU throughput)
│        (Expensive but fast)
│
└─ NO → Send to: inference_cluster
         (Optimized for cost)
         (Cheaper but sufficient for CPU)
```

### ❓ Question 3: Is the job complete?

**Status Lifecycle:**
```
submitted → running → completed
          → running → failed
          → running → cancelled
          → deployment (for deploy jobs)
```

---

## Data Flow Diagram: Complete Request

```
USER
 │
 ├─→ Creates Training Job
 │   │
 │   ├─ model_name: "ResNet50"
 │   ├─ epochs: 50
 │   ├─ gpu_count: 2
 │   └─ memory_gb: 32
 │
 ▼
API ENDPOINT: POST /train
 │
 ▼
REQUEST VALIDATOR
 │
 ├─ Check: epochs in [1-1000]? → ✅
 ├─ Check: batch_size in [1-10000]? → ✅
 ├─ Check: gpu_count in [0-8]? → ✅
 ├─ Check: memory_gb in [4-256]? → ✅
 │
 ▼ (If all pass)
CLEAN & SANITIZE DATA
 │
 ▼
POLICY ENGINE
 │
 ├─ Read: gpu_count = 2
 ├─ Decision: gpu_count > 0?
 │   └─ YES → training_cluster ← HIGH PRIORITY
 │
 ▼
DEPLOYMENT CONNECTOR
 │
 ├─ Generate job_id: "a7f3-2891"
 ├─ Submit config to training_cluster
 ├─ Allocate 2x V100 GPUs
 ├─ Allocate 32GB memory
 ├─ Record status: "submitted"
 │
 ▼
RETURN TO USER
 │
 ├─ HTTP 200 OK
 ├─ task_id: "train-001"
 ├─ cluster: "training_cluster"
 ├─ status: "submitted"
 │
 ▼
MONITORING & STATUS UPDATES
 │
 ├─ User calls: GET /status/train-001
 ├─ Returns: {status: "running", progress: "35%"}
 ├─ User calls again after 12 hours
 ├─ Returns: {status: "completed", accuracy: 0.89}
 │
 ▼
DONE ✅
```

---

## Summary

| Phase | Purpose | Example |
|-------|---------|---------|
| **Validation** | Verify input meets constraints | Reject epochs > 1000 |
| **Policy** | Decide where to route | GPU → training_cluster |
| **Submission** | Send job to cloud cluster | Deploy to Kubernetes |
| **Tracking** | Monitor progress & provide status | 35% complete |
| **Completion** | Job done, return results | Accuracy: 0.89 |

The policy engine orchestrates ML workloads across multiple cloud environments with intelligent routing, comprehensive validation, and full lifecycle management.
