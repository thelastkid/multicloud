"""
Comprehensive examples and tests for the Policy Engine API.
Demonstrates training, deployment, and status checking workflows.
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:5000"

# Color codes for output
GREEN = '\033[92m'
BLUE = '\033[94m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def print_section(title):
    """Print a formatted section title."""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{title:^80}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")


def print_request(method, endpoint, data=None):
    """Print the request being made."""
    print(f"{YELLOW}➜ {method} {endpoint}{RESET}")
    if data:
        print(f"{YELLOW}Body:{RESET}\n{json.dumps(data, indent=2)}\n")


def print_response(response):
    """Print the response."""
    try:
        resp_data = response.json()
    except:
        resp_data = response.text
    
    status_color = GREEN if response.status_code < 300 else RED
    print(f"{status_color}← Status: {response.status_code}{RESET}")
    print(f"{status_color}Response:{RESET}\n{json.dumps(resp_data, indent=2)}\n")
    
    return resp_data


class PolicyEngineTestSuite:
    """Test suite for policy engine API."""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.tasks = {}
    
    def test_health_check(self):
        """Test 1: Health Check"""
        print_section("TEST 1: Health Check")
        
        endpoint = f"{self.base_url}/health"
        print_request("GET", "/health")
        
        response = requests.get(endpoint)
        print_response(response)
        
        assert response.status_code == 200, "Health check failed"
        print(f"{GREEN}✓ Health check passed{RESET}")
    
    def test_training_job_submission(self):
        """Test 2: Training Job Submission"""
        print_section("TEST 2: Training Job Submission")
        
        endpoint = f"{self.base_url}/train"
        
        training_request = {
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
        
        print_request("POST", "/train", training_request)
        response = requests.post(endpoint, json=training_request)
        resp_data = print_response(response)
        
        assert response.status_code == 201, "Training job submission failed"
        assert resp_data.get('success'), "Success flag not set"
        assert resp_data.get('task_id') == "train-gpu-001", "Task ID mismatch"
        
        # Store task ID for status check
        self.tasks['training'] = resp_data.get('task_id')
        
        print(f"{GREEN}✓ Training job submitted successfully{RESET}")
        print(f"{GREEN}✓ Task routed to: {resp_data.get('policy_decision', {}).get('cluster', 'unknown')}{RESET}")
    
    def test_training_validation_errors(self):
        """Test 3: Training Request Validation"""
        print_section("TEST 3: Training Request Validation - Error Cases")
        
        endpoint = f"{self.base_url}/train"
        
        # Test missing required fields
        print(f"{YELLOW}Testing missing task_id...{RESET}")
        bad_request = {
            "user_id": "user@company.com",
            "model_name": "model",
            "dataset": "data",
            "epochs": 100
        }
        
        print_request("POST", "/train", bad_request)
        response = requests.post(endpoint, json=bad_request)
        resp_data = print_response(response)
        
        assert response.status_code == 400, "Should return 400 for missing fields"
        print(f"{GREEN}✓ Validation error caught correctly{RESET}")
        
        # Test invalid epochs
        print(f"{YELLOW}Testing invalid epochs (> 1000)...{RESET}")
        bad_request = {
            "task_id": "train-001",
            "user_id": "user@company.com",
            "model_name": "model",
            "dataset": "data",
            "epochs": 5000,
            "batch_size": 32
        }
        
        print_request("POST", "/train", bad_request)
        response = requests.post(endpoint, json=bad_request)
        resp_data = print_response(response)
        
        assert response.status_code == 400, "Should validate epoch range"
        print(f"{GREEN}✓ Epoch validation working correctly{RESET}")
    
    def test_deployment_submission(self):
        """Test 4: Model Deployment Submission"""
        print_section("TEST 4: Model Deployment Submission")
        
        endpoint = f"{self.base_url}/deploy"
        
        deployment_request = {
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
        
        print_request("POST", "/deploy", deployment_request)
        response = requests.post(endpoint, json=deployment_request)
        resp_data = print_response(response)
        
        assert response.status_code == 201, "Deployment submission failed"
        assert resp_data.get('success'), "Success flag not set"
        assert resp_data.get('task_id') == "deploy-inf-001", "Task ID mismatch"
        
        # Store task ID for status check
        self.tasks['deployment'] = resp_data.get('task_id')
        
        print(f"{GREEN}✓ Deployment submitted successfully{RESET}")
        print(f"{GREEN}✓ Task routed to: {resp_data.get('policy_decision', {}).get('cluster', 'unknown')}{RESET}")
    
    def test_deployment_validation_errors(self):
        """Test 5: Deployment Request Validation"""
        print_section("TEST 5: Deployment Request Validation - Error Cases")
        
        endpoint = f"{self.base_url}/deploy"
        
        # Test invalid model_version format
        print(f"{YELLOW}Testing invalid model_version (not semantic)...{RESET}")
        bad_request = {
            "task_id": "deploy-001",
            "user_id": "devops@company.com",
            "model_id": "model",
            "model_version": "latest",
            "target_platform": "kubernetes"
        }
        
        print_request("POST", "/deploy", bad_request)
        response = requests.post(endpoint, json=bad_request)
        resp_data = print_response(response)
        
        assert response.status_code == 400, "Should validate semantic versioning"
        print(f"{GREEN}✓ Version validation working correctly{RESET}")
        
        # Test invalid target_platform
        print(f"{YELLOW}Testing invalid target_platform...{RESET}")
        bad_request = {
            "task_id": "deploy-002",
            "user_id": "devops@company.com",
            "model_id": "model",
            "model_version": "1.0.0",
            "target_platform": "invalid_platform"
        }
        
        print_request("POST", "/deploy", bad_request)
        response = requests.post(endpoint, json=bad_request)
        resp_data = print_response(response)
        
        assert response.status_code == 400, "Should validate platform"
        print(f"{GREEN}✓ Platform validation working correctly{RESET}")
    
    def test_status_check_get(self):
        """Test 6: Status Check via GET"""
        print_section("TEST 6: Status Check via GET")
        
        if 'training' not in self.tasks:
            print(f"{YELLOW}Skipping - no training task to check{RESET}")
            return
        
        task_id = self.tasks['training']
        endpoint = f"{self.base_url}/status/{task_id}"
        
        print_request("GET", f"/status/{task_id}")
        response = requests.get(endpoint)
        resp_data = print_response(response)
        
        assert response.status_code == 200, "Status check failed"
        assert resp_data.get('success'), "Success flag not set"
        assert resp_data.get('task_id') == task_id, "Task ID mismatch"
        assert resp_data.get('status') in ['pending', 'running', 'completed', 'failed'], "Invalid status"
        
        print(f"{GREEN}✓ Status check successful{RESET}")
        print(f"{GREEN}✓ Task Status: {resp_data.get('status')}{RESET}")
        print(f"{GREEN}✓ Progress: {resp_data.get('progress', 0)}%{RESET}")
    
    def test_status_check_post(self):
        """Test 7: Status Check via POST"""
        print_section("TEST 7: Status Check via POST")
        
        if 'deployment' not in self.tasks:
            print(f"{YELLOW}Skipping - no deployment task to check{RESET}")
            return
        
        task_id = self.tasks['deployment']
        endpoint = f"{self.base_url}/status"
        
        status_request = {"task_id": task_id}
        
        print_request("POST", "/status", status_request)
        response = requests.post(endpoint, json=status_request)
        resp_data = print_response(response)
        
        assert response.status_code == 200, "Status check failed"
        assert resp_data.get('success'), "Success flag not set"
        assert resp_data.get('task_id') == task_id, "Task ID mismatch"
        
        print(f"{GREEN}✓ Status check successful{RESET}")
        print(f"{GREEN}✓ Task Cluster: {resp_data.get('cluster')}{RESET}")
        print(f"{GREEN}✓ Task Status: {resp_data.get('status')}{RESET}")
    
    def test_invalid_task_status(self):
        """Test 8: Status Check for Non-existent Task"""
        print_section("TEST 8: Status Check - Non-existent Task")
        
        endpoint = f"{self.base_url}/status/nonexistent-task-12345"
        
        print_request("GET", "/status/nonexistent-task-12345")
        response = requests.get(endpoint)
        resp_data = print_response(response)
        
        assert response.status_code == 404, "Should return 404 for non-existent task"
        print(f"{GREEN}✓ Error handling correct for non-existent task{RESET}")
    
    def test_policies_endpoint(self):
        """Test 9: List Policies"""
        print_section("TEST 9: List Policies")
        
        endpoint = f"{self.base_url}/api/v1/policies"
        
        print_request("GET", "/api/v1/policies")
        response = requests.get(endpoint)
        resp_data = print_response(response)
        
        assert response.status_code == 200, "Policies list failed"
        print(f"{GREEN}✓ Policies retrieved successfully{RESET}")
    
    def test_metrics_endpoint(self):
        """Test 10: Get Metrics"""
        print_section("TEST 10: Get Metrics")
        
        endpoint = f"{self.base_url}/api/v1/metrics"
        
        print_request("GET", "/api/v1/metrics")
        response = requests.get(endpoint)
        resp_data = print_response(response)
        
        assert response.status_code == 200, "Metrics retrieval failed"
        print(f"{GREEN}✓ Metrics retrieved successfully{RESET}")
    
    def run_all_tests(self):
        """Run all tests."""
        print_section("Policy Engine API - Comprehensive Test Suite")
        print(f"{BLUE}Running all tests for policy engine endpoints...{RESET}\n")
        
        try:
            self.test_health_check()
            self.test_training_job_submission()
            self.test_training_validation_errors()
            self.test_deployment_submission()
            self.test_deployment_validation_errors()
            self.test_status_check_get()
            self.test_status_check_post()
            self.test_invalid_task_status()
            self.test_policies_endpoint()
            self.test_metrics_endpoint()
            
            print_section("All Tests Completed Successfully!")
            print(f"{GREEN}✓ All 10 tests passed!{RESET}\n")
            
        except AssertionError as e:
            print(f"\n{RED}✗ Test failed: {str(e)}{RESET}")
            return False
        except Exception as e:
            print(f"\n{RED}✗ Error running tests: {str(e)}{RESET}")
            return False
        
        return True


if __name__ == '__main__':
    # Run the test suite
    suite = PolicyEngineTestSuite()
    success = suite.run_all_tests()
    exit(0 if success else 1)
