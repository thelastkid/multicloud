"""Cost management module for multi-cloud optimization."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from core.decision_context import DecisionContext
from utils.logger import get_logger


class CloudProvider(Enum):
    """Supported cloud providers."""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"


@dataclass
class CloudPricing:
    """Pricing information for a cloud provider."""
    provider: CloudProvider
    region: str
    on_demand_hourly_rate: float  # USD
    spot_hourly_rate: Optional[float]  # USD, None if spot not available
    spot_availability: float  # 0-1 probability
    
    def get_effective_rate(self, use_spot: bool = False) -> float:
        """Get effective hourly rate."""
        if use_spot and self.spot_hourly_rate:
            return self.spot_hourly_rate
        return self.on_demand_hourly_rate


class CostManager:
    """Manage costs across multiple cloud providers."""
    
    def __init__(self):
        self.logger = get_logger("CostManager")
        self.provider_pricing: Dict[str, List[CloudPricing]] = {}
        self.budget_tracker: Dict[str, float] = {}  # task_id -> spent_cost
        self._initialize_pricing()
    
    def _initialize_pricing(self) -> None:
        """Initialize sample pricing data."""
        # AWS pricing (simplified)
        self.provider_pricing['aws'] = [
            CloudPricing(
                provider=CloudProvider.AWS,
                region='us-east-1',
                on_demand_hourly_rate=3.06,  # p3.2xlarge GPU instance
                spot_hourly_rate=0.92,
                spot_availability=0.95
            ),
            CloudPricing(
                provider=CloudProvider.AWS,
                region='eu-west-1',
                on_demand_hourly_rate=3.47,
                spot_hourly_rate=1.04,
                spot_availability=0.90
            ),
        ]
        
        # GCP pricing (simplified)
        self.provider_pricing['gcp'] = [
            CloudPricing(
                provider=CloudProvider.GCP,
                region='us-central1',
                on_demand_hourly_rate=2.48,  # NVIDIA_L4 GPU
                spot_hourly_rate=0.74,
                spot_availability=0.98
            ),
        ]
        
        # Azure pricing (simplified)
        self.provider_pricing['azure'] = [
            CloudPricing(
                provider=CloudProvider.AZURE,
                region='eastus',
                on_demand_hourly_rate=3.18,
                spot_hourly_rate=0.95,
                spot_availability=0.92
            ),
        ]
    
    def optimize(self, context: DecisionContext) -> Dict[str, Any]:
        """Optimize cloud provider and instance type for cost.
        
        Returns:
            Dict with recommended provider, instance type, and estimated cost
        """
        task = context.task
        required_regions = context.task.preferred_regions
        
        action = {
            'module': 'cost_manager',
            'optimization_type': 'cost_minimization',
        }
        
        # Find cheapest option across providers and regions
        best_option = self._find_cheapest_option(
            required_regions,
            task.budget_limit,
            context
        )
        
        if best_option:
            action['recommended_provider'] = best_option['provider']
            action['recommended_region'] = best_option['region']
            action['use_spot_instance'] = best_option.get('use_spot', False)
            action['estimated_cost_usd'] = best_option['estimated_cost']
            action['savings_vs_on_demand'] = best_option.get('savings', 0)
            
            self.logger.info(
                f"Cost optimization for {task.task_id}: "
                f"{best_option['provider']} in {best_option['region']} "
                f"(${best_option['estimated_cost']:.2f}/hour)"
            )
        else:
            action['error'] = 'No cost-acceptable option found within budget'
            self.logger.warning(f"Task {task.task_id}: No cost-acceptable option in budget")
        
        return action
    
    def _find_cheapest_option(
        self,
        required_regions: List[str],
        budget_limit: Optional[float],
        context: DecisionContext
    ) -> Optional[Dict[str, Any]]:
        """Find cheapest provider/region combination."""
        best = None
        best_cost = float('inf')
        
        for provider, pricing_list in self.provider_pricing.items():
            for pricing in pricing_list:
                # Check region match
                if pricing.region not in required_regions and required_regions:
                    continue
                
                # Try spot first if available
                if pricing.spot_hourly_rate:
                    estimated_cost = pricing.spot_hourly_rate
                    savings = pricing.on_demand_hourly_rate - pricing.spot_hourly_rate
                    
                    if budget_limit is None or estimated_cost <= budget_limit:
                        if estimated_cost < best_cost:
                            best_cost = estimated_cost
                            best = {
                                'provider': provider,
                                'region': pricing.region,
                                'use_spot': True,
                                'estimated_cost': estimated_cost,
                                'savings': savings,
                            }
                
                # Try on-demand
                estimated_cost = pricing.on_demand_hourly_rate
                if budget_limit is None or estimated_cost <= budget_limit:
                    if estimated_cost < best_cost:
                        best_cost = estimated_cost
                        best = {
                            'provider': provider,
                            'region': pricing.region,
                            'use_spot': False,
                            'estimated_cost': estimated_cost,
                            'savings': 0,
                        }
        
        return best
    
    def estimate_task_cost(
        self,
        hourly_rate: float,
        duration_hours: float
    ) -> float:
        """Estimate total cost for a task."""
        return hourly_rate * duration_hours
    
    def get_budget_remaining(self, task_id: str, total_budget: float) -> float:
        """Get remaining budget for a task."""
        spent = self.budget_tracker.get(task_id, 0)
        return max(0, total_budget - spent)
    
    def record_cost(self, task_id: str, cost_usd: float) -> None:
        """Record cost spent on a task."""
        self.budget_tracker[task_id] = self.budget_tracker.get(task_id, 0) + cost_usd
        self.logger.debug(f"Recorded ${cost_usd:.2f} cost for task {task_id}")
