# MLOps Policy Engine - Quick Start Guide

## What You've Built

A **production-ready Multi-Cloud Policy Engine** that makes intelligent decisions about ML workloads across AWS, GCP, and Azure. It's like an "operating manual" for your entire cloud infrastructure.

## The 4 Core Decision Areas

### 1. 🔧 Resource Optimization
**Question: What hardware?**
- Routes GPU jobs vs CPU jobs
- Allocates memory dynamically
- Recommends instance types

**Example:**
```
Task: Training with GPU
Decision: Allocate 2x A100 GPUs, 48GB RAM, AWS p4d instance
```

### 2. 💰 Cost Management
**Question: How much will it cost?**
- Compares cloud providers (AWS vs GCP vs Azure)
- Recommends spot instances for low-priority tasks
- Enforces budget limits
- Shows potential savings

**Example:**
```
Task: Batch processing (low priority)
Decision: GCP preemptible VM, $0.74/hr (saves $1.74/hr vs on-demand)
```

### 3. 🔐 Compliance & Security
**Question: Where can the data go?**
- Enforces GDPR data residency (EU only)
- Validates HIPAA requirements
- Ensures encryption and audit logging
- Checks user access control

**Example:**
```
Task: Processing EU customer data
Decision: Enforce eu-west-1 region, require encryption, audit logging
Reason: GDPR compliance requirement
```

### 4. ⏰ Scheduling & Prioritization
**Question: When should it run?**
- Critical tasks: Run immediately (5 minutes)
- High priority: Within 1 hour
- Medium: Run during off-peak hours (2-4 hour delay)
- Low: Overnight batch processing (save 30%+ on costs)

**Example:**
```
Low priority batch job scheduled for 2:00 AM
Reason: 70% cheaper during off-peak hours
```

## Getting Started (5 Minutes)

### Installation

```bash
cd policy-engine
pip install -r requirements.txt
```

### Quick Test

```python
from policy_engine import MLOpsPolicyEngine

engine = MLOpsPolicyEngine()

# Evaluate a GPU training job
decision = engine.evaluate_task(
    task_id="train-001",
    task_type="training",
    user_id="scientist@company.com",
    user_roles=["ml_engineer"],
    priority="high",
    requirement={'gpu_needed': True, 'gpu_count': 2, 'memory_gb': 48},
    budget_limit=100.0,
    preferred_regions=['us-east-1']
)

print(f"✓ Status: {decision['status']}")
print(f"✓ Provider: {decision['suggested_action'].get('recommended_provider')}")
print(f"✓ GPU Type: {decision['suggested_action'].get('gpu_type')}")
print(f"✓ Cost: ${decision['suggested_action'].get('estimated_cost_usd'):.2f}/hour")
```

### Run Examples

```bash
python examples.py
```

Shows 6 real-world examples:
1. GPU training optimization
2. CPU inference with cost savings
3. GDPR-compliant batch processing
4. Critical priority execution
5. Multi-cloud selection
6. Engine metrics

## Using the REST API

### Start Server

```bash
python -m policy_engine.api.rest_api
# API runs on http://localhost:5000
```

### Test Endpoints

```bash
# Evaluate a task
curl -X POST http://localhost:5000/api/v1/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "train-001",
    "task_type": "training",
    "user_id": "user1",
    "user_roles": ["ml_engineer"],
    "priority": "high",
    "requirement": {"gpu_needed": true, "gpu_count": 2, "memory_gb": 48},
    "budget_limit": 100.0
  }'

# Get all policies
curl http://localhost:5000/api/v1/policies

# Get metrics
curl http://localhost:5000/api/v1/metrics
```

## Using the CLI

```bash
# Evaluate a training task
policy-engine evaluate \
  --task-id train-001 \
  --task-type training \
  --user-id scientist@company.com \
  --priority high \
  --gpu-count 2 \
  --memory-gb 48 \
  --budget 100.0

# List all policies
policy-engine list-policies

# Show policy details
policy-engine show-policy --policy-name resource_optimization_policy

# View metrics
policy-engine metrics

# Start REST API server
policy-engine serve --port 5000
```

## Key Scenarios

### Scenario 1: Cost-Conscious Org
```python
# User wants cheapest option
decision = engine.evaluate_task(
    task_id="batch-job",
    task_type="batch_processing",
    priority="low",  # Use spot instances
    budget_limit=50.0,
    preferred_regions=['us-east-1', 'us-west-2'],
)
# Result: GCP preemptible VM in cheapest region, estimated $0.74/hr
```

### Scenario 2: Regulated Industry (Healthcare)
```python
# Must comply with HIPAA
decision = engine.evaluate_task(
    task_id="patient-analysis",
    task_type="training",
    priority="medium",
    required_compliance=['HIPAA'],  # Enforce HIPAA
    preferred_regions=['us-east-1'],
    security_requirements=['encrypted', 'audit_logging'],
)
# Result: AWS us-east-1 (HIPAA-compliant region), encryption enforced
```

### Scenario 3: European Company (GDPR)
```python
# All EU data must stay in Europe
decision = engine.evaluate_task(
    task_id="eu-data-processing",
    task_type="batch_processing",
    required_compliance=['GDPR'],
    preferred_regions=['eu-west-1', 'eu-central-1'],  # EU only
)
# Result: Forces EU-only region selection despite cost
```

### Scenario 4: Urgent Real-Time Task
```python
# Critical production inference - no waiting
decision = engine.evaluate_task(
    task_id="realtime-pred",
    task_type="inference",
    priority="critical",  # Immediate execution
)
# Result: Earliest available resource, time ~5 minutes, cost not considered
```

