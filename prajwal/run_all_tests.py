#!/usr/bin/env python
"""
Comprehensive Test Suite for MLOps Policy Engine
Executes all tests: Unit, Integration, Validation, E2E, Performance
Run from: f:\Multi-cloud directory
"""

import json
import time
from typing import Dict, Any
from datetime import datetime
import sys

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


class TestResult:
    """Track test results."""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, name):
        self.passed += 1
        print(f"{GREEN}✓{RESET} {name}")
    
    def add_fail(self, name, reason):
        self.failed += 1
        self.errors.append((name, reason))
        print(f"{RED}✗{RESET} {name}: {reason}")


# TEST DATA
TRAINING_JOBS = [
    {
        'task_id': 'train-gpu-001',
        'user_id': 'alice@company.com',
        'model_name': 'resnet50_classifier',
        'dataset': 'imagenet_2024',
        'epochs': 100,
        'batch_size': 64,
        'gpu_count': 2,
        'gpu_type': 'a100',
        'memory_gb': 48,
        'priority': 'high',
        'budget_limit': 2000.0
    },
    {
        'task_id': 'train-gpu-002',
        'user_id': 'bob@company.com',
        'model_name': 'bert_large',
        'dataset': 'wikipedia',
        'epochs': 50,
        'batch_size': 32,
        'gpu_count': 4,
        'gpu_type': 'h100',
        'memory_gb': 80,
        'priority': 'critical'
    },
    {
        'task_id': 'train-cpu-001',
        'user_id': 'charlie@company.com',
        'model_name': 'tabular',
        'dataset': 'structured_data',
        'epochs': 200,
        'batch_size': 256,
        'gpu_count': 0,
        'memory_gb': 16,
        'priority': 'normal'
    }
]

DEPLOYMENT_JOBS = [
    {
        'task_id': 'deploy-prod-001',
        'user_id': 'devops@company.com',
        'model_id': 'resnet50_classifier',
        'model_version': '2.1.3',
        'target_platform': 'kubernetes',
        'replicas': 5,
        'max_replicas': 20,
        'cpu_limit': '8',
        'memory_limit': '8Gi',
        'priority': 'high'
    },
    {
        'task_id': 'deploy-staging-001',
        'user_id': 'qa@company.com',
        'model_id': 'bert_large',
        'model_version': '1.5.0',
        'target_platform': 'docker',
        'replicas': 2,
        'cpu_limit': '4',
        'memory_limit': '4Gi',
        'priority': 'normal'
    }
]


def test_request_validation():
    """Test Request Validator"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}REQUEST VALIDATOR TESTS{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")
    
    from policy_engine.utils.request_validator import RequestValidator
    validator = RequestValidator()
    results = TestResult()
    
    # Valid training requests
    print(f"{BOLD}Valid Training Requests:{RESET}")
    for job in TRAINING_JOBS:
        is_valid, error, _ = validator.validate_train_request(job)
        if is_valid:
            results.add_pass(f"Training {job['task_id']}")
        else:
            results.add_fail(f"Training {job['task_id']}", error)
    
    # Valid deployment requests
    print(f"\n{BOLD}Valid Deployment Requests:{RESET}")
    for job in DEPLOYMENT_JOBS:
        is_valid, error, _ = validator.validate_deploy_request(job)
        if is_valid:
            results.add_pass(f"Deployment {job['task_id']}")
        else:
            results.add_fail(f"Deployment {job['task_id']}", error)
    
    # Invalid requests
    print(f"\n{BOLD}Invalid Requests (Should Fail):{RESET}")
    
    # Missing field
    is_valid, _, _ = validator.validate_train_request({'user_id': 'user@company.com'})
    if not is_valid:
        results.add_pass("Reject missing required field")
    else:
        results.add_fail("Reject missing field", "Should have failed")
    
    # Invalid epochs
    is_valid, _, _ = validator.validate_train_request({
        'task_id': 'test', 'user_id': 'user@company.com', 'model_name': 'x',
        'dataset': 'x', 'epochs': 5000, 'batch_size': 32
    })
    if not is_valid:
        results.add_pass("Reject epochs > 1000")
    else:
        results.add_fail("Reject epochs", "Should have failed")
    
    # Invalid semantic version
    is_valid, _, _ = validator.validate_deploy_request({
        'task_id': 'test', 'user_id': 'user@company.com', 'model_id': 'x',
        'model_version': 'latest', 'target_platform': 'kubernetes'
    })
    if not is_valid:
        results.add_pass("Reject non-semantic version")
    else:
        results.add_fail("Non-semantic version", "Should have failed")
    
    return results


def test_resource_optimizer():
    """Test Resource Optimizer"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}RESOURCE OPTIMIZER TESTS{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")
    
    from policy_engine.modules.resource_optimizer import ResourceOptimizer
    from policy_engine.core.decision_context import DecisionContext, TaskContext
    
    optimizer = ResourceOptimizer()
    results = TestResult()
    
    # Test training cluster routing
    print(f"{BOLD}Training Cluster Routing (GPU):{RESET}")
    for job in TRAINING_JOBS[:2]:
        task = TaskContext(
            task_id=job['task_id'],
            task_type='training',
            user_id=job['user_id'],
            user_roles=['data_scientist'],
            priority=job.get('priority', 'normal'),
            requirement={'gpu_needed': job.get('gpu_count', 0) > 0, 'gpu_count': job.get('gpu_count', 0), 'memory_gb': job.get('memory_gb', 32)}
        )
        context = DecisionContext(task=task, resource=None, compliance=None)
        decision = optimizer.optimize(context)
        
        if decision.get('cluster') == 'training_cluster':
            results.add_pass(f"GPU route: {job['task_id']} → training_cluster")
        else:
            results.add_fail(f"GPU route {job['task_id']}", decision.get('cluster'))
    
    # Test inference cluster routing
    print(f"\n{BOLD}Inference Cluster Routing (CPU):{RESET}")
    for job in DEPLOYMENT_JOBS[:1]:
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
            results.add_pass(f"CPU route: {job['task_id']} → inference_cluster")
        else:
            results.add_fail(f"CPU route {job['task_id']}", decision.get('cluster'))
    
    return results


