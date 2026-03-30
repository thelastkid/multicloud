"""Command-line interface for policy engine."""
import click
import json
import sys
from typing import Dict, Any
from tabulate import tabulate

from . import MLOpsPolicyEngine
from ..utils.logger import get_logger


@click.group()
def cli():
    """MLOps Policy Engine CLI."""
    pass


@cli.command()
@click.option('--task-id', required=True, help='Unique task identifier')
@click.option('--task-type', required=True, type=click.Choice(['training', 'inference', 'batch_processing', 'data_pipeline']), help='Type of task')
@click.option('--user-id', required=True, help='User/service ID')
@click.option('--priority', required=True, type=click.Choice(['critical', 'high', 'medium', 'low']), help='Task priority')
@click.option('--gpu-count', type=int, default=0, help='Number of GPUs required')
@click.option('--cpu-cores', type=int, default=8, help='Number of CPU cores')
@click.option('--memory-gb', type=float, default=32, help='Memory in GB')
@click.option('--budget', type=float, default=None, help='Budget limit in USD')
@click.option('--region', multiple=True, default=['us-east-1'], help='Preferred regions')
@click.option('--compliance', multiple=True, default=[], help='Compliance requirements')
def evaluate(task_id, task_type, user_id, priority, gpu_count, cpu_cores, memory_gb, budget, region, compliance):
    """Evaluate a task against policies."""
    try:
        engine = MLOpsPolicyEngine()
        
        requirement = {
            'gpu_count': gpu_count,
            'cpu_cores': cpu_cores,
            'memory_gb': memory_gb,
            'gpu_needed': gpu_count > 0,
        }
        
        decision = engine.evaluate_task(
            task_id=task_id,
            task_type=task_type,
            user_id=user_id,
            user_roles=['ml_engineer'],  # Default role
            priority=priority,
            requirement=requirement,
            budget_limit=budget,
            preferred_regions=list(region),
            required_compliance=list(compliance),
        )
        
        click.echo(json.dumps(decision, indent=2))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def list_policies():
    """List all registered policies."""
    try:
        engine = MLOpsPolicyEngine()
        policies = engine.list_policies()
        
        click.echo("Registered Policies:")
        for i, policy in enumerate(policies, 1):
            click.echo(f"  {i}. {policy}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--policy-name', required=True, help='Name of the policy')
def show_policy(policy_name):
    """Show details of a specific policy."""
    try:
        engine = MLOpsPolicyEngine()
        policy = engine.get_policy(policy_name)
        
        if not policy:
            click.echo(f"Policy '{policy_name}' not found", err=True)
            sys.exit(1)
        
        click.echo(json.dumps(policy, indent=2))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def metrics():
    """Display policy engine metrics."""
    try:
        engine = MLOpsPolicyEngine()
        metrics_data = engine.get_metrics()
        
        click.echo("Policy Engine Metrics:")
        click.echo(f"  Total Decisions: {metrics_data['total_decisions']}")
        click.echo(f"  Avg Execution Time: {metrics_data['avg_execution_time_ms']:.2f}ms")
        
        if metrics_data.get('policy_counters'):
            click.echo("\n  Policy Usage:")
            for policy, count in metrics_data['policy_counters'].items():
                click.echo(f"    {policy}: {count}")
        
        if metrics_data.get('status_counters'):
            click.echo("\n  Decision Status:")
            for status, count in metrics_data['status_counters'].items():
                click.echo(f"    {status}: {count}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--port', type=int, default=5000, help='API port')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def serve(port, debug):
    """Start the REST API server."""
    from .rest_api import PolicyEngineAPI
    
    try:
        api = PolicyEngineAPI(port=port)
        click.echo(f"Starting Policy Engine API on port {port}...")
        api.run(debug=debug)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
