"""Example usage of MLOps Policy Engine."""

import json
from policy_engine import MLOpsPolicyEngine


def example_1_training_task():
    """Example 1: GPU Training Task Optimization"""
    print("=" * 80)
    print("EXAMPLE 1: GPU Training Task - Resource Optimization")
    print("=" * 80)
    
    engine = MLOpsPolicyEngine()
    
    # Training job requiring GPU
    decision = engine.evaluate_task(
        task_id="training-001",
        task_type="training",
        user_id="user123",
        user_roles=["data_scientist", "ml_engineer"],
        priority="high",
        requirement={
            'gpu_needed': True,
            'gpu_count': 2,
            'memory_gb': 48,
            'estimated_duration': 4  # hours
        },
        budget_limit=100.0,
        preferred_regions=['us-east-1', 'us-west-2'],
    )
    
    print("\nDecision Result:")
    print(json.dumps(decision, indent=2))
    print()


def example_2_inference_task():
    """Example 2: CPU-Based Inference - Cost Optimization"""
    print("=" * 80)
    print("EXAMPLE 2: Inference Task - Cost Optimization")
    print("=" * 80)
    
    engine = MLOpsPolicyEngine()
    
    # Inference typically runs on CPU
    decision = engine.evaluate_task(
        task_id="inference-001",
        task_type="inference",
        user_id="service-account-1",
        user_roles=["service", "ml_engineer"],
        priority="low",  # Low priority = use spot instances
        requirement={
            'gpu_needed': False,
            'cpu_cores': 16,
            'memory_gb': 32,
            'estimated_duration': 1
        },
        budget_limit=10.0,
        preferred_regions=['us-east-1'],
    )
    
    print("\nDecision Result:")
    print(json.dumps(decision, indent=2))
    print()


def example_3_batch_processing_gdpr():
    """Example 3: Batch Processing with GDPR Compliance"""
    print("=" * 80)
    print("EXAMPLE 3: Batch Processing - GDPR Compliance")
    print("=" * 80)
    
    engine = MLOpsPolicyEngine()
    
    # Batch processing with EU data (GDPR requirement)
    decision = engine.evaluate_task(
        task_id="batch-001",
        task_type="batch_processing",
        user_id="batch-scheduler",
        user_roles=["service", "data_engineer"],
        priority="medium",
        requirement={
            'gpu_needed': True,
            'gpu_count': 4,
            'memory_gb': 128,
            'estimated_duration': 8
        },
        budget_limit=500.0,
        preferred_regions=['eu-west-1', 'eu-central-1'],  # EU only
        required_compliance=['GDPR'],  # GDPR compliance required
        encryption_required=True,
        security_requirements=['encrypted', 'audit_logging'],
    )
    
    print("\nDecision Result:")
    print(json.dumps(decision, indent=2))
    print()


def example_4_critical_priority():
    """Example 4: Critical Priority Task - Immediate Execution"""
    print("=" * 80)
    print("EXAMPLE 4: Critical Priority - Immediate Execution")
    print("=" * 80)
    
    engine = MLOpsPolicyEngine()
    
    # Critical priority task - should execute immediately
    decision = engine.evaluate_task(
        task_id="critical-001",
        task_type="training",
        user_id="ceo@company.com",
        user_roles=["data_scientist", "admin"],
        priority="critical",  # CRITICAL priority
        requirement={
            'gpu_needed': True,
            'gpu_count': 8,
            'memory_gb': 160,
            'estimated_duration': 2
        },
        budget_limit=2000.0,  # No budget constraints for critical
        preferred_regions=['us-east-1'],
    )
    
    print("\nDecision Result:")
    print(json.dumps(decision, indent=2))
    print()


def example_5_multiple_regions():
    """Example 5: Multi-Cloud Multi-Region Selection"""
    print("=" * 80)
    print("EXAMPLE 5: Multi-Cloud Optimization")
    print("=" * 80)
    
    engine = MLOpsPolicyEngine()
    
    # Task that can run in multiple regions across providers
    decision = engine.evaluate_task(
        task_id="data-pipeline-001",
        task_type="data_pipeline",
        user_id="data-pipeline",
        user_roles=["service"],
        priority="low",
        requirement={
            'gpu_needed': False,
            'cpu_cores': 32,
            'memory_gb': 256,
            'estimated_duration': 12
        },
        budget_limit=50.0,
        preferred_regions=['us-east-1', 'us-west-2', 'eu-west-1'],
        # No strict compliance, so can choose for cost
    )
    
    print("\nDecision Result:")
    print(json.dumps(decision, indent=2))
    print()


def example_6_metrics():
    """Example 6: View Policy Engine Metrics"""
    print("=" * 80)
    print("EXAMPLE 6: Policy Engine Metrics")
    print("=" * 80)
    
    engine = MLOpsPolicyEngine()
    
    # Run a few evaluations first
    for i in range(3):
        engine.evaluate_task(
            task_id=f"task-{i}",
            task_type="training" if i % 2 == 0 else "inference",
            user_id="test-user",
            user_roles=["data_scientist"],
            priority="high",
            requirement={'gpu_needed': i % 2 == 0, 'cpu_cores': 8, 'memory_gb': 32},
        )
    
    # Get metrics
    metrics = engine.get_metrics()
    
    print("\nEngine Metrics:")
    print(json.dumps(metrics, indent=2))
    print()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("MLOps Policy Engine - Usage Examples")
    print("=" * 80 + "\n")
    
    # Run all examples
    example_1_training_task()
    example_2_inference_task()
    example_3_batch_processing_gdpr()
    example_4_critical_priority()
    example_5_multiple_regions()
    example_6_metrics()
    
    print("=" * 80)
    print("Examples completed successfully!")
    print("=" * 80)