def test_deployment_connector():
    """Test Deployment Connector"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}DEPLOYMENT CONNECTOR TESTS{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")
    
    from policy_engine.modules.deployment_connector import DeploymentConnector
    
    connector = DeploymentConnector()
    results = TestResult()
    
    # Test training submissions
    print(f"{BOLD}Training Job Submissions:{RESET}")
    for job in TRAINING_JOBS[:2]:
        response = connector.submit_training_job(job)
        if response.get('success'):
            results.add_pass(f"Submit training {job['task_id']}")
        else:
            results.add_fail(f"Submit training {job['task_id']}", "Failed")
    
    # Test deployment submissions
    print(f"\n{BOLD}Deployment Job Submissions:{RESET}")
    for job in DEPLOYMENT_JOBS[:2]:
        response = connector.submit_deployment_job(job)
        if response.get('success'):
            results.add_pass(f"Submit deployment {job['task_id']}")
        else:
            results.add_fail(f"Submit deployment {job['task_id']}", "Failed")
    
    # Test status tracking
    print(f"\n{BOLD}Status Tracking:{RESET}")
    job = TRAINING_JOBS[0]
    connector.submit_training_job(job)
    status = connector.get_task_status(job['task_id'])
    if status.get('success'):
        results.add_pass(f"Track status: {job['task_id']} ({status.get('status')})")
    else:
        results.add_fail(f"Track status {job['task_id']}", "Failed")
    
    # Test task listing
    print(f"\n{BOLD}Task Listing:{RESET}")
    task_list = connector.list_tasks(limit=10)
    if task_list.get('success'):
        count = len(task_list.get('tasks', []))
        results.add_pass(f"List tasks ({count} total)")
    else:
        results.add_fail("List tasks", "Failed")
    
    return results


def test_integration():
    """Test Integration: Validate → Submit → Status"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}INTEGRATION TESTS{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")
    
    from policy_engine.utils.request_validator import RequestValidator
    from policy_engine.modules.deployment_connector import DeploymentConnector
    
    validator = RequestValidator()
    connector = DeploymentConnector()
    results = TestResult()
    
    # Training workflow
    print(f"{BOLD}Training Workflow (Validate → Submit → Status):{RESET}")
    job = TRAINING_JOBS[0]
    is_valid, error, cleaned = validator.validate_train_request(job)
    if is_valid:
        response = connector.submit_training_job(cleaned)
        if response.get('success'):
            status = connector.get_task_status(job['task_id'])
            if status.get('success'):
                results.add_pass("Training workflow complete")
            else:
                results.add_fail("Training workflow", "Status check failed")
        else:
            results.add_fail("Training workflow", "Submission failed")
    else:
        results.add_fail("Training workflow", f"Validation: {error}")
    
    # Deployment workflow
    print(f"\n{BOLD}Deployment Workflow (Validate → Submit → Status):{RESET}")
    job = DEPLOYMENT_JOBS[0]
    is_valid, error, cleaned = validator.validate_deploy_request(job)
    if is_valid:
        response = connector.submit_deployment_job(cleaned)
        if response.get('success'):
            status = connector.get_task_status(job['task_id'])
            if status.get('success'):
                results.add_pass("Deployment workflow complete")
            else:
                results.add_fail("Deployment workflow", "Status check failed")
        else:
            results.add_fail("Deployment workflow", "Submission failed")
    else:
        results.add_fail("Deployment workflow", f"Validation: {error}")
    
    # E2E: Train then Deploy
    print(f"\n{BOLD}E2E Pipeline (Train → Deploy):{RESET}")
    train_job = TRAINING_JOBS[1]
    deploy_job = DEPLOYMENT_JOBS[1]
    
    _, _, train_clean = validator.validate_train_request(train_job)
    _, _, deploy_clean = validator.validate_deploy_request(deploy_job)
    
    train_resp = connector.submit_training_job(train_clean)
    deploy_resp = connector.submit_deployment_job(deploy_clean)
    
    if train_resp.get('success') and deploy_resp.get('success'):
        results.add_pass("E2E pipeline (train + deploy)")
    else:
        results.add_fail("E2E pipeline", "One or both submissions failed")
    
    return results


