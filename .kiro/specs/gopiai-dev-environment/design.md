# Design Document: GopiAI Development Environment & Dependencies

## Overview

This design addresses the streamlining of development environment setup, dependency management, and development tooling for GopiAI. The solution focuses on creating a unified development experience with clear environment separation, automated dependency management, comprehensive tooling, and excellent documentation.

## Architecture

### Development Environment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          GopiAI Development Environment                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │   crewai_env    │  │   gopiai_env    │  │   shared_env    │             │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤             │
│  │ • CrewAI Server │  │ • UI Application│  │ • Dev Tools     │             │
│  │ • LLM Integration│  │ • PySide6 GUI   │  │ • Testing       │             │
│  │ • Tool Execution│  │ • API Client    │  │ • Linting       │             │
│  │ • Backend APIs  │  │ • UI Components │  │ • Documentation │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│           │                     │                     │                     │
│           └─────────────────────┼─────────────────────┘                     │
│                                 │                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                    Development Tooling Layer                           │ │
│  ├─────────────────────────────────────────────────────────────────────────┤ │
│  │ • Environment Manager  • Dependency Resolver  • Build System           │ │
│  │ • Testing Framework   • Code Quality Tools   • Documentation Generator │ │
│  │ • Deployment Scripts  • Configuration Manager • Monitoring Tools       │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Package Management Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Package Registry  │    │   Dependency Tree   │    │   Environment       │
├─────────────────────┤    ├─────────────────────┤    ├─────────────────────┤
│ • PyPI Packages     │    │ • Version Resolver  │    │ • Virtual Env       │
│ • Local Packages    │    │ • Conflict Detector │    │ • Path Management   │
│ • Development Deps  │    │ • Update Manager    │    │ • Activation Scripts│
│ • Optional Features │    │ • Security Scanner  │    │ • Isolation Control │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## Components and Interfaces

### Environment Management Components

#### 1. Environment Manager
**File:** `dev-tools/environment/manager.py`

```python
class EnvironmentManager:
    """Manages multiple virtual environments and their dependencies"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.environments = {
            'crewai': EnvironmentConfig('crewai_env', 'Backend services'),
            'gopiai': EnvironmentConfig('gopiai_env', 'UI application'),
            'shared': EnvironmentConfig('shared_env', 'Development tools')
        }
        
    def create_environment(self, name: str, python_version: str = "3.9") -> Environment:
        """Create new virtual environment"""
        
    def activate_environment(self, name: str) -> EnvironmentContext:
        """Activate specific environment"""
        
    def install_dependencies(self, name: str, requirements: List[str]) -> InstallResult:
        """Install dependencies in environment"""
        
    def check_environment_health(self, name: str) -> HealthReport:
        """Check environment health and conflicts"""
        
    def sync_environments(self) -> SyncResult:
        """Synchronize environments with requirements files"""
```

#### 2. Dependency Resolver
**File:** `dev-tools/dependencies/resolver.py`

```python
class DependencyResolver:
    """Resolves and manages package dependencies across environments"""
    
    def __init__(self):
        self.package_registry = PackageRegistry()
        self.conflict_detector = ConflictDetector()
        self.version_manager = VersionManager()
        
    def resolve_dependencies(self, requirements: List[Requirement]) -> ResolutionResult:
        """Resolve package dependencies and versions"""
        
    def detect_conflicts(self, environments: List[Environment]) -> List[Conflict]:
        """Detect dependency conflicts between environments"""
        
    def suggest_resolutions(self, conflicts: List[Conflict]) -> List[Resolution]:
        """Suggest conflict resolutions"""
        
    def update_dependencies(self, package: str, target_version: str = None) -> UpdateResult:
        """Update package and resolve new dependencies"""
        
    def generate_lock_file(self, environment: str) -> LockFile:
        """Generate dependency lock file for reproducible builds"""
```

#### 3. Configuration Manager
**File:** `dev-tools/config/manager.py`

