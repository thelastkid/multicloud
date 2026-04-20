"""Resource optimization module for GPU/CPU/Memory allocation."""
from typing import Dict, Any, Tuple
from dataclasses import dataclass

from core.decision_context import DecisionContext
from utils.logger import get_logger


@dataclass
class ResourceRecommendation:
    """Recommended resource allocation."""
    compute_type: str  # 'gpu', 'cpu', 'mixed'
    gpu_type: str  # 'v100', 'a100', 'rtx_a6000', etc.
    gpu_count: int
    cpu_cores: int
    memory_gb: float
    instance_type: str  # AWS/GCP instance name
    estimated_throughput: float  # tasks/hour


class ResourceOptimizer:
    """Optimize resource allocation for different task types."""
    
    def __init__(self):
        self.logger = get_logger("ResourceOptimizer")
        # Define compute profiles for different task types
        self.profiles = self._initialize_profiles()
    
    def _initialize_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Initialize predefined compute profiles."""
        return {
            'training': {
                'prefers_gpu': True,
                'min_memory_gb': 16,
                'recommended_memory_gb': 32,
                'min_gpu_count': 1,
                'recommended_gpu_count': 2,
                'gpu_preference': ['a100', 'v100', 'h100'],  # In order of preference
                'cpu_backup': {
                    'cpu_cores': 16,
                    'memory_gb': 64,
                    'throughput_multiplier': 0.3  # 30% of GPU throughput
                }
            },
            'inference': {
                'prefers_gpu': False,  # Inference can be on CPU typically
                'min_memory_gb': 4,
                'recommended_memory_gb': 8,
                'gpu_count': 0,
                'cpu_cores': 8,
                'gpu_preference': ['t4', 'rtx_a6000'],  # Cheaper GPUs if used
            },
            'batch_processing': {
                'prefers_gpu': True,
                'min_memory_gb': 32,
                'recommended_memory_gb': 64,
                'min_gpu_count': 2,
                'recommended_gpu_count': 4,
                'gpu_preference': ['a100', 'v100'],
                'cpu_backup_allowed': False
            },
            'data_pipeline': {
                'prefers_gpu': False,
                'min_memory_gb': 8,
                'recommended_memory_gb': 16,
                'cpu_cores': 32,  # I/O intensive
                'gpu_needed': False,
            }
        }
    
    def optimize(self, context: DecisionContext) -> Dict[str, Any]:
        """Optimize resource allocation for a task.
        
        Returns:
            Dict with recommended resources and routing
        """
        task = context.task
        requirement = task.requirement
        
        profile = self.profiles.get(task.task_type)
        if not profile:
            self.logger.warning(f"Unknown task type: {task.task_type}, using default profile")
            profile = self._default_profile()
        
        # Analyze requirement
        gpu_needed = requirement.get('gpu_needed', profile.get('prefers_gpu', False))
        memory_gb = requirement.get('memory_gb', profile.get('recommended_memory_gb', 8))
        
        action = {
            'module': 'resource_optimizer',
            'optimization_type': 'resource_allocation',
        }
        
        # Determine target cluster based on task type and GPU requirement
        cluster_routing = self._determine_cluster_routing(task.task_type, gpu_needed)
        action['cluster'] = cluster_routing['cluster']
        action['cluster_description'] = cluster_routing['description']
        
        if gpu_needed:
            # GPU path
            gpu_count = requirement.get('gpu_count', profile.get('recommended_gpu_count', 1))
            gpu_type = self._select_gpu_type(gpu_count, profile, memory_gb)
            
            action['compute_type'] = 'gpu'
            action['gpu_type'] = gpu_type
            action['gpu_count'] = gpu_count
            action['memory_gb'] = memory_gb
            action['cpu_cores'] = requirement.get('cpu_cores', 8)
            action['recommendation'] = f"Use {gpu_count}x {gpu_type} GPU(s) with {memory_gb}GB memory"
            
            self.logger.info(
                f"Optimized task {task.task_id}: {action['recommendation']}"
            )
        else:
            # CPU path
            cpu_cores = requirement.get('cpu_cores', profile.get('cpu_cores', 8))
            
            action['compute_type'] = 'cpu'
            action['gpu_count'] = 0
            action['cpu_cores'] = cpu_cores
            action['memory_gb'] = memory_gb
            action['recommendation'] = f"Use CPU with {cpu_cores} cores and {memory_gb}GB memory"
            
            self.logger.info(f"Optimized task {task.task_id}: {action['recommendation']}")
        
        # Calculate estimated throughput
        action['estimated_throughput'] = self._estimate_throughput(action, profile)
        
        return action
    
    def _select_gpu_type(self, gpu_count: int, profile: Dict[str, Any], memory_gb: float) -> str:
        """Select the best GPU type based on requirements."""
        # This is a simplified selection - could be enhanced with cost/perf tradeoffs
        preferences = profile.get('gpu_preference', ['v100', 'a100'])
        
        # If requesting more memory, prefer A100
        if memory_gb > 32:
            return 'a100'  # A100 has 80GB memory
        
        # Return first preference as default
        return preferences[0] if preferences else 'v100'
    
    def _estimate_throughput(self, allocation: Dict[str, Any], profile: Dict[str, Any]) -> float:
        """Estimate task throughput per hour."""
        if allocation['compute_type'] == 'gpu':
            base_throughput = 100  # baseline tasks/hour for single GPU
            gpu_count = allocation.get('gpu_count', 1)
            # Linear scaling with GPU count (simplified)
            return base_throughput * gpu_count
        else:
            # CPU throughput is lower
            cpu_cores = allocation.get('cpu_cores', 8)
            return 10 * (cpu_cores / 8)  # Baseline 10 tasks/hour per 8 cores
    
    @staticmethod
    def _default_profile() -> Dict[str, Any]:
        """Return default profile for unknown task types."""
        return {
            'prefers_gpu': False,
            'min_memory_gb': 4,
            'recommended_memory_gb': 8,
            'cpu_cores': 8,
        }
    
    def _determine_cluster_routing(self, task_type: str, gpu_needed: bool) -> Dict[str, Any]:
        """Determine which cluster should handle this task.
        
        Rules:
        - GPU tasks (training, batch_processing) → training_cluster
        - CPU tasks (inference, data_pipeline) → inference_cluster
        
        Returns:
            Dict with cluster name and description
        """
        if task_type in ['training', 'batch_processing'] or gpu_needed:
            return {
                'cluster': 'training_cluster',
                'description': 'GPU-enabled training cluster optimized for ML model training',
                'cluster_type': 'gpu'
            }
        else:
            return {
                'cluster': 'inference_cluster',
                'description': 'CPU-optimized inference cluster for model serving and inference',
                'cluster_type': 'cpu'
            }