def test_performance():
    """Test Performance"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}PERFORMANCE TESTS{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")
    
    from policy_engine.modules.deployment_connector import DeploymentConnector
    
    connector = DeploymentConnector()
    results = TestResult()
    
    # Submission speed
    print(f"{BOLD}Submission Speed (10 jobs):{RESET}")
    start = time.time()
    for i in range(10):
        connector.submit_training_job({
            'task_id': f'perf-{i}', 'user_id': 'user@company.com',
            'model_name': f'model{i}', 'dataset': 'data',
            'epochs': 10, 'batch_size': 32, 'gpu_count': 1,
            'gpu_type': 'v100', 'memory_gb': 16
        })
    elapsed = (time.time() - start) / 10 * 1000
    results.add_pass(f"Submission speed: {elapsed:.2f}ms per job")
    
    # Status query speed
    print(f"\n{BOLD}Status Query Speed (20 queries):{RESET}")
    connector.submit_training_job({
        'task_id': 'perf-status', 'user_id': 'user@company.com',
        'model_name': 'model', 'dataset': 'data',
        'epochs': 10, 'batch_size': 32, 'gpu_count': 1,
        'gpu_type': 'v100', 'memory_gb': 16
    })
    start = time.time()
    for _ in range(20):
        connector.get_task_status('perf-status')
    elapsed = (time.time() - start) / 20 * 1000
    results.add_pass(f"Status query speed: {elapsed:.2f}ms per query")
    
    # Concurrent submissions
    print(f"\n{BOLD}Concurrent Submissions (100 mixed jobs):{RESET}")
    start = time.time()
    for i in range(50):
        connector.submit_training_job({
            'task_id': f'concurrent-train-{i}', 'user_id': f'user{i}@company.com',
            'model_name': f'model{i}', 'dataset': 'data',
            'epochs': 10, 'batch_size': 32, 'gpu_count': 1,
            'gpu_type': 'v100', 'memory_gb': 16
        })
        connector.submit_deployment_job({
            'task_id': f'concurrent-deploy-{i}', 'user_id': f'user{i}@company.com',
            'model_id': f'model{i}', 'model_version': '1.0.0',
            'target_platform': 'kubernetes', 'replicas': 1,
            'cpu_limit': '2', 'memory_limit': '2Gi'
        })
    elapsed = time.time() - start
    throughput = 100 / elapsed
    results.add_pass(f"Processed 100 jobs in {elapsed:.2f}s ({throughput:.0f} jobs/sec)")
    
    return results


def main():
    """Run all tests"""
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}MLOps POLICY ENGINE - COMPREHENSIVE TEST SUITE{RESET}")
    print(f"{BOLD}{'='*80}{RESET}")
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    all_results = []
    
    try:
        all_results.append(("Request Validation", test_request_validation()))
        all_results.append(("Resource Optimizer", test_resource_optimizer()))
        all_results.append(("Deployment Connector", test_deployment_connector()))
        all_results.append(("Integration Tests", test_integration()))
        all_results.append(("Performance Tests", test_performance()))
    except Exception as e:
        print(f"\n{RED}Fatal Error: {str(e)}{RESET}")
        import traceback
        traceback.print_exc()
        return False
    
    # Summary
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}TEST SUMMARY{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")
    
    total_passed = 0
    total_failed = 0
    all_errors = []
    
    for name, result in all_results:
        total_passed += result.passed
        total_failed += result.failed
        all_errors.extend(result.errors)
        status = f"{GREEN}✓{RESET}" if result.failed == 0 else f"{RED}✗{RESET}"
        print(f"{status} {name}: {result.passed} passed, {result.failed} failed")
    
    total = total_passed + total_failed
    print(f"\n{BOLD}Overall: {BLUE}{total_passed}/{total}{RESET} tests passed{RESET}")
    
    if all_errors:
        print(f"\n{RED}Failed Tests:{RESET}")
        for name, reason in all_errors:
            print(f"  ✗ {name}: {reason}")
    
    print(f"\n{BOLD}End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")
    
    return total_failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
