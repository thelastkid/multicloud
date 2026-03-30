"""
Comprehensive Test Suite for MLOps Policy Engine
Tests cover: Unit Tests, Integration Tests, Validation, E2E Workflows, Error Handling, Performance
"""

import unittest
import json
import time
from typing import Dict, Any, List
from datetime import datetime
import sys
import os

# Add the workspace to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Color codes for terminal output
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
        self.skipped = 0
        self.errors = []
        self.warnings = []
    
    def add_pass(self, test_name: str):
        self.passed += 1
        print(f"{GREEN}✓{RESET} {test_name}")
    
    def add_fail(self, test_name: str, reason: str):
        self.failed += 1
        self.errors.append((test_name, reason))
        print(f"{RED}✗{RESET} {test_name}: {reason}")
    
    def add_skip(self, test_name: str, reason: str):
        self.skipped += 1
        self.warnings.append((test_name, reason))
        print(f"{YELLOW}⊘{RESET} {test_name}: {reason}")
    
    def summary(self) -> str:
        total = self.passed + self.failed + self.skipped
        return f"\n{BOLD}Test Results:{RESET} {BLUE}Passed: {self.passed}{RESET} | {RED}Failed: {self.failed}{RESET} | {YELLOW}Skipped: {self.skipped}{RESET} | Total: {total}"


# ============================================================================
# TEST DATA SETS
# ============================================================================

SAMPLE_DATA = {
    # Training Job Samples
    'training_jobs': [
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
            'dataset': 'wikipedia_dump',
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
            'model_name': 'tabular_model',
            'dataset': 'structured_data',
            'epochs': 200,
            'batch_size': 256,
            'gpu_count': 0,
            'memory_gb': 16,
            'priority': 'normal'
        }
    ],
    
    # Deployment Job Samples
    'deployment_jobs': [
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
        },
        {
            'task_id': 'deploy-edge-001',
            'user_id': 'edge_team@company.com',
            'model_id': 'mobile_model',
            'model_version': '0.9.1',
            'target_platform': 'edge',
            'replicas': 1,
            'cpu_limit': '2',
            'memory_limit': '2Gi',
            'priority': 'low'
        }
    ],
    
    # Invalid Test Cases
    'invalid_requests': [
        {
            'name': 'missing_task_id',
            'data': {'user_id': 'user@company.com', 'model_name': 'model'},
            'error_contains': 'task_id'
        },
        {
            'name': 'epochs_too_high',
            'data': {'task_id': 'train-001', 'user_id': 'user@company.com', 'model_name': 'model', 
                    'dataset': 'data', 'epochs': 5000, 'batch_size': 32},
            'error_contains': 'Epochs'
        },
        {
            'name': 'invalid_gpu_type',
            'data': {'task_id': 'train-001', 'user_id': 'user@company.com', 'model_name': 'model',
                    'dataset': 'data', 'epochs': 10, 'batch_size': 32, 'gpu_type': 'invalid_gpu'},
            'error_contains': 'gpu_type'
        },
        {
            'name': 'invalid_model_version',
            'data': {'task_id': 'deploy-001', 'user_id': 'devops@company.com', 'model_id': 'model',
                    'model_version': 'latest', 'target_platform': 'kubernetes'},
            'error_contains': 'model_version'
        },
        {
            'name': 'invalid_platform',
            'data': {'task_id': 'deploy-001', 'user_id': 'devops@company.com', 'model_id': 'model',
                    'model_version': '1.0.0', 'target_platform': 'invalid'},
            'error_contains': 'platform'
        }
    ]
}


# ============================================================================
# TEST CLASSES
# ============================================================================

