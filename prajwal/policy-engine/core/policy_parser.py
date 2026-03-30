"""Policy parser for parsing policy definitions."""
import yaml
import re
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass


@dataclass
class PolicyRule:
    """Represents a single policy rule."""
    name: str
    condition: str  # Expression to evaluate
    action: str  # Action to take if condition is true
    metadata: Dict[str, Any]


class PolicyParser:
    """Parse and validate policy definitions."""
    
    def __init__(self):
        self.operators = {
            '==': lambda a, b: a == b,
            '!=': lambda a, b: a != b,
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '>=': lambda a, b: a >= b,
            '<=': lambda a, b: a <= b,
            'in': lambda a, b: a in b,
            'not_in': lambda a, b: a not in b,
            'starts_with': lambda a, b: str(a).startswith(str(b)),
            'contains': lambda a, b: str(b) in str(a),
        }
    
    @staticmethod
    def parse_yaml(policy_content: str) -> Dict[str, Any]:
        """Parse YAML policy file."""
        return yaml.safe_load(policy_content)
    
    @staticmethod
    def parse_json(policy_content: str) -> Dict[str, Any]:
        """Parse JSON policy file."""
        import json
        return json.loads(policy_content)
    
    def parse_rules(self, rules_list: List[Dict[str, Any]]) -> List[PolicyRule]:
        """Parse rules from policy definition."""
        parsed_rules = []
        for rule_dict in rules_list:
            rule = PolicyRule(
                name=rule_dict.get('name', 'unnamed_rule'),
                condition=rule_dict.get('condition', ''),
                action=rule_dict.get('action', ''),
                metadata=rule_dict.get('metadata', {})
            )
            parsed_rules.append(rule)
        return parsed_rules
    
    def evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a condition against context.
        
        Example conditions:
        - "task_type == 'training'"
        - "priority in ['critical', 'high']"
        - "gpu_count > 0"
        - "budget_limit >= 100.0"
        """
        try:
            condition = condition.strip()
            
            # Handle simple equality
            if '==' in condition:
                parts = condition.split('==')
                key = parts[0].strip()
                value = parts[1].strip().strip("'\"")
                return context.get(key) == value
            
            # Handle 'in' operator
            if ' in ' in condition:
                match = re.match(r'(\w+)\s+in\s+\[(.*?)\]', condition)
                if match:
                    key = match.group(1)
                    values_str = match.group(2)
                    values = [v.strip().strip("'\"") for v in values_str.split(',')]
                    return context.get(key) in values
            
            # Handle comparison operators
            for op in ['>=', '<=', '!=', '>', '<']:
                if op in condition:
                    parts = condition.split(op)
                    key = parts[0].strip()
                    value = parts[1].strip()
                    try:
                        value = float(value)
                    except:
                        pass
                    return self.operators[op](context.get(key), value)
            
            return False
        except Exception as e:
            raise PolicyParseError(f"Error evaluating condition '{condition}': {str(e)}")
    
    def validate_policy(self, policy: Dict[str, Any]) -> bool:
        """Validate policy structure."""
        if not isinstance(policy, dict):
            raise PolicyParseError("Policy must be a dictionary")
        
        required_keys = {'name', 'type', 'rules'}
        if not required_keys.issubset(policy.keys()):
            raise PolicyParseError(f"Policy missing required keys: {required_keys}")
        
        if not isinstance(policy['rules'], list) or len(policy['rules']) == 0:
            raise PolicyParseError("Policy must have at least one rule")
        
        for i, rule in enumerate(policy['rules']):
            if not isinstance(rule, dict):
                raise PolicyParseError(f"Rule {i} must be a dictionary")
            if 'condition' not in rule or 'action' not in rule:
                raise PolicyParseError(f"Rule {i} missing 'condition' or 'action'")
        
        return True


class PolicyParseError(Exception):
    """Raised when policy parsing fails."""
    pass
