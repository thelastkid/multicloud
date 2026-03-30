"""Core policy engine implementation."""
import uuid
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum

from .decision_context import DecisionContext, TaskContext, ResourceContext, ComplianceContext
from .policy_parser import PolicyParser, PolicyRule, PolicyParseError
from ..utils.logger import get_logger
from ..utils.metrics import DecisionMetrics, MetricsCollector
from ..utils.validators import ValidationError


class DecisionStatus(Enum):
    """Status of a policy decision."""
    ALLOWED = "allowed"
    DENIED = "denied"
    REDIRECTED = "redirected"
    PENDING = "pending"


class PolicyDecision:
    """Result of policy evaluation."""
    
    def __init__(self, task_id: str, status: DecisionStatus):
        self.decision_id = str(uuid.uuid4())
        self.task_id = task_id
        self.status = status
        self.suggested_action: Dict[str, Any] = {}
        self.applied_policies: List[str] = []
        self.denial_reason: Optional[str] = None
        self.metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert decision to dictionary."""
        return {
            'decision_id': self.decision_id,
            'task_id': self.task_id,
            'status': self.status.value,
            'suggested_action': self.suggested_action,
            'applied_policies': self.applied_policies,
            'denial_reason': self.denial_reason,
            'metadata': self.metadata,
        }


class PolicyEngine:
    """Core policy engine for making resource and compliance decisions."""
    
    def __init__(self, policies: Optional[List[Dict[str, Any]]] = None):
        self.logger = get_logger("PolicyEngine")
        self.parser = PolicyParser()
        self.metrics = MetricsCollector()
        self.policies: Dict[str, List[PolicyRule]] = {}
        
        # Register policy modules
        self.resource_optimizer = None
        self.cost_manager = None
        self.compliance_enforcer = None
        self.scheduler = None
        
        if policies:
            for policy in policies:
                self.register_policy(policy)
        
        self.logger.info("PolicyEngine initialized")
    
    def register_policy(self, policy: Dict[str, Any]) -> None:
        """Register a new policy."""
        try:
            self.parser.validate_policy(policy)
            policy_type = policy['type']
            policy_name = policy['name']
            
            rules = self.parser.parse_rules(policy.get('rules', []))
            self.policies[policy_name] = rules
            
            self.logger.info(f"Registered policy '{policy_name}' of type '{policy_type}' with {len(rules)} rules")
        except PolicyParseError as e:
            self.logger.error(f"Failed to register policy: {str(e)}")
            raise
    
    def evaluate(self, context: DecisionContext) -> PolicyDecision:
        """Evaluate policies against decision context.
        
        This is the main entry point for policy evaluation.
        Returns a PolicyDecision with the result.
        """
        start_time = time.time()
        decision = PolicyDecision(context.task.task_id, DecisionStatus.PENDING)
        
        try:
            self.logger.info(f"Evaluating policies for task {context.task.task_id}")
            
            # Step 1: Compliance check first (must-have)
            if not self._check_compliance(context, decision):
                decision.status = DecisionStatus.DENIED
                decision.denial_reason = "Failed compliance checks"
                return decision
            
            # Step 2: Resource optimization
            if self.resource_optimizer:
                resource_action = self.resource_optimizer.optimize(context)
                decision.suggested_action.update(resource_action)
            
            # Step 3: Cost management
            if self.cost_manager:
                cost_action = self.cost_manager.optimize(context)
                decision.suggested_action.update(cost_action)
                
                # Check budget constraint
                if not self._check_budget(context, decision):
                    decision.status = DecisionStatus.DENIED
                    decision.denial_reason = "Budget limit exceeded"
                    return decision
            
            # Step 4: Scheduling
            if self.scheduler:
                scheduling_action = self.scheduler.schedule(context, decision)
                decision.suggested_action.update(scheduling_action)
            
            decision.status = DecisionStatus.ALLOWED
            
            # Record metrics
            self._record_metrics(context, decision, start_time)
            
            self.logger.info(f"Decision for task {context.task.task_id}: {decision.status.value}")
            return decision
            
        except Exception as e:
            self.logger.error(f"Error evaluating policies: {str(e)}")
            decision.status = DecisionStatus.DENIED
            decision.denial_reason = f"Evaluation error: {str(e)}"
            return decision
    
    def _check_compliance(self, context: DecisionContext, decision: PolicyDecision) -> bool:
        """Check compliance requirements."""
        if not self.compliance_enforcer:
            return True
        
        try:
            is_compliant = self.compliance_enforcer.validate(context)
            if not is_compliant:
                decision.denial_reason = "Compliance validation failed"
            return is_compliant
        except Exception as e:
            self.logger.warning(f"Compliance check error: {str(e)}")
            return False
    
    def _check_budget(self, context: DecisionContext, decision: PolicyDecision) -> bool:
        """Check if decision is within budget."""
        if context.task.budget_limit is None:
            return True
        
        estimated_cost = decision.suggested_action.get('estimated_cost_usd', 0)
        if estimated_cost > context.task.budget_limit:
            self.logger.warning(
                f"Task {context.task.task_id} estimated cost {estimated_cost} "
                f"exceeds budget {context.task.budget_limit}"
            )
            return False
        return True
    
    def _record_metrics(self, context: DecisionContext, decision: PolicyDecision, start_time: float) -> None:
        """Record decision metrics."""
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        
        metric = DecisionMetrics(
            decision_id=decision.decision_id,
            timestamp=datetime.now(),
            policy_type='general',
            task_id=context.task.task_id,
            suggested_resource=decision.suggested_action,
            applied_policy=','.join(decision.applied_policies) or 'default',
            execution_time_ms=execution_time,
            status=decision.status.value,
        )
        self.metrics.record(metric)
    
    def get_policy(self, name: str) -> Optional[List[PolicyRule]]:
        """Get a registered policy by name."""
        return self.policies.get(name)
    
    def list_policies(self) -> List[str]:
        """List all registered policies."""
        return list(self.policies.keys())
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics."""
        return self.metrics.get_summary()
    
    def set_resource_optimizer(self, optimizer: 'ResourceOptimizer') -> None:
        """Set resource optimizer module."""
        self.resource_optimizer = optimizer
        self.logger.info("Resource optimizer registered")
    
    def set_cost_manager(self, manager: 'CostManager') -> None:
        """Set cost manager module."""
        self.cost_manager = manager
        self.logger.info("Cost manager registered")
    
    def set_compliance_enforcer(self, enforcer: 'ComplianceEnforcer') -> None:
        """Set compliance enforcer module."""
        self.compliance_enforcer = enforcer
        self.logger.info("Compliance enforcer registered")
    
    def set_scheduler(self, scheduler: 'Scheduler') -> None:
        """Set scheduler module."""
        self.scheduler = scheduler
        self.logger.info("Scheduler registered")