## Architecture at a Glance

```
Your ML Task Request
        ↓
┌───────────────────────────┐
│  Policy Engine Core        │  Parses policies, evaluates conditions
│  - Parse policies          │
│  - Evaluate rules          │
└───────────┬───────────────┘
            ↓
┌─────────────────────────────────────────────────────────┐
│  4 Specialized Decision Modules                         │
├──────────────────┬──────────┬──────────┬────────────────┤
│ 1. Resource      │ 2. Cost  │ 3. Comp  │ 4. Schedule    │
│    Optimizer     │  Manager │  Enforcer│               │
├──────────────────┼──────────┼──────────┼────────────────┤
│ GPU? CPU? RAM?   │ Which    │ GDPR?    │ When to run?   │
│                  │ provider?│ HIPAA?   │ Priority Q?    │
└──────────────────┴──────────┴──────────┴────────────────┘
            ↓
    Policy Decision ✓
    ├─ Status: ALLOWED
    ├─ Provider: AWS
    ├─ Region: us-east-1
    ├─ GPU: 2x A100
    ├─ Cost: $3.06/hr
    └─ Schedule: Immediate
```

## Decision Output Example

```json
{
  "decision_id": "dec-12345",
  "task_id": "train-001",
  "status": "allowed",
  "suggested_action": {
    "compute_type": "gpu",
    "gpu_type": "a100",
    "gpu_count": 2,
    "cpu_cores": 8,
    "memory_gb": 48,
    "estimated_throughput": 200,
    "recommended_provider": "aws",
    "recommended_region": "us-east-1",
    "use_spot_instance": false,
    "estimated_cost_usd": 3.06,
    "scheduled_start_time": "2024-01-20T14:30:00",
    "queue_position": 1
  },
  "applied_policies": [
    "resource_optimization_policy",
    "cost_optimization_policy",
    "compliance_policy"
  ]
}
```

## Next Steps

1. **Integrate with Your ML Platform**
   - Use REST API to hook into Kubeflow, MLflow, or Airflow
   - Replace manual resource provisioning decisions

2. **Customize Policies**
   - Modify `config/default_policies.py` for your org
   - Add compliance frameworks you need
   - Define your pricing model

3. **Monitor Decisions**
   - Use metrics endpoint to track all decisions
   - Identify optimization opportunities
   - Measure cost savings

4. **Scale to Production**
   - Run as Kubernetes service
   - Add real pricing APIs from cloud providers
   - Integrate with cost tracking systems

## Troubleshooting

**Q: All my tasks are being DENIED**
A: Check compliance requirements. You may have strict GDPR/HIPAA constraints conflicting with available regions.

**Q: Why is my critical task not immediate?**
A: Check priority level. Use `priority="critical"` for immediate execution. Other priorities have delays.

**Q: How do I change cost optimization behavior?**
A: Edit `CostManager.optimize()` method or modify cost policies in `default_policies.py`

**Q: How do I add a new compliance framework?**
A: Add to `compliance_enforcer.py` - define allowed regions and required settings

## Advanced Configuration

### Custom Cloud Pricing

Edit `cost_manager.py`:

```python
CloudPricing(
    provider=CloudProvider.AWS,
    region='us-east-1',
    on_demand_hourly_rate=3.06,  # Your actual price
    spot_hourly_rate=0.92,
    spot_availability=0.95
)
```

### Custom Compliance Rules

Edit `compliance_enforcer.py`:

```python
self.compliance_rules['my_framework'] = {
    'encryption_required': True,
    'audit_logging_required': True,
    'data_residency_required': True,
}
```

### Custom Resource Profiles

Edit `resource_optimizer.py`:

```python
'my_custom_task': {
    'prefers_gpu': True,
    'min_memory_gb': 64,
    'recommended_gpu_count': 4,
    'gpu_preference': ['a100', 'h100'],
}
```

## Metrics & Analytics

```python
# Get engine metrics
metrics = engine.get_metrics()

print(f"Total decisions: {metrics['total_decisions']}")
print(f"Avg execution time: {metrics['avg_execution_time_ms']}ms")
print(f"Decision breakdown by status: {metrics['status_counters']}")
print(f"Most used policies: {metrics['policy_counters']}")
```

## File Structure

```
policy-engine/
├── README.md                    # This guide
├── examples.py                  # 6 runnable examples
├── requirements.txt             # Dependencies
├── setup.py                     # Installation config
│
├── core/
│   ├── policy_engine.py         # Main decision engine
│   ├── policy_parser.py         # Parse policies (YAML/JSON)
│   └── decision_context.py      # Context models
│
├── modules/
│   ├── resource_optimizer.py    # GPU/CPU/RAM decisions
│   ├── cost_manager.py          # Multi-cloud cost optimization
│   ├── compliance_enforcer.py   # GDPR/HIPAA/PCI-DSS
│   └── scheduler.py             # Priority & timing
│
├── api/
│   ├── rest_api.py              # Flask REST API
│   └── cli.py                   # Command-line interface
│
├── config/
│   ├── default_policies.py      # Built-in policies
│   └── config_loader.py         # Load YAML/JSON configs
│
└── utils/
    ├── logger.py                # Logging
    ├── metrics.py               # Decision tracking
    └── validators.py            # Input validation
```

---

**You now have a production-ready MLOps Policy Engine!** 🎉

For detailed documentation, see [README.md](README.md)