```python
class ConfigurationManager:
    """Manages application configuration across environments"""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.environments = ['development', 'testing', 'production']
        self.config_schema = self._load_schema()
        
    def load_config(self, environment: str) -> Configuration:
        """Load configuration for specific environment"""
        
    def validate_config(self, config: Configuration) -> ValidationResult:
        """Validate configuration against schema"""
        
    def merge_configs(self, base: Configuration, override: Configuration) -> Configuration:
        """Merge configuration files with override support"""
        
    def generate_config_template(self, environment: str) -> str:
        """Generate configuration template"""
        
    def encrypt_sensitive_values(self, config: Configuration) -> Configuration:
        """Encrypt sensitive configuration values"""
```

### Development Tooling Components

#### 1. Build System
**File:** `dev-tools/build/system.py`

```python
class BuildSystem:
    """Manages building, packaging, and distribution of GopiAI components"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.modules = self._discover_modules()
        self.build_config = self._load_build_config()
        
    def build_module(self, module_name: str, target: str = 'development') -> BuildResult:
        """Build specific GopiAI module"""
        
    def build_all(self, target: str = 'development') -> List[BuildResult]:
        """Build all GopiAI modules"""
        
    def package_for_distribution(self, modules: List[str]) -> PackageResult:
        """Package modules for distribution"""
        
    def install_development_mode(self, modules: List[str]) -> InstallResult:
        """Install modules in development mode"""
        
    def clean_build_artifacts(self) -> CleanResult:
        """Clean build artifacts and temporary files"""
```

#### 2. Testing Framework
**File:** `dev-tools/testing/framework.py`

```python
class TestingFramework:
    """Comprehensive testing framework for GopiAI"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_config = self._load_test_config()
        self.coverage_config = self._load_coverage_config()
        
    def run_unit_tests(self, modules: List[str] = None) -> TestResult:
        """Run unit tests for specified modules"""
        
    def run_integration_tests(self) -> TestResult:
        """Run integration tests"""
        
    def run_ui_tests(self) -> TestResult:
        """Run UI tests using pytest-qt"""
        
    def generate_coverage_report(self) -> CoverageReport:
        """Generate code coverage report"""
        
    def run_performance_tests(self) -> PerformanceTestResult:
        """Run performance benchmarks"""
```

#### 3. Code Quality Tools
**File:** `dev-tools/quality/tools.py`

```python
class CodeQualityTools:
    """Code quality and style enforcement tools"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.style_config = self._load_style_config()
        
    def run_linting(self, files: List[Path] = None) -> LintResult:
        """Run code linting with flake8/pylint"""
        
    def format_code(self, files: List[Path] = None) -> FormatResult:
        """Format code with black and isort"""
        
    def check_type_hints(self, files: List[Path] = None) -> TypeCheckResult:
        """Check type hints with mypy"""
        
    def run_security_scan(self) -> SecurityScanResult:
        """Run security vulnerability scan"""
        
    def generate_quality_report(self) -> QualityReport:
        """Generate comprehensive code quality report"""
```

### Documentation and Deployment Components

#### 1. Documentation Generator
**File:** `dev-tools/docs/generator.py`

```python
class DocumentationGenerator:
    """Generates and maintains project documentation"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.docs_config = self._load_docs_config()
        
    def generate_api_docs(self, modules: List[str]) -> DocsResult:
        """Generate API documentation from docstrings"""
        
    def build_user_guide(self) -> DocsResult:
        """Build user guide from markdown sources"""
        
    def generate_setup_guide(self) -> DocsResult:
        """Generate development setup guide"""
        
    def validate_documentation(self) -> ValidationResult:
        """Validate documentation for completeness and accuracy"""
        
    def deploy_documentation(self, target: str) -> DeployResult:
        """Deploy documentation to hosting platform"""
```

#### 2. Deployment Manager
**File:** `dev-tools/deployment/manager.py`

```python
class DeploymentManager:
    """Manages deployment processes and environments"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.deployment_configs = self._load_deployment_configs()
        
    def prepare_deployment(self, target: str) -> PreparationResult:
        """Prepare application for deployment"""
        
    def deploy_application(self, target: str, version: str) -> DeploymentResult:
        """Deploy application to target environment"""
        
    def rollback_deployment(self, target: str, version: str) -> RollbackResult:
        """Rollback to previous deployment version"""
        
    def health_check(self, target: str) -> HealthCheckResult:
        """Perform post-deployment health check"""
        
    def generate_deployment_report(self, deployment_id: str) -> DeploymentReport:
        """Generate deployment report"""
```