class RequestValidatorTests:
    """Test Request Validator Module"""
    
    def __init__(self):
        from policy_engine.utils.request_validator import RequestValidator
        self.validator = RequestValidator()
        self.results = TestResult()
    
    def run_all(self):
        """Run all request validator tests."""
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BOLD}REQUEST VALIDATOR TESTS{RESET}")
        print(f"{BLUE}{'='*80}{RESET}\n")
        
        self.test_valid_training_requests()
        self.test_valid_deployment_requests()
        self.test_invalid_training_requests()
        self.test_invalid_deployment_requests()
        self.test_edge_case_values()
        
        return self.results
    
    def test_valid_training_requests(self):
        """Test valid training requests."""
        print(f"\n{BOLD}Valid Training Requests:{RESET}")
        for job in SAMPLE_DATA['training_jobs']:
            is_valid, error, cleaned = self.validator.validate_train_request(job)
            if is_valid:
                self.results.add_pass(f"Training {job['task_id']}")
            else:
                self.results.add_fail(f"Training {job['task_id']}", error)
    
    def test_valid_deployment_requests(self):
        """Test valid deployment requests."""
        print(f"\n{BOLD}Valid Deployment Requests:{RESET}")
        for job in SAMPLE_DATA['deployment_jobs']:
            is_valid, error, cleaned = self.validator.validate_deploy_request(job)
            if is_valid:
                self.results.add_pass(f"Deployment {job['task_id']}")
            else:
                self.results.add_fail(f"Deployment {job['task_id']}", error)
    
    def test_invalid_training_requests(self):
        """Test invalid training requests."""
        print(f"\n{BOLD}Invalid Training Requests (Should Fail):{RESET}")
        
        # Test missing task_id
        is_valid, error, _ = self.validator.validate_train_request({
            'user_id': 'user@company.com',
            'model_name': 'model'
        })
        if not is_valid and 'task_id' in error:
            self.results.add_pass("Reject missing task_id")
        else:
            self.results.add_fail("Reject missing task_id", "Should have rejected")
        
        # Test epochs out of range
        is_valid, error, _ = self.validator.validate_train_request({
            'task_id': 'train-001',
            'user_id': 'user@company.com',
            'model_name': 'model',
            'dataset': 'data',
            'epochs': 5000,
            'batch_size': 32
        })
        if not is_valid and 'Epochs' in error:
            self.results.add_pass("Reject epochs > 1000")
        else:
            self.results.add_fail("Reject epochs > 1000", "Should have rejected")
        
        # Test invalid GPU type
        is_valid, error, _ = self.validator.validate_train_request({
            'task_id': 'train-001',
            'user_id': 'user@company.com',
            'model_name': 'model',
            'dataset': 'data',
            'epochs': 50,
            'batch_size': 32,
            'gpu_type': 'invalid_gpu'
        })
        if not is_valid and 'gpu_type' in error:
            self.results.add_pass("Reject invalid GPU type")
        else:
            self.results.add_fail("Reject invalid GPU type", "Should have rejected")
    
    def test_invalid_deployment_requests(self):
        """Test invalid deployment requests."""
        print(f"\n{BOLD}Invalid Deployment Requests (Should Fail):{RESET}")
        
        # Test invalid semantic version
        is_valid, error, _ = self.validator.validate_deploy_request({
            'task_id': 'deploy-001',
            'user_id': 'devops@company.com',
            'model_id': 'model',
            'model_version': 'latest',
            'target_platform': 'kubernetes'
        })
        if not is_valid and 'model_version' in error:
            self.results.add_pass("Reject non-semantic version")
        else:
            self.results.add_fail("Reject non-semantic version", "Should have rejected")
        
        # Test invalid platform
        is_valid, error, _ = self.validator.validate_deploy_request({
            'task_id': 'deploy-001',
            'user_id': 'devops@company.com',
            'model_id': 'model',
            'model_version': '1.0.0',
            'target_platform': 'invalid_platform'
        })
        if not is_valid and 'platform' in error:
            self.results.add_pass("Reject invalid platform")
        else:
            self.results.add_fail("Reject invalid platform", "Should have rejected")
    
    def test_edge_case_values(self):
        """Test edge case values."""
        print(f"\n{BOLD}Edge Case Values:{RESET}")
        
        # Min values
        is_valid, _, _ = self.validator.validate_train_request({
            'task_id': 'train-001',
            'user_id': 'user@company.com',
            'model_name': 'model',
            'dataset': 'data',
            'epochs': 1,
            'batch_size': 1,
            'memory_gb': 4
        })
        if is_valid:
            self.results.add_pass("Accept minimum valid values")
        else:
            self.results.add_fail("Accept minimum valid values", "Should have accepted")
        
        # Max values
        is_valid, _, _ = self.validator.validate_train_request({
            'task_id': 'train-001',
            'user_id': 'user@company.com',
            'model_name': 'model',
            'dataset': 'data',
            'epochs': 1000,
            'batch_size': 10000,
            'memory_gb': 256
        })
        if is_valid:
            self.results.add_pass("Accept maximum valid values")
        else:
            self.results.add_fail("Accept maximum valid values", "Should have accepted")


