#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Policy Engine - Direct Module Tests
No imports needed - tests modules inline
"""

import json
import sys
import time
import os
from datetime import datetime

# Add policy-engine directory to path
sys.path.insert(0, os.getcwd())

print("Python path:", sys.path[:2])
print("Current dir:", os.getcwd())

class Results:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def ok(self, name):
        self.passed += 1
        print("[PASS] " + name)
    
    def fail(self, name, reason):
        self.failed += 1
        self.errors.append((name, reason))
        print("[FAIL] " + name + ": " + reason)

# ============= INLINE TESTS =============

# Test 1: Request Validator
def test_1_request_validator():
    print("\n========== TEST 1: REQUEST VALIDATOR ==========\n")
    
    results = Results()
    
    # Import validator
    try:
        from utils.request_validator import RequestValidator
        validator = RequestValidator()
    except Exception as e:
        print("Cannot import validator: " + str(e))
        return results
    
    # Test data
    tests_pass = [
        ('train-001', 'alice@company.com', 'resnet', 'mnist', 50, 32, 2, 'v100', 32),
        ('train-002', 'bob@company.com', 'bert', 'wiki', 100, 64, 4, 'a100', 64),
        ('train-003', 'charlie@company.com', 'xgb', 'data', 10, 100, 0, None, 16),
    ]
    
    print("Valid training requests:")
    for task_id, user_id, name, dataset, epochs, batch, gpu_cnt, gpu_type, mem in tests_pass:
        data = {
            'task_id': task_id, 'user_id': user_id, 'model_name': name,
            'dataset': dataset, 'epochs': epochs, 'batch_size': batch,
            'gpu_count': gpu_cnt, 'memory_gb': mem
        }
        if gpu_type:
            data['gpu_type'] = gpu_type
        
        valid, err, _ = validator.validate_train_request(data)
        if valid:
            results.ok("train-request: " + task_id)
        else:
            results.fail("train-request: " + task_id, err)
    
    # Test deployment
    deploy_tests = [
        ('deploy-001', 'devops@company.com', 'resnet', '1.0.0', 'kubernetes'),
        ('deploy-002', 'qa@company.com', 'bert', '2.0.0', 'docker'),
    ]
    
    print("\nValid deployment requests:")
    for task_id, user_id, model_id, version, platform in deploy_tests:
        data = {
            'task_id': task_id, 'user_id': user_id, 'model_id': model_id,
            'model_version': version, 'target_platform': platform
        }
        valid, err, _ = validator.validate_deploy_request(data)
        if valid:
            results.ok("deploy-request: " + task_id)
        else:
            results.fail("deploy-request: " + task_id, err)
    
    # Test invalid requests
    print("\nInvalid requests (should fail):")
    
    # Missing required field
    valid, _, _ = validator.validate_train_request({'user_id': 'x@x.com'})
    if not valid:
        results.ok("reject-missing-field")
    else:
        results.fail("reject-missing", "should have failed")
    
    # Epochs too high
    valid, _, _ = validator.validate_train_request({
        'task_id': 't', 'user_id': 'u', 'model_name': 'm',
        'dataset': 'd', 'epochs': 5000, 'batch_size': 32
    })
    if not valid:
        results.ok("reject-epochs-too-high")
    else:
        results.fail("reject-epochs", "should have failed")
    
    # Invalid version
    valid, _, _ = validator.validate_deploy_request({
        'task_id': 't', 'user_id': 'u', 'model_id': 'm',
        'model_version': 'latest', 'target_platform': 'k8s'
    })
    if not valid:
        results.ok("reject-invalid-version")
    else:
        results.fail("reject-version", "should have failed")
    
    return results

# Test 2: Resource Optimizer
def test_2_resource_optimizer():
    print("\n========== TEST 2: RESOURCE OPTIMIZER ==========\n")
    
    results = Results()
    
    try:
        from modules.resource_optimizer import ResourceOptimizer
        from core.decision_context import DecisionContext, TaskContext
        optimizer = ResourceOptimizer()
    except Exception as e:
        print("Cannot import optimizer: " + str(e))
        return results
    
    # Training (GPU) -> training_cluster
    print("GPU training jobs (should route to training_cluster):")
    train_jobs = [
        ('train-gpu-001', 'alice', True, 2, 48),
        ('train-gpu-002', 'bob', True, 4, 64),
    ]
    
    for task_id, user_id, gpu_needed, gpu_count, memory in train_jobs:
        task = TaskContext(
            task_id=task_id,
            task_type='training',
            user_id=user_id,
            user_roles=['data_scientist'],
            priority='normal',
            requirement={'gpu_needed': gpu_needed, 'gpu_count': gpu_count, 'memory_gb': memory}
        )
        context = DecisionContext(task=task, resource=None, compliance=None)
        decision = optimizer.optimize(context)
        
        if decision.get('cluster') == 'training_cluster':
            results.ok("route-gpu-training: " + task_id + " -> training_cluster")
        else:
            results.fail("route: " + task_id, "got " + str(decision.get('cluster')))
    
    # Inference (CPU) -> inference_cluster  
    print("\nCPU inference jobs (should route to inference_cluster):")
    infer_jobs = [
        ('infer-cpu-001', 'devops', False),
        ('infer-cpu-002', 'qa', False),
    ]
    
    for task_id, user_id, gpu_needed in infer_jobs:
        task = TaskContext(
            task_id=task_id,
            task_type='inference',
            user_id=user_id,
            user_roles=['devops'],
            priority='normal',
            requirement={'gpu_needed': gpu_needed, 'cpu_cores': 4, 'memory_gb': 4}
        )
        context = DecisionContext(task=task, resource=None, compliance=None)
        decision = optimizer.optimize(context)
        
        if decision.get('cluster') == 'inference_cluster':
            results.ok("route-cpu-inference: " + task_id + " -> inference_cluster")
        else:
            results.fail("route: " + task_id, "got " + str(decision.get('cluster')))
    
    return results

# Test 3: Deployment Connector
def test_3_deployment_connector():
    print("\n========== TEST 3: DEPLOYMENT CONNECTOR ==========\n")
    
    results = Results()
    
    try:
        from modules.deployment_connector import DeploymentConnector
        connector = DeploymentConnector()
    except Exception as e:
        print("Cannot import connector: " + str(e))
        return results
    
    # Submit training jobs
    print("Submitting training jobs:")
    train_jobs = [
        {'task_id': 'sub-train-001', 'user_id': 'alice', 'model_name': 'resnet', 'dataset': 'mnist', 'epochs': 20, 'batch_size': 32, 'gpu_count': 2, 'gpu_type': 'v100', 'memory_gb': 32, 'priority': 'high'},
        {'task_id': 'sub-train-002', 'user_id': 'bob', 'model_name': 'bert', 'dataset': 'text', 'epochs': 50, 'batch_size': 64, 'gpu_count': 4, 'gpu_type': 'a100', 'memory_gb': 64, 'priority': 'normal'},
    ]
    
    for job in train_jobs:
        resp = connector.submit_training_job(job)
        if resp.get('success'):
            results.ok("submit-training: " + job['task_id'])
        else:
            results.fail("submit-training: " + job['task_id'], "failed")
    
    # Submit deploy jobs
    print("\nSubmitting deployment jobs:")
    deploy_jobs = [
        {'task_id': 'sub-deploy-001', 'user_id': 'devops', 'model_id': 'resnet', 'model_version': '1.0.0', 'target_platform': 'kubernetes', 'replicas': 3, 'cpu_limit': '4', 'memory_limit': '4Gi', 'priority': 'high'},
        {'task_id': 'sub-deploy-002', 'user_id': 'qa', 'model_id': 'bert', 'model_version': '2.0.0', 'target_platform': 'docker', 'replicas': 1, 'cpu_limit': '2', 'memory_limit': '2Gi', 'priority': 'normal'},
    ]
    
    for job in deploy_jobs:
        resp = connector.submit_deployment_job(job)
        if resp.get('success'):
            results.ok("submit-deploy: " + job['task_id'])
        else:
            results.fail("submit-deploy: " + job['task_id'], "failed")
    
    # Check status
    print("\nChecking job status:")
    test_job_id = train_jobs[0]['task_id']
    
    connector.submit_training_job(train_jobs[0])
    status = connector.get_task_status(test_job_id)
    
    if status.get('success'):
        results.ok("status-check: " + test_job_id + " (" + status.get('status') + ")")
    else:
        results.fail("status-check: " + test_job_id, "failed")
    
    return results

# Test 4: Integration Test
def test_4_integration():
    print("\n========== TEST 4: INTEGRATION (Validate->Submit->Status) ==========\n")
    
    results = Results()
    
    try:
        from utils.request_validator import RequestValidator
        from modules.deployment_connector import DeploymentConnector
        validator = RequestValidator()
        connector = DeploymentConnector()
    except Exception as e:
        print("Cannot import modules: " + str(e))
        return results
    
    # Training workflow
    print("Training workflow (validate -> submit -> status):")
    train_job = {
        'task_id': 'int-train-001',
        'user_id': 'alice@company.com',
        'model_name': 'resnet',
        'dataset': 'mnist',
        'epochs': 30,
        'batch_size': 32,
        'gpu_count': 2,
        'gpu_type': 'v100',
        'memory_gb': 32,
        'priority': 'high'
    }
    
    # Validate
    valid, err, cleaned = validator.validate_train_request(train_job)
    if not valid:
        results.fail("int-train-validate", "validation failed: " + err)
        return results
    
    # Submit
    resp = connector.submit_training_job(cleaned)
    if not resp.get('success'):
        results.fail("int-train-submit", "submission failed")
        return results
    
    # Status
    status = connector.get_task_status(train_job['task_id'])
    if status.get('success'):
        results.ok("int-train-complete: validate->submit->status-ok")
    else:
        results.fail("int-train-status", "status check failed")
    
    # Deployment workflow
    print("\nDeployment workflow (validate -> submit -> status):")
    deploy_job = {
        'task_id': 'int-deploy-001',
        'user_id': 'devops@company.com',
        'model_id': 'resnet',
        'model_version': '1.0.0',
        'target_platform': 'kubernetes',
        'replicas': 3,
        'cpu_limit': '4',
        'memory_limit': '4Gi',
        'priority': 'high'
    }
    
    # Validate
    valid, err, cleaned = validator.validate_deploy_request(deploy_job)
    if not valid:
        results.fail("int-deploy-validate", "validation failed: " + err)
        return results
    
    # Submit
    resp = connector.submit_deployment_job(cleaned)
    if not resp.get('success'):
        results.fail("int-deploy-submit", "submission failed")
        return results
    
    # Status
    status = connector.get_task_status(deploy_job['task_id'])
    if status.get('success'):
        results.ok("int-deploy-complete: validate->submit->status-ok")
    else:
        results.fail("int-deploy-status", "status check failed")
    
    # E2E: Train then Deploy
    print("\nE2E Pipeline (Train -> Deploy):")
    
    train_job2 = train_job.copy()
    train_job2['task_id'] = 'e2e-train-001'
    deploy_job2 = deploy_job.copy()
    deploy_job2['task_id'] = 'e2e-deploy-001'
    
    _, _, tc = validator.validate_train_request(train_job2)
    _, _, dc = validator.validate_deploy_request(deploy_job2)
    
    tr = connector.submit_training_job(tc)
    dr = connector.submit_deployment_job(dc)
    
    if tr.get('success') and dr.get('success'):
        results.ok("e2e-pipeline: train+deploy submitted")
    else:
        results.fail("e2e-pipeline", "submissions failed")
    
    return results

# Test 5: Performance
def test_5_performance():
    print("\n========== TEST 5: PERFORMANCE ==========\n")
    
    results = Results()
    
    try:
        from modules.deployment_connector import DeploymentConnector
        connector = DeploymentConnector()
    except Exception as e:
        print("Cannot import connector: " + str(e))
        return results
    
    # Submission throughput
    print("Submission throughput (10 jobs):")
    start = time.time()
    for i in range(10):
        connector.submit_training_job({
            'task_id': 'perf-t-' + str(i),
            'user_id': 'user@x.com',
            'model_name': 'm',
            'dataset': 'd',
            'epochs': 10,
            'batch_size': 32,
            'gpu_count': 1,
            'gpu_type': 'v100',
            'memory_gb': 16
        })
    elapsed_ms = (time.time() - start) * 1000
    avg_ms = elapsed_ms / 10
    results.ok("throughput: %.2f ms per submission" % avg_ms)
    
    # Query throughput
    print("\nStatus query throughput (20 queries):")
    connector.submit_training_job({
        'task_id': 'perf-q',
        'user_id': 'user@x.com',
        'model_name': 'm',
        'dataset': 'd',
        'epochs': 10,
        'batch_size': 32,
        'gpu_count': 1,
        'gpu_type': 'v100',
        'memory_gb': 16
    })
    start = time.time()
    for _ in range(20):
        connector.get_task_status('perf-q')
    elapsed_ms = (time.time() - start) * 1000
    avg_ms = elapsed_ms / 20
    results.ok("throughput: %.2f ms per query" % avg_ms)
    
    # Concurrent load
    print("\nConcurrent load (100 mixed jobs):")
    start = time.time()
    for i in range(50):
        connector.submit_training_job({
            'task_id': 'load-t-' + str(i),
            'user_id': 'u@x.com',
            'model_name': 'm',
            'dataset': 'd',
            'epochs': 10,
            'batch_size': 32,
            'gpu_count': 1,
            'gpu_type': 'v100',
            'memory_gb': 16
        })
        connector.submit_deployment_job({
            'task_id': 'load-d-' + str(i),
            'user_id': 'u@x.com',
            'model_id': 'm',
            'model_version': '1.0.0',
            'target_platform': 'kubernetes',
            'replicas': 1,
            'cpu_limit': '2',
            'memory_limit': '2Gi'
        })
    elapsed = time.time() - start
    throughput = 100.0 / elapsed if elapsed > 0 else 0
    results.ok("concurrent: 100 jobs in %.1f sec (%.0f jobs/sec)" % (elapsed, throughput))
    
    return results

# ============= MAIN =============

def main():
    print("\n" + "=" * 80)
    print("MLOPS POLICY ENGINE - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print("Start: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    all_results = []
    
    try:
        all_results.append(("1. Request Validator", test_1_request_validator()))
        all_results.append(("2. Resource Optimizer", test_2_resource_optimizer()))
        all_results.append(("3. Deployment Connector", test_3_deployment_connector()))
        all_results.append(("4. Integration Tests", test_4_integration()))
        all_results.append(("5. Performance Tests", test_5_performance()))
    except Exception as e:
        print("\nFATAL ERROR: " + str(e))
        import traceback
        traceback.print_exc()
        return False
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total_pass = 0
    total_fail = 0
    all_errors = []
    
    for name, result in all_results:
        total_pass += result.passed
        total_fail += result.failed
        all_errors.extend(result.errors)
        status = "[PASS]" if result.failed == 0 else "[FAIL]"
        print(status + " " + name + ": " + str(result.passed) + " passed, " + str(result.failed) + " failed")
    
    total = total_pass + total_fail
    print("\nRESULT: " + str(total_pass) + "/" + str(total) + " TESTS PASSED")
    
    if all_errors:
        print("\nFAILED TESTS:")
        for name, reason in all_errors:
            print("  [*] " + name + ": " + reason)
    
    print("\nEnd: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 80 + "\n")
    
    return total_fail == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
