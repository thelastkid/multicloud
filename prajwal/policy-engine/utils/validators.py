"""Validation utilities for policy engine."""
from typing import Any, Dict, List, Optional
import re


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class ResourceValidator:
    """Validate resource requests."""
    
    @staticmethod
    def validate_resource_request(request: Dict[str, Any]) -> bool:
        """Validate a resource request has required fields."""
        required_fields = ['task_id', 'task_type', 'estimated_duration']
        for field in required_fields:
            if field not in request:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate task_type
        valid_types = ['training', 'inference', 'batch_processing', 'data_pipeline']
        if request['task_type'] not in valid_types:
            raise ValidationError(f"Invalid task_type: {request['task_type']}")
        
        # Validate estimated_duration
        if not isinstance(request['estimated_duration'], (int, float)) or request['estimated_duration'] <= 0:
            raise ValidationError("estimated_duration must be a positive number")
        
        return True
    
    @staticmethod
    def validate_memory_requirement(memory_gb: float) -> bool:
        """Validate memory requirement."""
        if not isinstance(memory_gb, (int, float)):
            raise ValidationError("Memory must be a number")
        if memory_gb <= 0:
            raise ValidationError("Memory must be positive")
        if memory_gb > 1024:  # 1TB max
            raise ValidationError("Memory request exceeds maximum (1TB)")
        return True
    
    @staticmethod
    def validate_budget(budget_usd: float) -> bool:
        """Validate budget amount."""
        if not isinstance(budget_usd, (int, float)):
            raise ValidationError("Budget must be a number")
        if budget_usd < 0:
            raise ValidationError("Budget cannot be negative")
        return True


class ComplianceValidator:
    """Validate compliance requirements."""
    
    @staticmethod
    def validate_data_residency(region: str, allowed_regions: List[str]) -> bool:
        """Validate data residency compliance."""
        if region not in allowed_regions:
            raise ValidationError(f"Region {region} not in allowed regions: {allowed_regions}")
        return True
    
    @staticmethod
    def validate_access_control(user_id: str, required_roles: List[str], user_roles: List[str]) -> bool:
        """Validate user has required roles."""
        for role in required_roles:
            if role not in user_roles:
                raise ValidationError(f"User {user_id} missing required role: {role}")
        return True
    
    @staticmethod
    def validate_sla(priority: str) -> bool:
        """Validate SLA priority level."""
        valid_priorities = ['critical', 'high', 'medium', 'low']
        if priority not in valid_priorities:
            raise ValidationError(f"Invalid priority: {priority}. Must be one of {valid_priorities}")
        return True


class PolicyValidator:
    """Validate policy definitions."""
    
    @staticmethod
    def validate_policy_structure(policy: Dict[str, Any]) -> bool:
        """Validate policy has required structure."""
        required = ['name', 'type', 'rules']
        for field in required:
            if field not in policy:
                raise ValidationError(f"Policy missing required field: {field}")
        
        if not isinstance(policy.get('rules'), list) or len(policy['rules']) == 0:
            raise ValidationError("Policy must have at least one rule")
        
        return True
    
    @staticmethod
    def validate_rule(rule: Dict[str, Any]) -> bool:
        """Validate a single rule."""
        if 'condition' not in rule or 'action' not in rule:
            raise ValidationError("Rule must have 'condition' and 'action'")
        return True
