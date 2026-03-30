"""Default policy definitions."""

DEFAULT_POLICIES = [
    {
        'name': 'resource_optimization_policy',
        'type': 'resource_optimization',
        'description': 'Optimize resource allocation for different task types',
        'rules': [
            {
                'name': 'gpu_for_training',
                'condition': "task_type == 'training'",
                'action': 'allocate_gpu',
                'metadata': {'gpu_preferred': True}
            },
            {
                'name': 'cpu_for_inference',
                'condition': "task_type == 'inference'",
                'action': 'allocate_cpu',
                'metadata': {'gpu_preferred': False}
            },
            {
                'name': 'high_memory_for_batch',
                'condition': "task_type == 'batch_processing'",
                'action': 'allocate_high_memory_gpu',
                'metadata': {'min_memory_gb': 64}
            }
        ]
    },
    {
        'name': 'cost_optimization_policy',
        'type': 'cost_management',
        'description': 'Optimize costs across providers and regions',
        'rules': [
            {
                'name': 'use_spot_for_low_priority',
                'condition': "priority in ['low', 'medium']",
                'action': 'use_spot_instances',
                'metadata': {'savings_potential': '70%'}
            },
            {
                'name': 'prefer_cheapest_provider',
                'condition': 'budget_limit > 0',
                'action': 'select_cheapest_provider',
                'metadata': {'multi_cloud': True}
            }
        ]
    },
    {
        'name': 'compliance_policy',
        'type': 'compliance',
        'description': 'Enforce compliance and data residency',
        'rules': [
            {
                'name': 'gdpr_data_residency',
                'condition': "compliance in ['gdpr']",
                'action': 'enforce_eu_region',
                'metadata': {'regions': ['eu-west-1', 'eu-central-1']}
            },
            {
                'name': 'hipaa_encryption',
                'condition': "compliance in ['hipaa']",
                'action': 'require_encryption',
                'metadata': {'encryption_algorithm': 'AES-256'}
            }
        ]
    },
    {
        'name': 'scheduling_policy',
        'type': 'scheduling',
        'description': 'Schedule tasks based on priority',
        'rules': [
            {
                'name': 'immediate_for_critical',
                'condition': "priority == 'critical'",
                'action': 'execute_immediately',
                'metadata': {'max_delay': '5_minutes'}
            },
            {
                'name': 'batch_for_low_priority',
                'condition': "priority == 'low'",
                'action': 'schedule_for_offpeak',
                'metadata': {'target_time': '02:00'}
            }
        ]
    }
]
