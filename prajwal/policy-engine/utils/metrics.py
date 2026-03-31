"""Metrics tracking for policy engine decisions."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any
import json


@dataclass
class DecisionMetrics:
    """Track metrics for policy decisions."""
    decision_id: str
    timestamp: datetime
    policy_type: str  # resource_optimization, cost_management, compliance, scheduling
    task_id: str
    suggested_resource: Dict[str, Any]
    applied_policy: str
    execution_time_ms: float
    status: str  # 'allowed', 'denied', 'redirected'
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'decision_id': self.decision_id,
            'timestamp': self.timestamp.isoformat(),
            'policy_type': self.policy_type,
            'task_id': self.task_id,
            'suggested_resource': self.suggested_resource,
            'applied_policy': self.applied_policy,
            'execution_time_ms': self.execution_time_ms,
            'status': self.status,
            'metadata': self.metadata
        }
    
    def to_json(self) -> str:
        """Convert metrics to JSON."""
        return json.dumps(self.to_dict(), default=str)


class MetricsCollector:
    """Collect and aggregate metrics."""
    
    def __init__(self):
        self.metrics: List[DecisionMetrics] = []
        self.policy_counters: Dict[str, int] = {}
        self.status_counters: Dict[str, int] = {}
    
    def record(self, metric: DecisionMetrics) -> None:
        """Record a metric."""
        self.metrics.append(metric)
        
        # Update counters
        self.policy_counters[metric.applied_policy] = \
            self.policy_counters.get(metric.applied_policy, 0) + 1
        self.status_counters[metric.status] = \
            self.status_counters.get(metric.status, 0) + 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        return {
            'total_decisions': len(self.metrics),
            'policy_counters': self.policy_counters,
            'status_counters': self.status_counters,
            'avg_execution_time_ms': self._avg_execution_time(),
        }
    
    def _avg_execution_time(self) -> float:
        """Calculate average execution time."""
        if not self.metrics:
            return 0.0
        total = sum(m.execution_time_ms for m in self.metrics)
        return total / len(self.metrics)
    
    def clear(self) -> None:
        """Clear all metrics."""
        self.metrics.clear()
        self.policy_counters.clear()
        self.status_counters.clear()
