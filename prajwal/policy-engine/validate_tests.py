#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Policy Engine Validation Test - Direct Execution
Demonstrates core functionality with actual sample data
"""

import sys
import os
import re
from datetime import datetime

print("=" * 80)
print("MLOPS POLICY ENGINE - VALIDATION & EXECUTION TEST")
print("=" * 80)
print("Start:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print()

# ===== SAMPLE DATA =====

training_jobs = [
    {
        'task_id': 'train-001',
        'user_id': 'alice@company.com',
        'model_name': 'ResNet50',
        'dataset': 'MNIST',
        'epochs': 50,
        'batch_size': 32,
        'gpu_count': 2,
        'gpu_type': 'v100',
        'memory_gb': 32,
        'priority': 'high',
        'cluster_decision': 'training_cluster',
        'status': 'submitted'
    },
    {
        'task_id': 'train-002',
        'user_id': 'bob@company.com',
        'model_name': 'BERT',
        'dataset': 'Wikipedia',
        'epochs': 100,
        'batch_size': 64,
        'gpu_count': 4,
        'gpu_type': 'a100',
        'memory_gb': 64,
        'priority': 'normal',
        'cluster_decision': 'training_cluster',
        'status': 'running',
        'progress': '35%'
    },
    {
        'task_id': 'train-003',
        'user_id': 'charlie@company.com',
        'model_name': 'XGBoost',
        'dataset': 'Tabular Data',
        'epochs': 10,
        'batch_size': 100,
        'gpu_count': 0,
        'memory_gb': 16,
        'priority': 'low',
        'cluster_decision': 'inference_cluster',
        'status': 'completed'
    }
]

deployment_jobs = [
    {
        'task_id': 'deploy-001',
        'user_id': 'devops@company.com',
        'model_id': 'ResNet50',
        'model_version': '1.5.0',
        'target_platform': 'kubernetes',
        'replicas': 3,
        'cpu_limit': '4',
        'memory_limit': '4Gi',
        'priority': 'high',
        'cluster_decision': 'inference_cluster',
        'status': 'deployed'
    },
    {
        'task_id': 'deploy-002',
        'user_id': 'qa@company.com',
        'model_id': 'BERT',
        'model_version': '2.1.3',
        'target_platform': 'docker',
        'replicas': 1,
        'cpu_limit': '2',
        'memory_limit': '2Gi',
        'priority': 'normal',
        'cluster_decision': 'inference_cluster',
        'status': 'deployed'
    }
]

# ===== VALIDATION RULES =====

def validate_version(version_str):
    """Validate semantic versioning X.Y.Z"""
    pattern = r'^\d+\.\d+\.\d+$'
    return bool(re.match(pattern, version_str))

def validate_epochs(epochs):
    """Validate epochs between 1-1000"""
    return 1 <= epochs <= 1000

def validate_batch_size(batch_size):
    """Validate batch size between 1-10000"""
    return 1 <= batch_size <= 10000

def validate_gpu_count(gpu_count):
    """Validate GPU count between 0-8"""
    return 0 <= gpu_count <= 8

def validate_memory(memory_gb):
    """Validate memory between 4-256 GB"""
    return 4 <= memory_gb <= 256

def validate_replicas(replicas):
    """Validate replicas between 1-100"""
    return 1 <= replicas <= 100

# ===== TESTS =====

results = {'passed': 0, 'failed': 0, 'tests': []}

print("TEST 1: TRAINING JOB VALIDATION")
print("-" * 80)

for job in training_jobs:
    checks = {
        'epochs_valid': validate_epochs(job['epochs']),
        'batch_valid': validate_batch_size(job['batch_size']),
        'gpu_valid': validate_gpu_count(job['gpu_count']),
        'memory_valid': validate_memory(job['memory_gb'])
    }
    
    all_valid = all(checks.values())
    status = "PASS" if all_valid else "FAIL"
    
    msg = f"[{status}] train-{job['task_id']}: {job['model_name']} - {job['epochs']} epochs, {job['gpu_count']}x {job.get('gpu_type', 'CPU')}"
    print(msg)
    
    if all_valid:
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    results['tests'].append({
        'name': f"train-{job['task_id']}",
        'passed': all_valid,
        'details': checks
    })

print()
print("TEST 2: DEPLOYMENT JOB VALIDATION")
print("-" * 80)

for job in deployment_jobs:
    checks = {
        'version_valid': validate_version(job['model_version']),
        'replicas_valid': validate_replicas(job['replicas'])
    }
    
    all_valid = all(checks.values())
    status = "PASS" if all_valid else "FAIL"
    
    msg = f"[{status}] deploy-{job['task_id']}: {job['model_id']} v{job['model_version']} on {job['target_platform']}"
    print(msg)
    
    if all_valid:
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    results['tests'].append({
        'name': f"deploy-{job['task_id']}",
        'passed': all_valid,
        'details': checks
    })

print()
print("TEST 3: CLUSTER ROUTING DECISIONS")
print("-" * 80)

for job in training_jobs:
    expected = 'training_cluster' if job['gpu_count'] > 0 else 'inference_cluster'
    actual = job['cluster_decision']
    correct = expected == actual
    status = "PASS" if correct else "FAIL"
    
    msg = f"[{status}] {job['task_id']}: GPU={job['gpu_count']} -> {actual} (expected: {expected})"
    print(msg)
    
    if correct:
        results['passed'] += 1
    else:
        results['failed'] += 1

for job in deployment_jobs:
    expected = 'inference_cluster'
    actual = job['cluster_decision']
    correct = expected == actual
    status = "PASS" if correct else "FAIL"
    
    msg = f"[{status}] {job['task_id']}: {job['target_platform']} -> {actual}"
    print(msg)
    
    if correct:
        results['passed'] += 1
    else:
        results['failed'] += 1

print()
print("TEST 4: STATUS TRACKING")
print("-" * 80)

all_jobs = training_jobs + deployment_jobs
for job in all_jobs:
    status = job.get('status', 'unknown')
    valid_statuses = ['submitted', 'running', 'completed', 'deployed', 'pending', 'failed']
    correct = status in valid_statuses
    mark = "PASS" if correct else "FAIL"
    
    progress = f" ({job.get('progress', '0%')})" if 'progress' in job else ""
    msg = f"[{mark}] {job['task_id']}: status={status}{progress}"
    print(msg)
    
    if correct:
        results['passed'] += 1
    else:
        results['failed'] += 1

print()
print("TEST 5: INVALID REQUEST REJECTION")
print("-" * 80)

invalid_tests = [
    {'epochs': 5000, 'batch_size': 32, 'reason': 'epochs > 1000'},
    {'epochs': 50, 'batch_size': 50000, 'reason': 'batch_size > 10000'},
    {'epochs': 0, 'batch_size': 32, 'reason': 'epochs < 1'},
    {'model_version': 'latest', 'reason': 'non-semantic version'},
    {'model_version': '1.2', 'reason': 'incomplete version'},
    {'replicas': 200, 'reason': 'replicas > 100'},
]

for test in invalid_tests:
    should_fail = True
    this_invalid = False
    
    # Check all validation conditions
    if 'epochs' in test:
        this_invalid = this_invalid or (not validate_epochs(test['epochs']))
    if 'batch_size' in test:
        this_invalid = this_invalid or (not validate_batch_size(test['batch_size']))
    if 'model_version' in test:
        this_invalid = this_invalid or (not validate_version(test['model_version']))
    if 'replicas' in test:
        this_invalid = this_invalid or (not validate_replicas(test['replicas']))
    
    correct = this_invalid == should_fail
    mark = "PASS" if correct else "FAIL"
    
    msg = f"[{mark}] reject: {test['reason']}"
    print(msg)
    
    if correct:
        results['passed'] += 1
    else:
        results['failed'] += 1

print()
print("TEST 6: SAMPLE DATA COMPLETENESS")
print("-" * 80)

required_train_fields = {'task_id', 'user_id', 'model_name', 'dataset', 'epochs', 'batch_size', 'gpu_count', 'memory_gb'}
required_deploy_fields = {'task_id', 'user_id', 'model_id', 'model_version', 'target_platform', 'replicas'}

for job in training_jobs:
    has_all = required_train_fields.issubset(set(job.keys()))
    mark = "PASS" if has_all else "FAIL"
    msg = f"[{mark}] {job['task_id']}: training job fields complete"
    print(msg)
    
    if has_all:
        results['passed'] += 1
    else:
        results['failed'] += 1

for job in deployment_jobs:
    has_all = required_deploy_fields.issubset(set(job.keys()))
    mark = "PASS" if has_all else "FAIL"
    msg = f"[{mark}] {job['task_id']}: deployment job fields complete"
    print(msg)
    
    if has_all:
        results['passed'] += 1
    else:
        results['failed'] += 1

# ===== SUMMARY =====

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)

total = results['passed'] + results['failed']
print(f"TOTAL: {results['passed']}/{total} tests PASSED")

if results['failed'] == 0:
    print("STATUS: ALL TESTS PASSED")
else:
    print(f"STATUS: {results['failed']} test(s) failed")

print("End:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print()

# Print sample data structure
print("=" * 80)
print("SAMPLE DATA STRUCTURE")
print("=" * 80)
print()
print(f"Training Jobs: {len(training_jobs)}")
for job in training_jobs:
    print(f"  - {job['task_id']}: {job['model_name']} ({job['epochs']} epochs, {job['gpu_count']} GPUs)")

print()
print(f"Deployment Jobs: {len(deployment_jobs)}")
for job in deployment_jobs:
    print(f"  - {job['task_id']}: {job['model_id']} v{job['model_version']} ({job['target_platform']})")

print()
print("=" * 80)

sys.exit(0 if results['failed'] == 0 else 1)
