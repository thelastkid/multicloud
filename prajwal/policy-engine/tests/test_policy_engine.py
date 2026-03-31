"""Unit tests for policy engine."""
import pytest
from datetime import datetime

from policy_engine.core import (
    PolicyEngine,
    DecisionContext,
    TaskContext,
    ResourceContext,
    ComplianceContext,
    DecisionStatus,
)
from policy_engine.modules import ResourceOptimizer, CostManager
from policy_engine.config import DEFAULT_POLICIES
from policy_engine.utils.validators import ResourceValidator, ValidationError


class TestResourceValidator:
    """Test resource validation."""
    
    def test_valid_resource_request(self):
        """Test valid resource request."""
        request = {
            'task_id': 'test-001',
            'task_type': 'training',
            'estimated_duration': 4.0
        }
        assert ResourceValidator.validate_resource_request(request)
    
    def test_missing_required_field(self):
        """Test missing required field."""
        request = {
            'task_id': 'test-001',
            'task_type': 'training'
            # Missing estimated_duration
        }
        with pytest.raises(ValidationError):
            ResourceValidator.validate_resource_request(request)
    
    def test_invalid_task_type(self):
        """Test invalid task type."""
        request = {
            'task_id': 'test-001',
            'task_type': 'invalid_type',
            'estimated_duration': 4.0
        }
        with pytest.raises(ValidationError):
            ResourceValidator.validate_resource_request(request)


class TestResourceOptimizer:
    """Test resource optimization."""
    
    def test_training_task_gpu_allocation(self):
        """Test GPU allocation for training."""
        optimizer = ResourceOptimizer()
        
        task = TaskContext(
            task_id='train-001',
            task_type='training',
            user_id='user1',
            user_roles=['data_scientist'],
            priority='high',
            requirement={'gpu_needed': True, 'memory_gb': 48}
        )
        
        resource_ctx = ResourceContext(
            available_providers={'aws': {}, 'gcp': {}, 'azure': {}},
            current_utilization={}
        )
        
        compliance_ctx = ComplianceContext()
        
        context = DecisionContext(
            task=task,
            resources=resource_ctx,
            compliance=compliance_ctx
        )
        
        result = optimizer.optimize(context)
        assert result['compute_type'] == 'gpu'
        assert result['gpu_count'] > 0
    
    def test_inference_task_cpu_allocation(self):
        """Test CPU allocation for inference."""
        optimizer = ResourceOptimizer()
        
        task = TaskContext(
            task_id='infer-001',
            task_type='inference',
            user_id='user1',
            user_roles=['ml_engineer'],
            priority='low',
            requirement={'gpu_needed': False, 'cpu_cores': 8}
        )
        
        resource_ctx = ResourceContext(
            available_providers={},
            current_utilization={}
        )
        
        compliance_ctx = ComplianceContext()
        
        context = DecisionContext(
            task=task,
            resources=resource_ctx,
            compliance=compliance_ctx
        )
        
        result = optimizer.optimize(context)
        assert result['compute_type'] == 'cpu'
        assert result['gpu_count'] == 0


class TestCostManager:
    """Test cost management."""
    
    def test_find_cheapest_option(self):
        """Test finding cheapest provider option."""
        manager = CostManager()
        
        task = TaskContext(
            task_id='cost-001',
            task_type='inference',
            user_id='user1',
            user_roles=['ml_engineer'],
            priority='low',
            requirement={},
            budget_limit=10.0,
            preferred_regions=['us-east-1']
        )
        
        resource_ctx = ResourceContext(
            available_providers={},
            current_utilization={}
        )
        
        compliance_ctx = ComplianceContext()
        
        context = DecisionContext(
            task=task,
            resources=resource_ctx,
            compliance=compliance_ctx
        )
        
        result = manager.optimize(context)
        assert 'recommended_provider' in result
        assert 'estimated_cost_usd' in result


class TestPolicyEngine:
    """Test policy engine."""
    
    def test_policy_registration(self):
        """Test policy registration."""
        engine = PolicyEngine(DEFAULT_POLICIES)
        policies = engine.list_policies()
        
        assert len(policies) > 0
        assert 'resource_optimization_policy' in policies
        assert 'cost_optimization_policy' in policies
    
    def test_evaluation_with_valid_context(self):
        """Test evaluation with valid context."""
        engine = PolicyEngine(DEFAULT_POLICIES)
        
        task = TaskContext(
            task_id='test-001',
            task_type='training',
            user_id='user1',
            user_roles=['data_scientist'],
            priority='high',
            requirement={'gpu_needed': True, 'memory_gb': 32}
        )
        
        resource_ctx = ResourceContext(
            available_providers={},
            current_utilization={}
        )
        
        compliance_ctx = ComplianceContext()
        
        context = DecisionContext(
            task=task,
            resources=resource_ctx,
            compliance=compliance_ctx
        )
        
        # This will fail without modules registered, but tests the basic flow
        decision = engine.evaluate(context)
        assert decision.task_id == 'test-001'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
