"""
Quick Start Guide for Policy Engine API

This script demonstrates how to quickly get the Policy Engine API running
and test the main endpoints: /train, /deploy, and /status
"""

# ============================================================================
# QUICK START - 3 STEPS
# ============================================================================

"""
STEP 1: Install Dependencies
==============================
pip install -r requirements.txt

STEP 2: Start the API Server
=============================
python -m policy_engine.api.rest_api

You should see:
  * Running on http://0.0.0.0:5000 (Press CTRL+C to quit)

STEP 3: Test the Endpoints
============================
Run the examples below in your terminal or Python shell.
"""

# ============================================================================
# BASH EXAMPLES (Use in Terminal)
# ============================================================================

"""
1. HEALTH CHECK
===============
curl -X GET http://localhost:5000/health

Expected Response:
{
    "status": "healthy",
    "service": "MLOps Policy Engine"
}
"""


"""
2. SUBMIT TRAINING JOB
======================
curl -X POST http://localhost:5000/train \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "train-quickstart-001",
    "user_id": "user@company.com",
    "model_name": "my_first_model",
    "dataset": "sample_data",
    "epochs": 10,
    "batch_size": 32,
    "gpu_count": 1,
    "gpu_type": "v100",
    "memory_gb": 16,
    "priority": "normal"
  }'

Expected Response:
{
    "success": true,
    "task_id": "train-quickstart-001",
    "message": "Training job submitted successfully",
    "deployment": {
        "task_id": "train-quickstart-001",
        "cluster": "training_cluster",
        "status": "pending"
    }
}
"""


"""
3. CHECK JOB STATUS
===================
curl -X GET http://localhost:5000/status/train-quickstart-001

Expected Response:
{
    "success": true,
    "task_id": "train-quickstart-001",
    "status": "running",
    "cluster": "training_cluster",
    "progress": 50
}
"""


"""
4. SUBMIT DEPLOYMENT
====================
curl -X POST http://localhost:5000/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "deploy-quickstart-001",
    "user_id": "devops@company.com",
    "model_id": "my_first_model",
    "model_version": "1.0.0",
    "target_platform": "kubernetes",
    "replicas": 2,
    "priority": "normal"
  }'

Expected Response:
{
    "success": true,
    "task_id": "deploy-quickstart-001",
    "message": "Deployment submitted successfully",
    "deployment": {
        "task_id": "deploy-quickstart-001",
        "cluster": "inference_cluster",
        "status": "pending"
    }
}
"""


"""
5. CHECK DEPLOYMENT STATUS
===========================
curl -X GET http://localhost:5000/status/deploy-quickstart-001

Expected Response:
{
    "success": true,
    "task_id": "deploy-quickstart-001",
    "status": "running",
    "cluster": "inference_cluster",
    "progress": 50
}
"""


# ============================================================================
# PYTHON EXAMPLES (Use in Python Script or REPL)
# ============================================================================

import requests
import json

BASE_URL = "http://localhost:5000"

def health_check():
    """Check if API is healthy."""
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:", response.json())
    return response.status_code == 200


def submit_training_job():
    """Submit a training job."""
    training_request = {
        "task_id": "train-python-001",
        "user_id": "data_scientist@company.com",
        "model_name": "bert_classifier",
        "dataset": "mnist",
        "epochs": 20,
        "batch_size": 64,
        "gpu_count": 2,
        "gpu_type": "a100",
        "memory_gb": 32,
        "priority": "high",
        "budget_limit": 500
    }
    
    response = requests.post(f"{BASE_URL}/train", json=training_request)
    result = response.json()
    print("\nTraining Job Submitted:")
    print(json.dumps(result, indent=2))
    
    return result.get('task_id') if result.get('success') else None


def submit_deployment(model_id="bert_classifier"):
    """Submit a model deployment."""
    deployment_request = {
        "task_id": "deploy-python-001",
        "user_id": "devops@company.com",
        "model_id": model_id,
        "model_version": "1.0.0",
        "target_platform": "kubernetes",
        "replicas": 3,
        "max_replicas": 10,
        "cpu_limit": "4",
        "memory_limit": "4Gi",
        "priority": "normal"
    }
    
    response = requests.post(f"{BASE_URL}/deploy", json=deployment_request)
    result = response.json()
    print("\nDeployment Submitted:")
    print(json.dumps(result, indent=2))
    
    return result.get('task_id') if result.get('success') else None


def check_status(task_id):
    """Check the status of a task."""
    response = requests.get(f"{BASE_URL}/status/{task_id}")
    result = response.json()
    print(f"\nStatus for {task_id}:")
    print(json.dumps(result, indent=2))
    return result