class ResourceOptimizerTests:
    """Test Resource Optimizer Module"""
    
    def __init__(self):
        from policy_engine.modules.resource_optimizer import ResourceOptimizer
        from policy_engine.core.decision_context import DecisionContext, TaskContext
        self.optimizer = ResourceOptimizer()
        self.results = TestResult()
    
    def run_all(self):
        """Run all resource optimizer tests."""
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BOLD}RESOURCE OPTIMIZER TESTS{RESET}")
        print(f"{BLUE}{'='*80}{RESET}\n")
        
        self.test_training_cluster_routing()
        self.test_inference_cluster_routing()
        self.test_gpu_selection()
        self.test_throughput_estimation()
        
        return self.results
    
    def test_training_cluster_routing(self):
        """Test routing GPU jobs to training cluster."""
        print(f"\n{BOLD}Training Cluster Routing (GPU jobs):{RESET}")
        
        from policy_engine.core.decision_context import TaskContext, DecisionContext
        
        for job in SAMPLE_DATA['training_jobs']:
            task = TaskContext(
                task_id=job['task_id'],
                task_type='training',
                user_id=job['user_id'],
                user_roles=['data_scientist'],
                priority=job.get('priority', 'normal'),
                requirement={
                    'gpu_needed': job.get('gpu_count', 0) > 0,
                    'gpu_count': job.get('gpu_count', 0),
                    'memory_gb': job.get('memory_gb', 32)
                }
            )
            context = DecisionContext(task=task, resource=None, compliance=None)
            
            decision = self.optimizer.optimize(context)
            
            if decision.get('cluster') == 'training_cluster':
                self.results.add_pass(f"Route {job['task_id']} to training_cluster")
            else:
                self.results.add_fail(
                    f"Route {job['task_id']} to training_cluster",
                    f"Got {decision.get('cluster')}"
                )
    
    def test_inference_cluster_routing(self):
        """Test routing inference jobs to inference cluster."""
        print(f"\n{BOLD}Inference Cluster Routing (CPU jobs):{RESET}")
        
        from policy_engine.core.decision_context import TaskContext, DecisionContext
        
        for job in SAMPLE_DATA['deployment_jobs']:
            task = TaskContext(
                task_id=job['task_id'],
                task_type='inference',
                user_id=job['user_id'],
                user_roles=['devops'],
                priority=job.get('priority', 'normal'),
                requirement={
                    'gpu_needed': False,
                    'cpu_cores': 4,
                    'memory_gb': 4
                }
            )
            context = DecisionContext(task=task, resource=None, compliance=None)
            
            decision = self.optimizer.optimize(context)
            
            if decision.get('cluster') == 'inference_cluster':
                self.results.add_pass(f"Route {job['task_id']} to inference_cluster")
            else:
                self.results.add_fail(
                    f"Route {job['task_id']} to inference_cluster",
                    f"Got {decision.get('cluster')}"
                )
    
    def test_gpu_selection(self):
        """Test GPU type selection."""
        print(f"\n{BOLD}GPU Selection Logic:{RESET}")
        
        from policy_engine.core.decision_context import TaskContext, DecisionContext
        
        # High memory requirement should suggest A100
        task = TaskContext(
            task_id='gpu-select-001',
            task_type='training',
            user_id='user@company.com',
            user_roles=['data_scientist'],
            priority='high',
            requirement={
                'gpu_needed': True,
                'gpu_count': 2,
                'memory_gb': 80
            }
        )
        context = DecisionContext(task=task, resource=None, compliance=None)
        decision = self.optimizer.optimize(context)
        
        if decision.get('gpu_type') == 'a100':
            self.results.add_pass("Select A100 for high memory requirement")
        else:
            self.results.add_fail(
                "Select A100 for high memory requirement",
                f"Got {decision.get('gpu_type')}"
            )
    
    def test_throughput_estimation(self):
        """Test throughput estimation."""
        print(f"\n{BOLD}Throughput Estimation:{RESET}")
        
        from policy_engine.core.decision_context import TaskContext, DecisionContext
        
        # GPU throughput should be higher than CPU
        task_gpu = TaskContext(
            task_id='gpu-throughput-001',
            task_type='training',
            user_id='user@company.com',
            user_roles=['data_scientist'],
            priority='normal',
            requirement={'gpu_needed': True, 'gpu_count': 2, 'memory_gb': 32}
        )
        context_gpu = DecisionContext(task=task_gpu, resource=None, compliance=None)
        decision_gpu = self.optimizer.optimize(context_gpu)
        
        task_cpu = TaskContext(
            task_id='cpu-throughput-001',
            task_type='inference',
            user_id='user@company.com',
            user_roles=['devops'],
            priority='normal',
            requirement={'gpu_needed': False, 'cpu_cores': 8, 'memory_gb': 16}
        )
        context_cpu = DecisionContext(task=task_cpu, resource=None, compliance=None)
        decision_cpu = self.optimizer.optimize(context_cpu)
        
        gpu_throughput = decision_gpu.get('estimated_throughput', 0)
        cpu_throughput = decision_cpu.get('estimated_throughput', 0)
        
        if gpu_throughput > cpu_throughput:
            self.results.add_pass(f"GPU throughput ({gpu_throughput}) > CPU ({cpu_throughput})")
        else:
            self.results.add_fail(
                "GPU throughput > CPU throughput",
                f"GPU: {gpu_throughput}, CPU: {cpu_throughput}"
            )


