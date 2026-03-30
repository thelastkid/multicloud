"""Logging utility for the policy engine."""
import logging
import sys
from datetime import datetime


class PolicyEngineLogger:
    """Configure and provide logging for policy engine."""
    
    def __init__(self, name="PolicyEngine", level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)-8s [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # Add handler only if not already present
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
    
    def get_logger(self):
        return self.logger


def get_logger(name="PolicyEngine"):
    """Get or create logger instance."""
    return PolicyEngineLogger(name).get_logger()