## Data Models

### Environment Models

#### Environment Configuration
```python
@dataclass
class EnvironmentConfig:
    name: str
    description: str
    python_version: str
    requirements_file: Path
    environment_variables: Dict[str, str]
    activation_script: Path
    health_checks: List[HealthCheck]
```

#### Dependency Models
```python
@dataclass
class Requirement:
    name: str
    version_spec: str
    extras: List[str]
    environment_markers: str
    source: str  # pypi, git, local

@dataclass
class Conflict:
    package: str
    conflicting_versions: List[str]
    affected_environments: List[str]
    resolution_suggestions: List[str]
```

### Build and Test Models

#### Build Configuration
```python
@dataclass
class BuildConfig:
    module_name: str
    source_dir: Path
    build_dir: Path
    dependencies: List[str]
    build_steps: List[BuildStep]
    artifacts: List[Artifact]
```

#### Test Results
```python
@dataclass
class TestResult:
    total_tests: int
    passed: int
    failed: int
    skipped: int
    duration: float
    coverage_percentage: float
    failed_tests: List[FailedTest]
```

## Error Handling

### Environment Error Categories

1. **Environment Creation Errors**
   - Python version not available
   - Insufficient disk space
   - Permission issues
   - Network connectivity problems

2. **Dependency Resolution Errors**
   - Version conflicts
   - Missing packages
   - Incompatible dependencies
   - Network/registry issues

3. **Configuration Errors**
   - Invalid configuration syntax
   - Missing required settings
   - Environment variable issues
   - File permission problems

### Development Tool Error Handling

1. **Build Errors**
   - Compilation failures
   - Missing dependencies
   - Resource limitations
   - Output directory issues

2. **Test Errors**
   - Test environment setup
   - Missing test dependencies
   - Resource conflicts
   - Timeout issues

## Testing Strategy

### Environment Testing

#### Unit Tests
- Environment creation and management
- Dependency resolution logic
- Configuration validation
- Tool integration

#### Integration Tests
- Multi-environment workflows
- Cross-platform compatibility
- End-to-end development workflows
- Deployment processes

#### Environment Tests
```python
def test_environment_isolation():
    """Test that environments are properly isolated"""
    manager = EnvironmentManager(project_root)
    
    # Create two environments with conflicting dependencies
    env1 = manager.create_environment('test1')
    env2 = manager.create_environment('test2')
    
    # Install different versions of same package
    manager.install_dependencies('test1', ['requests==2.25.1'])
    manager.install_dependencies('test2', ['requests==2.28.0'])
    
    # Verify isolation
    assert env1.get_package_version('requests') == '2.25.1'
    assert env2.get_package_version('requests') == '2.28.0'
```

### Tool Testing

#### Functionality Tests
- Build system operations
- Test framework execution
- Code quality tool integration
- Documentation generation

#### Performance Tests
```python
def test_build_performance():
    """Test build system performance"""
    build_system = BuildSystem(project_root)
    
    start_time = time.time()
    result = build_system.build_all(target='development')
    duration = time.time() - start_time
    
    assert duration < 300  # Build should complete within 5 minutes
    assert all(r.success for r in result)
```

## Security Considerations

### Environment Security
- Isolated virtual environments
- Secure dependency installation
- Environment variable protection
- Access control for sensitive configurations

### Development Security
- Code scanning for vulnerabilities
- Dependency security auditing
- Secure credential management
- Build artifact integrity verification

## Deployment Strategy

### Development Environment Setup
1. Automated environment creation
2. Dependency installation and verification
3. Configuration setup and validation
4. Tool integration and testing

### Continuous Integration Integration
1. Automated testing on multiple platforms
2. Code quality enforcement
3. Security scanning integration
4. Documentation generation and deployment

### Developer Onboarding
1. Automated setup scripts
2. Interactive setup wizard
3. Comprehensive documentation
4. Troubleshooting guides and support

This design ensures a streamlined development experience with proper environment isolation, comprehensive tooling, and excellent developer productivity while maintaining code quality and security standards.