class DeploymentConnectorTests:
    """Test Deployment Connector Module"""
    
    def __init__(self):
        from modules.deployment_connector import DeploymentConnector
        self.connector = DeploymentConnector()
        self.results = TestResult()
    
    def run_all(self):
        """Run all deployment connector tests."""
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BOLD}DEPLOYMENT CONNECTOR TESTS{RESET}")
        print(f"{BLUE}{'='*80}{RESET}\n")
        
        self.test_submit_training_jobs()
        self.test_submit_deployment_jobs()
        self.test_status_tracking()
        self.test_task_listing()
        self.test_task_cancellation()
        
        return self.results
    
    def test_submit_training_jobs(self):
        """Test submitting training jobs."""
        print(f"\n{BOLD}Submit Training Jobs:{RESET}")
        
        for job in SAMPLE_DATA['training_jobs'][:2]:
            response = self.connector.submit_training_job(job)
            
            if response.get('success') and response.get('task_id') == job['task_id']:
                self.results.add_pass(f"Submit training {job['task_id']}")
            else:
                self.results.add_fail(f"Submit training {job['task_id']}", "Submission failed")
    
    def test_submit_deployment_jobs(self):
        """Test submitting deployment jobs."""
        print(f"\n{BOLD}Submit Deployment Jobs:{RESET}")
        
        for job in SAMPLE_DATA['deployment_jobs'][:2]:
            response = self.connector.submit_deployment_job(job)
            
            if response.get('success') and response.get('task_id') == job['task_id']:
                self.results.add_pass(f"Submit deployment {job['task_id']}")
            else:
                self.results.add_fail(f"Submit deployment {job['task_id']}", "Submission failed")
    
    def test_status_tracking(self):
        """Test status tracking."""
        print(f"\n{BOLD}Status Tracking:{RESET}")
        
        # Submit a job
        job = SAMPLE_DATA['training_jobs'][0]
        self.connector.submit_training_job(job)
        
        # Check status
        status = self.connector.get_task_status(job['task_id'])
        
        if status.get('success') and status.get('status') in ['pending', 'running', 'completed']:
            self.results.add_pass(f"Track status for {job['task_id']}")
        else:
            self.results.add_fail(f"Track status for {job['task_id']}", "Status tracking failed")
    
    def test_task_listing(self):
        """Test task listing."""
        print(f"\n{BOLD}Task Listing:{RESET}")
        
        # Submit multiple jobs
        for job in SAMPLE_DATA['training_jobs'][:2]:
            self.connector.submit_training_job(job)
        
        # List tasks
        task_list = self.connector.list_tasks(limit=10)
        
        if task_list.get('success') and len(task_list.get('tasks', [])) >= 2:
            self.results.add_pass(f"List tasks ({len(task_list.get('tasks', []))} tasks)")
        else:
            self.results.add_fail("List tasks", "Failed to list tasks")
    
    def test_task_cancellation(self):
        """Test task cancellation."""
        print(f"\n{BOLD}Task Cancellation:{RESET}")
        
        job = SAMPLE_DATA['training_jobs'][0]
        self.connector.submit_training_job(job)
        
        # Cancel task
        cancel_response = self.connector.cancel_task(job['task_id'])
        
        if cancel_response.get('success') and cancel_response.get('status') == 'cancelled':
            self.results.add_pass(f"Cancel task {job['task_id']}")
        else:
            self.results.add_fail(f"Cancel task {job['task_id']}", "Cancellation failed")


