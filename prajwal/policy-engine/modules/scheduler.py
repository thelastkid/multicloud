"""Task scheduling and prioritization module."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

from core.decision_context import DecisionContext
from core.policy_engine import PolicyDecision
from utils.logger import get_logger


class PriorityLevel(Enum):
    """Task priority levels."""
    CRITICAL = 1  # Immediate execution
    HIGH = 2      # Within 1 hour
    MEDIUM = 3    # Within 4 hours
    LOW = 4       # Batch/overnight


@dataclass
class ScheduledTask:
    """Represents a scheduled task."""
    task_id: str
    priority: PriorityLevel
    scheduled_time: datetime
    estimated_duration_hours: float
    estimated_cost_usd: float


class Scheduler:
    """Schedule tasks based on priority and resource availability."""
    
    def __init__(self):
        self.logger = get_logger("Scheduler")
        self.task_queue: List[ScheduledTask] = []
        self.cost_per_hour = {}  # provider -> cost_per_hour
        self.max_concurrent_tasks = 10
    
    def schedule(
        self,
        context: DecisionContext,
        previous_decision: Optional[PolicyDecision] = None
    ) -> Dict[str, Any]:
        """Schedule a task based on priority and availability.
        
        Returns:
            Dict with scheduling recommendation
        """
        task = context.task
        priority = self._parse_priority(task.priority)
        
        action = {
            'module': 'scheduler',
            'optimization_type': 'task_scheduling',
            'priority_level': priority.name,
        }
        
        # Determine optimal execution time
        scheduled_time = self._determine_execution_time(priority, task.budget_limit)
        action['scheduled_start_time'] = scheduled_time.isoformat()
        
        # Calculate queue position
        queue_position = self._get_queue_position(priority)
        action['queue_position'] = queue_position
        
        # Suggest cost optimization time window if low priority
        if priority in [PriorityLevel.LOW, PriorityLevel.MEDIUM]:
            optimal_hours = self._find_optimal_cost_window(task.estimated_duration)
            action['optimal_cost_hours'] = optimal_hours
            action['notice'] = f"Run during {optimal_hours} for 30%+ cost savings"
        
        self.logger.info(
            f"Scheduled task {task.task_id} with priority {priority.name} "
            f"at {scheduled_time}"
        )
        
        return action
    
    def _parse_priority(self, priority_str: str) -> PriorityLevel:
        """Parse priority string to enum."""
        priority_map = {
            'critical': PriorityLevel.CRITICAL,
            'high': PriorityLevel.HIGH,
            'medium': PriorityLevel.MEDIUM,
            'low': PriorityLevel.LOW,
        }
        return priority_map.get(priority_str.lower(), PriorityLevel.MEDIUM)
    
    def _determine_execution_time(
        self,
        priority: PriorityLevel,
        budget_limit: Optional[float]
    ) -> datetime:
        """Determine when task should execute."""
        now = datetime.now()
        
        if priority == PriorityLevel.CRITICAL:
            # Immediate execution
            return now + timedelta(minutes=5)
        
        elif priority == PriorityLevel.HIGH:
            # Within 1 hour
            return now + timedelta(minutes=30)
        
        elif priority == PriorityLevel.MEDIUM:
            # Within 4 hours - try to hit peak off-hours
            return now + timedelta(hours=2)
        
        else:  # LOW
            # Batch - overnight or weekend
            if now.hour >= 22 or now.hour < 6:
                # Already in off-hours
                return now + timedelta(minutes=30)
            else:
                # Schedule for 2 AM
                tomorrow = now + timedelta(days=1)
                return tomorrow.replace(hour=2, minute=0, second=0)
    
    def _get_queue_position(self, priority: PriorityLevel) -> int:
        """Get position in queue for this priority."""
        same_priority_count = sum(
            1 for t in self.task_queue if t.priority == priority
        )
        return same_priority_count + 1
    
    def _find_optimal_cost_window(self, estimated_duration_hours: float) -> str:
        """Find optimal time window for cost savings."""
        # Simplified: suggest off-peak hours
        current_hour = datetime.now().hour
        
        # Off-peak typically 10 PM - 6 AM
        if current_hour >= 22 or current_hour < 6:
            return "2:00 AM - 4:00 AM (off-peak)"
        else:
            return "2:00 AM - 4:00 AM (off-peak, consider scheduling for next day)"
    
    def add_task(self, task: ScheduledTask) -> None:
        """Add task to scheduling queue."""
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda t: t.priority.value)
        self.logger.debug(f"Added task {task.task_id} to queue")
    
    def get_next_task(self) -> Optional[ScheduledTask]:
        """Get next task to execute."""
        if self.task_queue:
            return self.task_queue[0]
        return None
    
    def complete_task(self, task_id: str) -> bool:
        """Mark task as complete."""
        initial_len = len(self.task_queue)
        self.task_queue = [t for t in self.task_queue if t.task_id != task_id]
        
        if len(self.task_queue) < initial_len:
            self.logger.info(f"Completed task {task_id}")
            return True
        return False
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        priority_breakdown = {}
        for priority in PriorityLevel:
            count = sum(1 for t in self.task_queue if t.priority == priority)
            if count > 0:
                priority_breakdown[priority.name] = count
        
        return {
            'total_queued': len(self.task_queue),
            'by_priority': priority_breakdown,
            'next_task_id': self.task_queue[0].task_id if self.task_queue else None,
        }
