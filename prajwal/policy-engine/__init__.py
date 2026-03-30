"""Main application entry point and initialization."""
from typing import Optional, List, Dict, Any

from .core import (
    PolicyEngine,
    DecisionContext,
    TaskContext,
    ResourceContext,
    ComplianceContext,
)
from .modules import (
    ResourceOptimizer,
    CostManager,
    ComplianceEnforcer,
    Scheduler,
)
from .config import DEFAULT_POLICIES
from .utils.logger import get_logger


class MLOpsPolicyEngine:
    """Main entry point for the MLOps Policy Engine."""
    
    def __init__(self, policies: Optional[List[Dict[str, Any]]] = None):
        """Initialize the policy engine.
        
        Args:
            policies: Optional custom policy definitions. If None, uses defaults.
        """
        self.logger = get_logger("MLOpsPolicyEngine")
        
        # Initialize core engine with policies
        policy_list = policies if policies is not None else DEFAULT_POLICIES
        self.engine = PolicyEngine(policy_list)
        
        # Initialize and register modules
        self._initialize_modules()
        
        self.logger.info("MLOps Policy Engine initialized successfully")
    
    def _initialize_modules(self) -> None:
        """Initialize and register policy modules."""
        # Resource optimization
        resource_optimizer = ResourceOptimizer()
        self.engine.set_resource_optimizer(resource_optimizer)
        
        # Cost management
        cost_manager = CostManager()
        self.engine.set_cost_manager(cost_manager)
        
        # Compliance enforcement
        compliance_enforcer = ComplianceEnforcer()
        self.engine.set_compliance_enforcer(compliance_enforcer)
        
        # Task scheduling
        scheduler = Scheduler()
        self.engine.set_scheduler(scheduler)
        
        self.logger.info("All policy modules registered")
    
    def evaluate_task(
        self,
        task_id: str,
        task_type: str,
        user_id: str,
        user_roles: List[str],
        priority: str,
        requirement: Dict[str, Any],
        budget_limit: Optional[float] = None,
        preferred_regions: Optional[List[str]] = None,
        required_compliance: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Evaluate a task against all policies.
        
        Args:
            task_id: Unique task identifier
            task_type: Type of task (training, inference, batch_processing, data_pipeline)
            user_id: ID of the user/service requesting resources
            user_roles: Roles of the user (for access control)
            priority: Priority level (critical, high, medium, low)
            requirement: Resource requirements (gpu_count, cpu_cores, memory_gb, etc.)
            budget_limit: Optional budget limit in USD
            preferred_regions: Optional list of preferred AWS/GCP/Azure regions
            required_compliance: Optional list of compliance frameworks (GDPR, HIPAA, etc.)
            **kwargs: Additional context
        
        Returns:
            Dictionary with policy decision and recommendations
        """
        # Build decision context
        task_context = TaskContext(
            task_id=task_id,
            task_type=task_type,
            user_id=user_id,
            user_roles=user_roles,
            priority=priority,
            requirement=requirement,
            budget_limit=budget_limit,
            preferred_regions=preferred_regions or ['us-east-1'],
            required_compliance=required_compliance or [],
        )
        
        resource_context = ResourceContext(
            available_providers={
                'aws': {'regions': ['us-east-1', 'us-west-2', 'eu-west-1']},
                'gcp': {'regions': ['us-central1', 'europe-west1']},
                'azure': {'regions': ['eastus', 'westeurope']},
            },
            current_utilization={'aws': 0.6, 'gcp': 0.4, 'azure': 0.5},
        )
        
        compliance_context = ComplianceContext(
            data_residency_required=preferred_regions,
            encryption_required='encrypted' in kwargs.get('security_requirements', []),
            audit_logging_required='audit_logging' in kwargs.get('security_requirements', []),
            pii_data_involved=kwargs.get('pii_data_involved', False),
        )
        
        decision_context = DecisionContext(
            task=task_context,
            resources=resource_context,
            compliance=compliance_context,
        )
        
        # Evaluate policies
        policy_decision = self.engine.evaluate(decision_context)
        
        return policy_decision.to_dict()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics from policy decisions."""
        return self.engine.get_metrics()
    
    def list_policies(self) -> List[str]:
        """List all registered policies."""
        return self.engine.list_policies()
    
    def get_policy(self, name: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific policy."""
        return self.engine.get_policy(name)
