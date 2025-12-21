from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal
import pandas as pd

@dataclass
class ValidationResult:
    """
    Standardized result from any validator.
    
    Applying DRY: All validators return this same structure instead of
    manually constructing dictionaries.
    
    Attributes:
        name: Identifier for this validation check
        status: 'passed', 'warning', or 'failed'
        message: Human-readable summary
        issues: Detailed list of problems found
        recommendations: Actionable suggestions for fixes
        details: Optional additional data for programmatic access
    """
    name: str
    status: Literal["passed", "warning", "failed"] = "passed"
    message: str = ""
    issues: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)
    details: dict = field(default_factory=dict)
    
    @property
    def passed(self) -> bool:
        """Convenience property for boolean checks."""
        return self.status == "passed"
    
    def to_dict(self) -> dict:
        """Serialize for JSON output."""
        return {
            'name': self.name,
            'status': self.status,
            'passed': self.passed,
            'message': self.message,
            'issues': self.issues,
            'recommendations': self.recommendations,
            'details': self.details
        }


class BaseValidator(ABC):
    """
    Abstract base class for all validators.
    
    Applying OCP: To add a new validation check, create a new class
    that extends BaseValidator. No modifications to existing code needed.
    
    Applying LSP: Any subclass can be used wherever BaseValidator is expected.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this validator."""
        pass
    
    @abstractmethod
    def validate(self, df: pd.DataFrame) -> ValidationResult:
        """
        Run validation on the given DataFrame.
        
        Args:
            df: The pandas DataFrame to validate
            
        Returns:
            ValidationResult with findings
        """
        pass
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


class Formatter(ABC):
    """
    Abstract base class for output formatters.
    
    Applying ISP: Formatters only need to implement format().
    Applying DIP: CLI depends on this abstraction, not concrete formatters.
    """
    
    @abstractmethod
    def format(self, results: list[ValidationResult]) -> str:
        """
        Format validation results for output.
        
        Args:
            results: List of ValidationResult objects
            
        Returns:
            Formatted string (text, JSON, HTML, etc.)
        """
        pass


class ValidationRunner:
    """
    Orchestrates multiple validators.
    
    Applying DIP: Accepts any list of BaseValidator implementations.
    Applying OCP: Adding validators doesn't require changing this class.
    """
    
    def __init__(self, validators: list[BaseValidator] | None = None):
        """
        Initialize with a list of validators.
        
        Args:
            validators: List of validator instances. If None, uses defaults.
        """
        self.validators = validators or []
    
    def add_validator(self, validator: BaseValidator) -> None:
        """Add a validator to the runner."""
        self.validators.append(validator)
    
    def run(self, df: pd.DataFrame) -> list[ValidationResult]:
        """
        Run all validators on the DataFrame.
        
        Args:
            df: The pandas DataFrame to validate
            
        Returns:
            List of ValidationResult from each validator
        """
        return [v.validate(df) for v in self.validators]
    
    def run_dict(self, df: pd.DataFrame) -> dict[str, ValidationResult]:
        """
        Run all validators and return as dictionary.
        
        Args:
            df: The pandas DataFrame to validate
            
        Returns:
            Dict mapping validator name to result
        """
        return {v.name: v.validate(df) for v in self.validators}