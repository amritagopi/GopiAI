"""
Core analyzers and infrastructure for project analysis
"""

from .project_cleanup_analyzer import (
    AnalysisResult, 
    AnalysisConfig, 
    BaseAnalyzer, 
    AnalysisError,
    ConfigurationError,
    FileAccessError,
    setup_logging,
    validate_project_path
)

from .structure_analyzer import StructureAnalyzer
from .code_quality_analyzer import CodeQualityAnalyzer  
from .dead_code_analyzer import DeadCodeAnalyzer
from .file_analyzer import FileAnalyzer
from .dependency_analyzer import DependencyAnalyzer
from .documentation_analyzer import DocumentationAnalyzer
from .duplicate_analyzer import DuplicateAnalyzer
from .conflict_analyzer import ConflictAnalyzer
from .report_generator import ReportGenerator
from .project_cleanup_orchestrator import ProjectCleanupAnalyzer

__all__ = [
    'AnalysisResult',
    'AnalysisConfig', 
    'BaseAnalyzer',
    'AnalysisError',
    'ConfigurationError',
    'FileAccessError',
    'setup_logging',
    'validate_project_path',
    'StructureAnalyzer',
    'CodeQualityAnalyzer',
    'DeadCodeAnalyzer', 
    'FileAnalyzer',
    'DependencyAnalyzer',
    'DocumentationAnalyzer',
    'DuplicateAnalyzer',
    'ConflictAnalyzer',
    'ReportGenerator',
    'ProjectCleanupAnalyzer'
]