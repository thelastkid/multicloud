"""REST API for policy engine."""
from flask import Flask, request, jsonify
from typing import Dict, Any
import logging

from . import MLOpsPolicyEngine
from ..utils.logger import get_logger
from ..utils.request_validator import RequestValidator
from ..modules.deployment_connector import DeploymentConnector


class PolicyEngineAPI:
    """REST API for the policy engine."""
    
    def __init__(self, port: int = 5000):
        self.app = Flask(__name__)
        self.port = port
        self.engine = MLOpsPolicyEngine()
        self.deployment_connector = DeploymentConnector()
        self.logger = get_logger("PolicyEngineAPI")
        self.validator = RequestValidator()
        
        self._setup_routes()
    
    def _setup_routes(self) -> None:
        """Setup API routes."""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return jsonify({'status': 'healthy', 'service': 'MLOps Policy Engine'})
        
        @self.app.route('/api/v1/evaluate', methods=['POST'])
        def evaluate_task():
            """Evaluate a task against policies."""
            try:
                data = request.json
                
                # Validate required fields
                required = ['task_id', 'task_type', 'user_id', 'user_roles', 'priority', 'requirement']
                for field in required:
                    if field not in data:
                        return jsonify({'error': f'Missing required field: {field}'}), 400
                
                # Evaluate task
                decision = self.engine.evaluate_task(
                    task_id=data['task_id'],
                    task_type=data['task_type'],
                    user_id=data['user_id'],
                    user_roles=data['user_roles'],
                    priority=data['priority'],
                    requirement=data['requirement'],
                    budget_limit=data.get('budget_limit'),
                    preferred_regions=data.get('preferred_regions'),
                    required_compliance=data.get('required_compliance'),
                )
                
                return jsonify(decision), 200
            except Exception as e:
                self.logger.error(f"Error evaluating task: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/policies', methods=['GET'])
        def list_policies():
            """List all policies."""
            policies = self.engine.list_policies()
            return jsonify({'policies': policies}), 200
        
        @self.app.route('/api/v1/policies/<policy_name>', methods=['GET'])
        def get_policy(policy_name):
            """Get a specific policy."""
            policy = self.engine.get_policy(policy_name)
            if not policy:
                return jsonify({'error': 'Policy not found'}), 404
            return jsonify({'policy': policy}), 200
        
        @self.app.route('/api/v1/metrics', methods=['GET'])
        def get_metrics():
            """Get engine metrics."""
            metrics = self.engine.get_metrics()
            return jsonify({'metrics': metrics}), 200
        
        @self.app.route('/train', methods=['POST'])
        def train():
            """Submit a training job to the policy engine.
            
            Request body:
            {
                "task_id": "train-001",
                "user_id": "user@company.com",
                "model_name": "my_model",
                "dataset": "training_data_v1",
                "epochs": 100,
                "batch_size": 32,
                "gpu_count": 2,
                "gpu_type": "a100",
                "memory_gb": 48,
                "priority": "high",
                "preferred_regions": ["us-east-1"],
                "budget_limit": 1000
            }
            """
            try:
                data = request.json or {}
                
                # Validate request
                is_valid, error_msg, cleaned_data = self.validator.validate_train_request(data)
                if not is_valid:
                    return jsonify({'error': error_msg}), 400
                
                # Evaluate with policy engine
                policy_decision = self.engine.evaluate_task(
                    task_id=cleaned_data['task_id'],
                    task_type='training',
                    user_id=cleaned_data['user_id'],
                    user_roles=['data_scientist', 'ml_engineer'],
                    priority=cleaned_data['priority'],
                    requirement={
                        'gpu_needed': True,
                        'gpu_count': cleaned_data['gpu_count'],
                        'gpu_type': cleaned_data['gpu_type'],
                        'memory_gb': cleaned_data['memory_gb'],
                        'epochs': cleaned_data['epochs'],
                        'batch_size': cleaned_data['batch_size'],
                    },
                    budget_limit=cleaned_data['budget_limit'],
                    preferred_regions=cleaned_data['preferred_regions'],
                )
                
                # Submit to deployment connector
                deployment_response = self.deployment_connector.submit_training_job({
                    **cleaned_data,
                    **policy_decision
                })
                
                self.logger.info(f"Training job submitted: {cleaned_data['task_id']}")
                
                return jsonify({
                    'success': True,
                    'task_id': cleaned_data['task_id'],
                    'message': 'Training job submitted successfully',
                    'policy_decision': policy_decision,
                    'deployment': deployment_response
                }), 201
                
            except Exception as e:
                self.logger.error(f"Error submitting training job: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/deploy', methods=['POST'])
        def deploy():
            """Submit a model deployment to the policy engine.
            
            Request body:
            {
                "task_id": "deploy-001",
                "user_id": "devops@company.com",
                "model_id": "my_model",
                "model_version": "1.0.0",
                "target_platform": "kubernetes",
                "replicas": 3,
                "cpu_limit": "2",
                "memory_limit": "2Gi",
                "priority": "high",
                "preferred_regions": ["us-east-1"],
                "max_replicas": 10
            }
            """
            try:
                data = request.json or {}
                
                # Validate request
                is_valid, error_msg, cleaned_data = self.validator.validate_deploy_request(data)
                if not is_valid:
                    return jsonify({'error': error_msg}), 400
                
                # Evaluate with policy engine
                policy_decision = self.engine.evaluate_task(
                    task_id=cleaned_data['task_id'],
                    task_type='inference',
                    user_id=cleaned_data['user_id'],
                    user_roles=['devops', 'platform_engineer'],
                    priority=cleaned_data['priority'],
                    requirement={
                        'gpu_needed': False,
                        'cpu_cores': 2,
                        'memory_gb': 2,
                    },
                    preferred_regions=cleaned_data['preferred_regions'],
                )
                
                # Submit to deployment connector
                deployment_response = self.deployment_connector.submit_deployment_job({
                    **cleaned_data,
                    **policy_decision
                })
                
                self.logger.info(f"Deployment submitted: {cleaned_data['task_id']}")
                
                return jsonify({
                    'success': True,
                    'task_id': cleaned_data['task_id'],
                    'message': 'Deployment submitted successfully',
                    'policy_decision': policy_decision,
                    'deployment': deployment_response
                }), 201
                
            except Exception as e:
                self.logger.error(f"Error submitting deployment: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/status/<task_id>', methods=['GET'])
        def get_status(task_id):
            """Get the status of a training or deployment task.
            
            Path parameters:
                task_id: The task ID to query
            """
            try:
                # Validate task_id format
                is_valid, error_msg, _ = self.validator.validate_status_request({'task_id': task_id})
                if not is_valid:
                    return jsonify({'error': error_msg}), 400
                
                # Get status from deployment connector
                status_response = self.deployment_connector.get_task_status(task_id)
                
                if not status_response.get('success'):
                    return jsonify(status_response), 404
                
                self.logger.info(f"Status requested for task: {task_id}")
                return jsonify(status_response), 200
                
            except Exception as e:
                self.logger.error(f"Error getting task status: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/status', methods=['POST'])
        def get_status_post():
            """Get the status of a training or deployment task (POST variant).
            
            Request body:
            {
                "task_id": "train-001"
            }
            """
            try:
                data = request.json or {}
                task_id = data.get('task_id')
                
                if not task_id:
                    return jsonify({'error': 'task_id is required'}), 400
                
                # Validate task_id format
                is_valid, error_msg, _ = self.validator.validate_status_request({'task_id': task_id})
                if not is_valid:
                    return jsonify({'error': error_msg}), 400
                
                # Get status from deployment connector
                status_response = self.deployment_connector.get_task_status(task_id)
                
                if not status_response.get('success'):
                    return jsonify(status_response), 404
                
                self.logger.info(f"Status requested for task: {task_id}")
                return jsonify(status_response), 200
                
            except Exception as e:
                self.logger.error(f"Error getting task status: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.errorhandler(404)
        def not_found(e):
            return jsonify({'error': 'Endpoint not found'}), 404
        
        @self.app.errorhandler(500)
        def server_error(e):
            return jsonify({'error': 'Internal server error'}), 500
    
    def run(self, debug: bool = False) -> None:
        """Run the API server."""
        self.logger.info(f"Starting Policy Engine API on port {self.port}")
        self.app.run(host='0.0.0.0', port=self.port, debug=debug)


def create_app() -> Flask:
    """Create Flask app instance."""
    api = PolicyEngineAPI()
    return api.app


if __name__ == '__main__':
    api = PolicyEngineAPI(port=5000)
    api.run(debug=True)