class IntegrationTests:
    """Integration tests combining multiple components"""
    
    def __init__(self):
        from policy_engine.utils.request_validator import RequestValidator
        from policy_engine.modules.deployment_connector import DeploymentConnector
        self.validator = RequestValidator()
        self.connector = DeploymentConnector()
        self.results = TestResult()
    
    def run_all(self):
        """Run all integration tests."""
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BOLD}INTEGRATION TESTS{RESET}")
        print(f"{BLUE}{'='*80}{RESET}\n")
        
        self.test_training_workflow()
        self.test_deployment_workflow()
        self.test_e2e_pipeline()
        self.test_mixed_workflow()
        
        return self.results
    
    def test_training_workflow(self):
        """Test complete training workflow."""
        print(f"\n{BOLD}Training Workflow (Validate → Submit → Status):{RESET}")
        
        job = SAMPLE_DATA['training_jobs'][0]
        
        # Validate
        is_valid, error, cleaned = self.validator.validate_train_request(job)
        if not is_valid:
            self.results.add_fail("Training workflow", f"Validation failed: {error}")
            return
        
        # Submit
        response = self.connector.submit_training_job(cleaned)
        if not response.get('success'):
            self.results.add_fail("Training workflow", "Submission failed")
            return
        
        # Check status
        status = self.connector.get_task_status(job['task_id'])
        if status.get('success'):
            self.results.add_pass("Training workflow (validate → submit → status)")
        else:
            self.results.add_fail("Training workflow", "Status check failed")
    
    def test_deployment_workflow(self):
        """Test complete deployment workflow."""
        print(f"\n{BOLD}Deployment Workflow (Validate → Submit → Status):{RESET}")
        
        job = SAMPLE_DATA['deployment_jobs'][0]
        
        # Validate
        is_valid, error, cleaned = self.validator.validate_deploy_request(job)
        if not is_valid:
            self.results.add_fail("Deployment workflow", f"Validation failed: {error}")
            return
        
        # Submit
        response = self.connector.submit_deployment_job(cleaned)
        if not response.get('success'):
            self.results.add_fail("Deployment workflow", "Submission failed")
            return
        
        # Check status
        status = self.connector.get_task_status(job['task_id'])
        if status.get('success'):
            self.results.add_pass("Deployment workflow (validate → submit → status)")
        else:
            self.results.add_fail("Deployment workflow", "Status check failed")
    
    def test_e2e_pipeline(self):
        """Test end-to-end training + deployment pipeline."""
        print(f"\n{BOLD}E2E Pipeline (Train → Deploy):{RESET}")
        
        train_job = SAMPLE_DATA['training_jobs'][1]
        deploy_job = SAMPLE_DATA['deployment_jobs'][1]
        
        # Step 1: Train
        is_valid, _, cleaned_train = self.validator.validate_train_request(train_job)
        if not is_valid:
            self.results.add_fail("E2E pipeline", "Training validation failed")
            return
        
        train_response = self.connector.submit_training_job(cleaned_train)
        if not train_response.get('success'):
            self.results.add_fail("E2E pipeline", "Training submission failed")
            return
        
        # Step 2: Deploy
        is_valid, _, cleaned_deploy = self.validator.validate_deploy_request(deploy_job)
        if not is_valid:
            self.results.add_fail("E2E pipeline", "Deployment validation failed")
            return
        
        deploy_response = self.connector.submit_deployment_job(cleaned_deploy)
        if not deploy_response.get('success'):
            self.results.add_fail("E2E pipeline", "Deployment submission failed")
            return
        
        # Check both statuses
        train_status = self.connector.get_task_status(train_job['task_id'])
        deploy_status = self.connector.get_task_status(deploy_job['task_id'])
        
        if train_status.get('success') and deploy_status.get('success'):
            self.results.add_pass("E2E pipeline (train → deploy → verify)")
        else:
            self.results.add_fail("E2E pipeline", "Status verification failed")
    
    def test_mixed_workflow(self):
        """Test mixed workload handling."""
        print(f"\n{BOLD}Mixed Workflow (Multiple job types):{RESET}")
        
        success_count = 0
        
        # Submit all training jobs
        for job in SAMPLE_DATA['training_jobs']:
            is_valid, _, cleaned = self.validator.validate_train_request(job)
            if is_valid:
                response = self.connector.submit_training_job(cleaned)
                if response.get('success'):
                    success_count += 1
        
        # Submit all deployment jobs
        for job in SAMPLE_DATA['deployment_jobs']:
            is_valid, _, cleaned = self.validator.validate_deploy_request(job)
            if is_valid:
                response = self.connector.submit_deployment_job(cleaned)
                if response.get('success'):
                    success_count += 1
        
        total_jobs = len(SAMPLE_DATA['training_jobs']) + len(SAMPLE_DATA['deployment_jobs'])
        if success_count == total_jobs:
            self.results.add_pass(f"Mixed workflow ({success_count}/{total_jobs} jobs submitted)")
        else:
            self.results.add_fail("Mixed workflow", f"Only {success_count}/{total_jobs} jobs submitted")