def run_complete_workflow():
    """Run complete training + deployment workflow."""
    
    print("\n" + "="*80)
    print("COMPLETE WORKFLOW: Training + Deployment")
    print("="*80)
    
    # 1. Health check
    print("\n1. Health Check...")
    if not health_check():
        print("❌ API is not healthy. Make sure it's running on port 5000")
        return False
    
    # 2. Submit training job
    print("\n2. Submitting Training Job...")
    train_task_id = submit_training_job()
    if not train_task_id:
        print("❌ Failed to submit training job")
        return False
    
    # 3. Check training status
    print("\n3. Checking Training Status...")
    check_status(train_task_id)
    
    # 4. Submit deployment
    print("\n4. Submitting Deployment...")
    deploy_task_id = submit_deployment()
    if not deploy_task_id:
        print("❌ Failed to submit deployment")
        return False
    
    # 5. Check deployment status
    print("\n5. Checking Deployment Status...")
    check_status(deploy_task_id)
    
    print("\n" + "="*80)
    print("✅ Complete workflow executed successfully!")
    print("="*80)
    
    return True


# ============================================================================
# VALIDATION TESTING
# ============================================================================

def test_input_validation():
    """Test input validation."""
    print("\n" + "="*80)
    print("VALIDATION TESTING")
    print("="*80)
    
    # Test 1: Missing required field
    print("\nTest 1: Missing required field (task_id)")
    bad_request = {
        "user_id": "user@company.com",
        "model_name": "model",
        "epochs": 10,
        "batch_size": 32
    }
    response = requests.post(f"{BASE_URL}/train", json=bad_request)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: Invalid epochs (too high)
    print("\nTest 2: Invalid epochs (> 1000)")
    bad_request = {
        "task_id": "train-test",
        "user_id": "user@company.com",
        "model_name": "model",
        "dataset": "data",
        "epochs": 5000,
        "batch_size": 32
    }
    response = requests.post(f"{BASE_URL}/train", json=bad_request)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 3: Invalid model version (not semantic)
    print("\nTest 3: Invalid model version (not semantic)")
    bad_request = {
        "task_id": "deploy-test",
        "user_id": "devops@company.com",
        "model_id": "model",
        "model_version": "latest",
        "target_platform": "kubernetes"
    }
    response = requests.post(f"{BASE_URL}/deploy", json=bad_request)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 4: Non-existent task status
    print("\nTest 4: Non-existent task status")
    response = requests.get(f"{BASE_URL}/status/nonexistent-task-12345")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")


# ============================================================================
# CLUSTERING DEMONSTRATION
# ============================================================================

def demo_gpu_to_training_cluster():
    """Demonstrate GPU job routing to training cluster."""
    print("\n" + "="*80)
    print("GPU JOB → TRAINING CLUSTER")
    print("="*80)
    
    training_request = {
        "task_id": "demo-gpu-training-001",
        "user_id": "ml_engineer@company.com",
        "model_name": "deep_learning_model",
        "dataset": "large_dataset",
        "epochs": 50,
        "batch_size": 128,
        "gpu_count": 4,
        "gpu_type": "h100",
        "memory_gb": 80,
        "priority": "high"
    }
    
    print("\nRequest:")
    print(json.dumps(training_request, indent=2))
    
    response = requests.post(f"{BASE_URL}/train", json=training_request)
    result = response.json()
    
    print("\nResponse:")
    print(json.dumps(result, indent=2))
    
    if result.get('success'):
        cluster = result.get('policy_decision', {}).get('cluster')
        print(f"\n✅ Job routed to: {cluster}")
        if cluster == 'training_cluster':
            print("✅ GPU jobs correctly routed to TRAINING_CLUSTER!")
    else:
        print(f"\n❌ Error: {result.get('error')}")


def demo_cpu_to_inference_cluster():
    """Demonstrate CPU/inference routing to inference cluster."""
    print("\n" + "="*80)
    print("CPU/INFERENCE JOB → INFERENCE CLUSTER")
    print("="*80)
    
    deployment_request = {
        "task_id": "demo-cpu-inference-001",
        "user_id": "ml_ops@company.com",
        "model_id": "inference_model",
        "model_version": "2.5.1",
        "target_platform": "kubernetes",
        "replicas": 5,
        "cpu_limit": "8",
        "memory_limit": "8Gi",
        "priority": "normal"
    }
    
    print("\nRequest:")
    print(json.dumps(deployment_request, indent=2))
    
    response = requests.post(f"{BASE_URL}/deploy", json=deployment_request)
    result = response.json()
    
    print("\nResponse:")
    print(json.dumps(result, indent=2))
    
    if result.get('success'):
        cluster = result.get('policy_decision', {}).get('cluster')
        print(f"\n✅ Job routed to: {cluster}")
        if cluster == 'inference_cluster':
            print("✅ Inference jobs correctly routed to INFERENCE_CLUSTER!")
    else:
        print(f"\n❌ Error: {result.get('error')}")


# ============================================================================
# MAIN - Run all examples
# ============================================================================

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║       POLICY ENGINE API - QUICK START EXAMPLES                 ║
    ║                                                                 ║
    ║  Make sure the API is running:                                 ║
    ║    python -m policy_engine.api.rest_api                        ║
    ║                                                                 ║
    ║  Then run this script:                                         ║
    ║    python QUICK_START.py                                       ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Run all demos
        run_complete_workflow()
        test_input_validation()
        demo_gpu_to_training_cluster()
        demo_cpu_to_inference_cluster()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*80)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print("Make sure the API is running:")
        print("  python -m policy_engine.api.rest_api")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
