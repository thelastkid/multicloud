"""Decision context for policy evaluation."""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from datetime import datetime


@dataclass
class TaskContext:
    """Context information about the task requesting resources."""
    task_id: str
    task_type: str  # training, inference, batch_processing, data_pipeline
    user_id: str
    user_roles: List[str]
    priority: str  # critical, high, medium, low
    requirement: Dict[str, Any]  # gpu_count, cpu_cores, memory_gb, etc.
    budget_limit: Optional[float] = None  # USD
    preferred_regions: List[str] = field(default_factory=lambda: ['us-east-1'])
    required_compliance: List[str] = field(default_factory=list)  # GDPR, HIPAA, etc.
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ResourceContext:
    """Context about available resources across clouds."""
    available_providers: Dict[str, Dict[str, Any]]  # Provider -> resource info
    current_utilization: Dict[str, float]  # Provider -> utilization %
    spot_price_available: bool = True
    current_hour_cost_estimate: float = 0.0


@dataclass
class ComplianceContext:
    """Context about compliance requirements."""
    data_residency_required: Optional[List[str]] = None  # List of allowed regions
    encryption_required: bool = False
    audit_logging_required: bool = False
    pii_data_involved: bool = False


@dataclass
class DecisionContext:
    """Complete context for policy decision-making."""
    task: TaskContext
    resources: ResourceContext
    compliance: ComplianceContext
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for logging."""
        return {
            'task_id': self.task.task_id,
            'task_type': self.task.task_type,
            'priority': self.task.priority,
            'user_id': self.task.user_id,
            'timestamp': self.timestamp.isoformat(),
            'budget_limit': self.task.budget_limit,
            'preferred_regions': self.task.preferred_regions,
        }
