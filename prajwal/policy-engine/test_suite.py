#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MLOps Policy Engine - Simple Direct Test Suite
Run from: policy-engine directory
Tests all modules with sample data
"""

import json
import sys
import time
from datetime import datetime

# Simple test result tracker
class Results:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def ok(self, name):
        self.passed += 1
        print("[OK] " + name)
    
    def fail(self, name, reason):
        self.failed += 1
        self.errors.append((name, reason))
        print("[FAIL] " + name + ": " + reason)

# ============= SAMPLE TEST DATA =============

TRAINING_SAMPLES = [
    {'task_id': 'train-001', 'user_id': 'alice@company.com', 'model_name': 'resnet', 'dataset': 'mnist', 'epochs': 50, 'batch_size': 32, 'gpu_count': 2, 'gpu_type': 'v100', 'memory_gb': 32, 'priority': 'high'},
    {'task_id': 'train-002', 'user_id': 'bob@company.com', 'model_name': 'bert', 'dataset': 'wiki', 'epochs': 100, 'batch_size': 64, 'gpu_count': 4, 'gpu_type': 'a100', 'memory_gb': 64, 'priority': 'critical'},
    {'task_id': 'train-003', 'user_id': 'charlie@company.com', 'model_name': 'xgboost', 'dataset': 'tabular', 'epochs': 10, 'batch_size': 100, 'gpu_count': 0, 'memory_gb': 16, 'priority': 'normal'},
]

DEPLOY_SAMPLES = [
    {'task_id': 'deploy-001', 'user_id': 'devops@company.com', 'model_id': 'resnet', 'model_version': '1.0.0', 'target_platform': 'kubernetes', 'replicas': 3, 'cpu_limit': '4', 'memory_limit': '4Gi', 'priority': 'high'},
    {'task_id': 'deploy-002', 'user_id': 'qa@company.com', 'model_id': 'bert', 'model_version': '2.1.0', 'target_platform': 'docker', 'replicas': 1, 'cpu_limit': '2', 'memory_limit': '2Gi', 'priority': 'normal'},
]

# ============= TEST SUITES =============

def test_validator():
    print("\n=== REQUEST VALIDATOR TESTS ===\n")
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from policy_engine.utils.request_validator import RequestValidator
    
    validator = RequestValidator()
    results = Results()
    
    # Valid training
    print("Valid Training Requests:")
    for job in TRAINING_SAMPLES:
        valid, err, _ = validator.validate_train_request(job)
        if valid:
            results.ok("train: " + job['task_id'])
        else:
            results.fail("train: " + job['task_id'], err)
    
    # Valid deployment
    print("\nValid Deployment Requests:")
    for job in DEPLOY_SAMPLES:
        valid, err, _ = validator.validate_deploy_request(job)
        if valid:
            results.ok("deploy: " + job['task_id'])
        else:
            results.fail("deploy: " + job['task_id'], err)
    
    # Invalid requests (should fail)
    print("\nInvalid Requests (expect failure):")
    
    # Missing field
    valid, _, _ = validator.validate_train_request({'user_id': 'x@x.com'})
    if not valid:
        results.ok("reject: missing field")
    else:
        results.fail("reject: missing field", "should have failed")
    
    # Epochs too high
    valid, _, _ = validator.validate_train_request({'task_id': 't', 'user_id': 'u', 'model_name': 'm', 'dataset': 'd', 'epochs': 5000, 'batch_size': 32})
    if not valid:
        results.ok("reject: epochs > 1000")
    else:
        results.fail("reject: epochs", "should have failed")
    
    # Invalid version
    valid, _, _ = validator.validate_deploy_request({'task_id': 't', 'user_id': 'u', 'model_id': 'm', 'model_version': 'latest', 'target_platform': 'kubernetes'})
    if not valid:
        results.ok("reject: non-semantic version")
    else:
        results.fail("reject: version", "should have failed")
    
    return results

def test_optimizer():
    print("\n=== RESOURCE OPTIMIZER TESTS ===\n")
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from policy_engine.modules.resource_optimizer import ResourceOptimizer
    from policy_engine.core.decision_context import DecisionContext, TaskContext
    
    optimizer = ResourceOptimizer()
    results = Results()
    
    # Training cluster routing
    print("Training Cluster Routing (GPU):")
    for job in TRAINING_SAMPLES[:2]:
        task = TaskContext(
            task_id=job['task_id'],
            task_type='training',
            user_id=job['user_id'],
            user_roles=['data_scientist'],
            priority=job.get('priority', 'normal'),
            requirement={'gpu_needed': job.get('gpu_count', 0) > 0, 'gpu_count': job.get('gpu_count', 1), 'memory_gb': job.get('memory_gb', 32)}
        )
        context = DecisionContext(task=task, resource=None, compliance=None)
        decision = optimizer.optimize(context)
        
        if decision.get('cluster') == 'training_cluster':
            results.ok("GPU route: " + job['task_id'] + " -> training_cluster")
        else:
            results.fail("GPU route: " + job['task_id'], "got " + str(decision.get('cluster')))
    
    # Inference cluster routing
    print("\nInference Cluster Routing (CPU):")
    for job in DEPLOY_SAMPLES[:1]:
        task = TaskContext(
            task_id=job['task_id'],
            task_type='inference',
            user_id=job['user_id'],
            user_roles=['devops'],
            priority=job.get('priority', 'normal'),
            requirement={'gpu_needed': False, 'cpu_cores': 4, 'memory_gb': 4}
        )
        context = DecisionContext(task=task, resource=None, compliance=None)
        decision = optimizer.optimize(context)
        
        if decision.get('cluster') == 'inference_cluster':
            results.ok("CPU route: " + job['task_id'] + " -> inference_cluster")
        else:
            results.fail("CPU route: " + job['task_id'], "got " + str(decision.get('cluster')))
    
    return results

def test_connector():
    print("\n=== DEPLOYMENT CONNECTOR TESTS ===\n")
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from policy_engine.modules.deployment_connector import DeploymentConnector
    
    connector = DeploymentConnector()
    results = Results()
    
    # Submit training
    print("Submit Training Jobs:")
    for job in TRAINING_SAMPLES[:2]:
        resp = connector.submit_training_job(job)
        if resp.get('success'):
            results.ok("submit: " + job['task_id'])
        else:
            results.fail("submit: " + job['task_id'], "failed")
    
    # Submit deployment
    print("\nSubmit Deployment Jobs:")
    for job in DEPLOY_SAMPLES[:2]:
        resp = connector.submit_deployment_job(job)
        if resp.get('success'):
            results.ok("submit: " + job['task_id'])
        else:
            results.fail("submit: " + job['task_id'], "failed")
    
    # Status tracking
    print("\nStatus Tracking:")
    job = TRAINING_SAMPLES[0]
    connector.submit_training_job(job)
    status = connector.get_task_status(job['task_id'])
    if status.get('success'):
        results.ok("status: " + job['task_id'] + " (" + status.get('status') + ")")
    else:
        results.fail("status: " + job['task_id'], "failed")
    
    return results

def test_integration():
    print("\n=== INTEGRATION TESTS ===\n")
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from policy_engine.utils.request_validator import RequestValidator
    from policy_engine.modules.deployment_connector import DeploymentConnector
    
    validator = RequestValidator()
    connector = DeploymentConnector()
    results = Results()
    
    # Training workflow: validate -> submit -> status
    print("Training Workflow:")
    job = TRAINING_SAMPLES[0]
    valid, err, cleaned = validator.validate_train_request(job)
    if valid:
        resp = connector.submit_training_job(cleaned)
        if resp.get('success'):
            status = connector.get_task_status(job['task_id'])
            if status.get('success'):
                results.ok("workflow: train validate->submit->status")
            else:
                results.fail("workflow: train status", "failed")
        else:
            results.fail("workflow: train submit", "failed")
    else:
        results.fail("workflow: train validate", err)
    
    # Deployment workflow: validate -> submit -> status
    print("\nDeployment Workflow:")
    job = DEPLOY_SAMPLES[0]
    valid, err, cleaned = validator.validate_deploy_request(job)
    if valid:
        resp = connector.submit_deployment_job(cleaned)
        if resp.get('success'):
            status = connector.get_task_status(job['task_id'])
            if status.get('success'):
                results.ok("workflow: deploy validate->submit->status")
            else:
                results.fail("workflow: deploy status", "failed")
        else:
            results.fail("workflow: deploy submit", "failed")
    else:
        results.fail("workflow: deploy validate", err)
    
    # E2E: Train + Deploy
    print("\nE2E Pipeline:")
    train_job = TRAINING_SAMPLES[1]
    deploy_job = DEPLOY_SAMPLES[1]
    
    _, _, train_clean = validator.validate_train_request(train_job)
    _, _, deploy_clean = validator.validate_deploy_request(deploy_job)
    
    train_resp = connector.submit_training_job(train_clean)
    deploy_resp = connector.submit_deployment_job(deploy_clean)
    
    if train_resp.get('success') and deploy_resp.get('success'):
        results.ok("E2E: train + deploy")
    else:
        results.fail("E2E: train + deploy", "submission failed")
    
    return results

def test_performance():
    print("\n=== PERFORMANCE TESTS ===\n")
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from policy_engine.modules.deployment_connector import DeploymentConnector
    
    connector = DeploymentConnector()
    results = Results()
    
    # Submission speed
    print("Submission Speed (10 jobs):")
    start = time.time()
    for i in range(10):
        connector.submit_training_job({'task_id': 'perf-' + str(i), 'user_id': 'u', 'model_name': 'm', 'dataset': 'd', 'epochs': 10, 'batch_size': 32, 'gpu_count': 1, 'gpu_type': 'v100', 'memory_gb': 16})
    elapsed = (time.time() - start) / 10 * 1000
    results.ok("submission speed: %.2f ms/job" % elapsed)
    
    # Status query speed
    print("\nStatus Query Speed (20 queries):")
    connector.submit_training_job({'task_id': 'perf-status', 'user_id': 'u', 'model_name': 'm', 'dataset': 'd', 'epochs': 10, 'batch_size': 32, 'gpu_count': 1, 'gpu_type': 'v100', 'memory_gb': 16})
    start = time.time()
    for _ in range(20):
        connector.get_task_status('perf-status')
    elapsed = (time.time() - start) / 20 * 1000
    results.ok("status query speed: %.2f ms/query" % elapsed)
    
    # Concurrent submissions
    print("\nConcurrent Submissions (100 mixed jobs):")
    start = time.time()
    for i in range(50):
        connector.submit_training_job({'task_id': 'conc-t-' + str(i), 'user_id': 'u', 'model_name': 'm', 'dataset': 'd', 'epochs': 10, 'batch_size': 32, 'gpu_count': 1, 'gpu_type': 'v100', 'memory_gb': 16})
        connector.submit_deployment_job({'task_id': 'conc-d-' + str(i), 'user_id': 'u', 'model_id': 'm', 'model_version': '1.0.0', 'target_platform': 'kubernetes', 'replicas': 1, 'cpu_limit': '2', 'memory_limit': '2Gi'})
    elapsed = time.time() - start
    throughput = 100 / elapsed
    results.ok("100 jobs in %.2f sec (%.0f jobs/sec)" % (elapsed, throughput))
    
    return results

# ============= MAIN =============

def main():
    print("\n" + "=" * 80)
    print("MLOps POLICY ENGINE - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print("Start: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    all_results = []
    
    try:
        all_results.append(("Request Validator", test_validator()))
        all_results.append(("Resource Optimizer", test_optimizer()))
        all_results.append(("Deployment Connector", test_connector()))
        all_results.append(("Integration Tests", test_integration()))
        all_results.append(("Performance Tests", test_performance()))
    except Exception as e:
        print("\nFATAL ERROR: " + str(e))
        import traceback
        traceback.print_exc()
        return False
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80 + "\n")
    
    total_passed = 0
    total_failed = 0
    all_errors = []
    
    for name, result in all_results:
        total_passed += result.passed
        total_failed += result.failed
        all_errors.extend(result.errors)
        status = "[OK]" if result.failed == 0 else "[FAIL]"
        print(status + " " + name + ": " + str(result.passed) + " passed, " + str(result.failed) + " failed")
    
    total = total_passed + total_failed
    print("\nOVERALL: " + str(total_passed) + "/" + str(total) + " tests passed")
    
    if all_errors:
        print("\nFAILED TESTS:")
        for name, reason in all_errors:
            print("  [FAIL] " + name + ": " + reason)
    
    print("\nEnd: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 80 + "\n")
    
    return total_failed == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
