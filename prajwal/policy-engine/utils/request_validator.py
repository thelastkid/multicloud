"""Request validation utilities for policy engine API."""
from typing import Dict, Any, List, Tuple
import re


class RequestValidator:
    """Validate incoming API requests."""
    
    @staticmethod
    def validate_train_request(data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate a training request.
        
        Args:
            data: Request data
            
        Returns:
            Tuple of (is_valid, error_message, cleaned_data)
        """
        required_fields = ['task_id', 'user_id', 'model_name', 'dataset', 'epochs', 'batch_size']
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                return False, f'Missing required field: {field}', {}
        
        # Validate task_id format (alphanumeric with hyphens)
        if not re.match(r'^[a-zA-Z0-9\-_]+$', str(data['task_id'])):
            return False, 'Invalid task_id format. Use alphanumeric, hyphens, or underscores', {}
        
        # Validate user_id
        if not isinstance(data['user_id'], str) or not data['user_id'].strip():
            return False, 'Invalid user_id', {}
        
        # Validate numeric fields
        try:
            epochs = int(data['epochs'])
            if epochs <= 0 or epochs > 1000:
                return False, 'Epochs must be between 1 and 1000', {}
        except (ValueError, TypeError):
            return False, 'Invalid epochs value (must be integer)', {}
        
        try:
            batch_size = int(data['batch_size'])
            if batch_size <= 0 or batch_size > 10000:
                return False, 'Batch size must be between 1 and 10000', {}
        except (ValueError, TypeError):
            return False, 'Invalid batch_size value (must be integer)', {}
        
        # Optional GPU configuration
        gpu_count = data.get('gpu_count', 1)
        try:
            gpu_count = int(gpu_count)
            if gpu_count < 0 or gpu_count > 8:
                return False, 'GPU count must be between 0 and 8', {}
        except (ValueError, TypeError):
            return False, 'Invalid gpu_count value (must be integer)', {}
        
        # Optional parameters with defaults
        gpu_type = data.get('gpu_type', 'v100')
        if gpu_type not in ['v100', 'a100', 't4', 'h100', 'rtx_a6000']:
            return False, f'Invalid gpu_type. Supported: v100, a100, t4, h100, rtx_a6000', {}
        
        memory_gb = data.get('memory_gb', 32)
        try:
            memory_gb = float(memory_gb)
            if memory_gb < 4 or memory_gb > 256:
                return False, 'Memory must be between 4GB and 256GB', {}
        except (ValueError, TypeError):
            return False, 'Invalid memory_gb value (must be numeric)', {}
        
        priority = data.get('priority', 'normal')
        if priority not in ['low', 'normal', 'high', 'critical']:
            return False, 'Priority must be: low, normal, high, or critical', {}
        
        # Build cleaned data
        cleaned_data = {
            'task_id': str(data['task_id']),
            'user_id': str(data['user_id']),
            'model_name': str(data['model_name']),
            'dataset': str(data['dataset']),
            'epochs': epochs,
            'batch_size': batch_size,
            'gpu_count': gpu_count,
            'gpu_type': gpu_type,
            'memory_gb': memory_gb,
            'priority': priority,
            'preferred_regions': data.get('preferred_regions', ['us-east-1']),
            'budget_limit': data.get('budget_limit', None)
        }
        
        return True, '', cleaned_data
    
    @staticmethod
    def validate_deploy_request(data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate a deployment request.
        
        Args:
            data: Request data
            
        Returns:
            Tuple of (is_valid, error_message, cleaned_data)
        """
        required_fields = ['task_id', 'user_id', 'model_id', 'model_version', 'target_platform']
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                return False, f'Missing required field: {field}', {}
        
        # Validate task_id format
        if not re.match(r'^[a-zA-Z0-9\-_]+$', str(data['task_id'])):
            return False, 'Invalid task_id format. Use alphanumeric, hyphens, or underscores', {}
        
        # Validate user_id
        if not isinstance(data['user_id'], str) or not data['user_id'].strip():
            return False, 'Invalid user_id', {}
        
        # Validate model_id
        if not isinstance(data['model_id'], str) or not data['model_id'].strip():
            return False, 'Invalid model_id', {}
        
        # Validate model_version format (e.g., 1.0.0)
        version = str(data['model_version'])
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            return False, 'Invalid model_version format. Use semantic versioning (x.y.z)', {}
        
        # Validate target_platform
        valid_platforms = ['kubernetes', 'docker', 'serverless', 'edge']
        if data['target_platform'] not in valid_platforms:
            return False, f'Invalid target_platform. Supported: {", ".join(valid_platforms)}', {}
        
        # Validate replicas if provided
        replicas = data.get('replicas', 1)
        try:
            replicas = int(replicas)
            if replicas < 1 or replicas > 100:
                return False, 'Replicas must be between 1 and 100', {}
        except (ValueError, TypeError):
            return False, 'Invalid replicas value (must be integer)', {}
        
        # Optional parameters
        priority = data.get('priority', 'normal')
        if priority not in ['low', 'normal', 'high', 'critical']:
            return False, 'Priority must be: low, normal, high, or critical', {}
        
        # Build cleaned data
        cleaned_data = {
            'task_id': str(data['task_id']),
            'user_id': str(data['user_id']),
            'model_id': str(data['model_id']),
            'model_version': version,
            'target_platform': data['target_platform'],
            'replicas': replicas,
            'priority': priority,
            'max_replicas': data.get('max_replicas', replicas * 2),
            'cpu_limit': data.get('cpu_limit', '2'),
            'memory_limit': data.get('memory_limit', '2Gi'),
            'preferred_regions': data.get('preferred_regions', ['us-east-1']),
        }
        
        return True, '', cleaned_data
    
    @staticmethod
    def validate_status_request(data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate a status request.
        
        Args:
            data: Request data
            
        Returns:
            Tuple of (is_valid, error_message, cleaned_data)
        """
        # task_id can be in body or passed separately
        task_id = data.get('task_id') if isinstance(data, dict) else data
        
        if not task_id:
            return False, 'task_id is required', {}
        
        # Validate task_id format
        if not re.match(r'^[a-zA-Z0-9\-_]+$', str(task_id)):
            return False, 'Invalid task_id format. Use alphanumeric, hyphens, or underscores', {}
        
        cleaned_data = {
            'task_id': str(task_id)
        }
        
        return True, '', cleaned_data
