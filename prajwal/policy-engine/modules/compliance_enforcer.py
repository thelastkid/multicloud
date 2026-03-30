"""Compliance and security enforcement module."""
from typing import Dict, Any, List, Optional
from enum import Enum

from ..core.decision_context import DecisionContext
from ..utils.logger import get_logger


class ComplianceFramework(Enum):
    """Compliance frameworks."""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    CCPA = "ccpa"
    SOC2 = "soc2"
    PCI_DSS = "pci_dss"


class ComplianceEnforcer:
    """Enforce compliance and security policies."""
    
    def __init__(self):
        self.logger = get_logger("ComplianceEnforcer")
        self.compliance_rules = self._initialize_compliance_rules()
        self.allowed_regions: Dict[str, List[str]] = {
            'gdpr': ['eu-west-1', 'eu-central-1', 'eu-north-1'],  # EU regions
            'hipaa': ['us-east-1', 'us-west-2'],  # HIPAA-compliant regions
            'ccpa': ['us-west-1'],  # California region
            's oc2': ['any'],
            'pci_dss': ['any'],
        }
    
    def _initialize_compliance_rules(self) -> Dict[str, Any]:
        """Initialize compliance rules."""
        return {
            'gdpr': {
                'data_residency_required': True,
                'encryption_required': True,
                'audit_logging_required': True,
                'max_data_transfer_regions': 0,
            },
            'hipaa': {
                'encryption_required': True,
                'audit_logging_required': True,
                'access_control_required': True,
                'data_residency_required': True,
            },
            'ccpa': {
                'data_visibility_required': True,
                'encryption_required': True,
                'right_to_deletion': True,
            },
            'soc2': {
                'audit_logging_required': True,
                'access_control_required': True,
            },
        }
    
    def validate(self, context: DecisionContext) -> bool:
        """Validate compliance requirements.
        
        Returns:
            True if all compliance requirements are met
        """
        task = context.task
        compliance_reqs = task.required_compliance
        compliance_ctx = context.compliance
        
        if not compliance_reqs:
            self.logger.debug(f"Task {task.task_id}: No compliance requirements")
            return True
        
        for framework in compliance_reqs:
            if not self._validate_framework(framework, context):
                self.logger.warning(
                    f"Task {task.task_id}: Failed {framework} compliance check"
                )
                return False
        
        self.logger.info(
            f"Task {task.task_id}: All compliance requirements satisfied: "
            f"{', '.join(compliance_reqs)}"
        )
        return True
    
    def _validate_framework(self, framework: str, context: DecisionContext) -> bool:
        """Validate a specific compliance framework."""
        framework = framework.lower()
        rules = self.compliance_rules.get(framework)
        
        if not rules:
            self.logger.warning(f"Unknown compliance framework: {framework}")
            return False
        
        task = context.task
        compliance_ctx = context.compliance
        
        # Check encryption requirement
        if rules.get('encryption_required', False) and not compliance_ctx.encryption_required:
            self.logger.warning(f"Encryption required for {framework}")
            return False
        
        # Check audit logging requirement
        if rules.get('audit_logging_required', False) and not compliance_ctx.audit_logging_required:
            self.logger.warning(f"Audit logging required for {framework}")
            return False
        
        # Check data residency
        if rules.get('data_residency_required', False):
            allowed_regions = self.allowed_regions.get(framework, [])
            if allowed_regions and 'any' not in allowed_regions:
                if not compliance_ctx.data_residency_required:
                    self.logger.warning(f"Data residency requirement not specified for {framework}")
                    return False
                
                if not set(task.preferred_regions).intersection(set(allowed_regions)):
                    self.logger.warning(
                        f"Task region {task.preferred_regions} not in allowed regions "
                        f"for {framework}: {allowed_regions}"
                    )
                    return False
        
        # Check access control requirement
        if rules.get('access_control_required', False):
            if not self._check_access_control(task):
                self.logger.warning(f"Access control check failed for {framework}")
                return False
        
        return True
    
    def _check_access_control(self, task) -> bool:
        """Validate access control requirements."""
        # Check if user has required roles for sensitive operations
        sensitive_task_types = ['training', 'batch_processing']
        
        if task.task_type in sensitive_task_types:
            required_role = 'data_scientist' in task.user_roles or 'ml_engineer' in task.user_roles
            if not required_role:
                return False
        
        return True
    
    def get_allowed_regions(self, compliance_frameworks: List[str]) -> List[str]:
        """Get regions where task can run based on compliance requirements."""
        if not compliance_frameworks:
            return ['any']
        
        # Find intersection of allowed regions
        allowed_sets = []
        for framework in compliance_frameworks:
            framework = framework.lower()
            regions = self.allowed_regions.get(framework, ['any'])
            if 'any' not in regions:
                allowed_sets.append(set(regions))
        
        if not allowed_sets:
            return ['any']
        
        # Intersection of all constraints
        result = allowed_sets[0]
        for s in allowed_sets[1:]:
            result = result.intersection(s)
        
        return list(result) if result else []
    
    def get_required_settings(self, compliance_frameworks: List[str]) -> Dict[str, Any]:
        """Get required settings for compliance frameworks."""
        settings = {
            'encryption_required': False,
            'audit_logging_required': False,
            'access_control_required': False,
        }
        
        for framework in compliance_frameworks:
            framework = framework.lower()
            rules = self.compliance_rules.get(framework, {})
            for key in settings:
                if rules.get(key, False):
                    settings[key] = True
        
        return settings