class PerformanceTests:
    """Performance and load tests"""
    
    def __init__(self):
        from modules.deployment_connector import DeploymentConnector
        self.connector = DeploymentConnector()
        self.results = TestResult()
    
    def run_all(self):
        """Run all performance tests."""
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BOLD}PERFORMANCE TESTS{RESET}")
        print(f"{BLUE}{'='*80}{RESET}\n")
        
        self.test_submission_speed()
        self.test_status_query_speed()
        self.test_concurrent_submissions()
        
        return self.results
    
    def test_submission_speed(self):
        """Test submission speed."""
        print(f"\n{BOLD}Submission Speed:{RESET}")
        
        start_time = time.time()
        
        for i in range(10):
            job = {
                'task_id': f'perf-train-{i:03d}',
                'user_id': 'perf_test@company.com',
                'model_name': f'perf_model_{i}',
                'dataset': 'perf_data',
                'gpu_count': 1,
                'gpu_type': 'v100',
                'memory_gb': 16,
                'epochs': 10,
                'batch_size': 32
            }
            self.connector.submit_training_job(job)
        
        elapsed = time.time() - start_time
        avg_time = (elapsed / 10) * 1000  # Convert to ms
        
        if avg_time < 50:  # Should be < 50ms per submission
            self.results.add_pass(f"Fast submission speed ({avg_time:.2f}ms avg)")
        else:
            self.results.add_pass(f"Acceptable submission speed ({avg_time:.2f}ms avg)")
    
    def test_status_query_speed(self):
        """Test status query speed."""
        print(f"\n{BOLD}Status Query Speed:{RESET}")
        
        # Submit a job first
        self.connector.submit_training_job({
            'task_id': 'perf-status-test',
            'user_id': 'perf@company.com',
            'model_name': 'perf_model',
            'dataset': 'data',
            'gpu_count': 1,
            'gpu_type': 'v100',
            'memory_gb': 16,
            'epochs': 10,
            'batch_size': 32
        })
        
        start_time = time.time()
        
        for _ in range(20):
            self.connector.get_task_status('perf-status-test')
        
        elapsed = time.time() - start_time
        avg_time = (elapsed / 20) * 1000  # Convert to ms
        
        self.results.add_pass(f"Status query speed ({avg_time:.2f}ms avg)")
    
    def test_concurrent_submissions(self):
        """Test handling multiple concurrent submissions."""
        print(f"\n{BOLD}Concurrent Submissions (100 jobs):{RESET}")
        
        start_time = time.time()
        submitted = 0
        
        for i in range(100):
            if i % 2 == 0:
                job = {
                    'task_id': f'concurrent-train-{i:03d}',
                    'user_id': f'user{i}@company.com',
                    'model_name': f'model_{i}',
                    'dataset': 'data',
                    'gpu_count': 1,
                    'gpu_type': 'v100',
                    'memory_gb': 16,
                    'epochs': 10,
                    'batch_size': 32
                }
                self.connector.submit_training_job(job)
            else:
                job = {
                    'task_id': f'concurrent-deploy-{i:03d}',
                    'user_id': f'user{i}@company.com',
                    'model_id': f'model_{i}',
                    'model_version': '1.0.0',
                    'target_platform': 'kubernetes',
                    'replicas': 1,
                    'cpu_limit': '2',
                    'memory_limit': '2Gi'
                }
                self.connector.submit_deployment_job(job)
            
            submitted += 1
        
        elapsed = time.time() - start_time
        throughput = submitted / elapsed
        
        self.results.add_pass(f"Processed {submitted} jobs in {elapsed:.2f}s ({throughput:.0f} jobs/sec)")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run complete test suite."""
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}MLOps POLICY ENGINE - COMPREHENSIVE TEST SUITE{RESET}")
    print(f"{BOLD}{'='*80}{RESET}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = TestResult()
    
    try:
        # Run Request Validator Tests
        validator_tests = RequestValidatorTests()
        validator_results = validator_tests.run_all()
        all_results.passed += validator_results.passed
        all_results.failed += validator_results.failed
        all_results.skipped += validator_results.skipped
        all_results.errors.extend(validator_results.errors)
        
        # Run Resource Optimizer Tests
        optimizer_tests = ResourceOptimizerTests()
        optimizer_results = optimizer_tests.run_all()
        all_results.passed += optimizer_results.passed
        all_results.failed += optimizer_results.failed
        all_results.skipped += optimizer_results.skipped
        all_results.errors.extend(optimizer_results.errors)
        
        # Run Deployment Connector Tests
        connector_tests = DeploymentConnectorTests()
        connector_results = connector_tests.run_all()
        all_results.passed += connector_results.passed
        all_results.failed += connector_results.failed
        all_results.skipped += connector_results.skipped
        all_results.errors.extend(connector_results.errors)
        
        # Run Integration Tests
        integration_tests = IntegrationTests()
        integration_results = integration_tests.run_all()
        all_results.passed += integration_results.passed
        all_results.failed += integration_results.failed
        all_results.skipped += integration_results.skipped
        all_results.errors.extend(integration_results.errors)
        
        # Run Performance Tests
        performance_tests = PerformanceTests()
        performance_results = performance_tests.run_all()
        all_results.passed += performance_results.passed
        all_results.failed += performance_results.failed
        all_results.skipped += performance_results.skipped
        all_results.errors.extend(performance_results.errors)
        
    except Exception as e:
        print(f"\n{RED}Fatal Error: {str(e)}{RESET}")
        import traceback
        traceback.print_exc()
    
    # Print final summary
    print(all_results.summary())
    
    if all_results.errors:
        print(f"\n{RED}Failed Tests:{RESET}")
        for test_name, reason in all_results.errors:
            print(f"  ✗ {test_name}: {reason}")
    
    if all_results.warnings:
        print(f"\n{YELLOW}Skipped Tests:{RESET}")
        for test_name, reason in all_results.warnings:
            print(f"  ⊘ {test_name}: {reason}")
    
    print(f"\n{BOLD}End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")
    
    return all_results.failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
