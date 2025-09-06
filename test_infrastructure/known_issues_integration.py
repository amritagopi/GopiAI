"""
Integration module for known issues management with existing test infrastructure.

This module provides integration between the known issues management system
and the existing test infrastructure, including:
- Automatic detection of potential known issues
- Integration with failure analyzer
- Pytest plugin for xfail markers
- Automatic reporting integration
"""

import json
import re
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass

from known_issues_manager import KnownIssuesManager, IssueStatus, IssuePriority
from failure_analyzer import FailureAnalyzer, FailureCategory


@dataclass
class PotentialIssue:
    """Represents a potential known issue detected from test failures."""
    pattern: str
    affected_tests: List[str]
    failure_category: FailureCategory
    frequency: int
    suggested_title: str
    suggested_description: str
    suggested_priority: IssuePriority


class KnownIssuesIntegration:
    """Integrates known issues management with test infrastructure."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues_manager = KnownIssuesManager(project_root)
        self.failure_analyzer = FailureAnalyzer(project_root)
        
        # Patterns for detecting potential issues
        self.issue_patterns = {
            "connection_timeout": {
                "pattern": r"(ConnectionError|ConnectTimeout|TimeoutError).*timeout",
                "title": "Connection timeout issues",
                "description": "Tests failing due to connection timeouts",
                "priority": IssuePriority.HIGH
            },
            "import_missing": {
                "pattern": r"ModuleNotFoundError.*'(\w+)'",
                "title": "Missing module dependency",
                "description": "Tests failing due to missing module imports",
                "priority": IssuePriority.CRITICAL
            },
            "api_key_missing": {
                "pattern": r"(API_KEY|api.*key).*not.*found",
                "title": "Missing API key configuration",
                "description": "Tests failing due to missing API key configuration",
                "priority": IssuePriority.HIGH
            },
            "service_unavailable": {
                "pattern": r"(Service.*unavailable|Connection.*refused|port.*5051)",
                "title": "Service unavailable",
                "description": "Tests failing because required service is not running",
                "priority": IssuePriority.HIGH
            },
            "ui_widget_error": {
                "pattern": r"(QWidget|PySide6|Qt).*error",
                "title": "UI widget errors",
                "description": "Tests failing due to UI widget issues",
                "priority": IssuePriority.MEDIUM
            }
        }
    
    def analyze_failures_for_issues(self) -> List[PotentialIssue]:
        """Analyze recent test failures to identify potential known issues."""
        print("🔍 Analyzing failures for potential known issues...")
        
        # Get failure analysis
        failure_report = self.failure_analyzer.analyze_failures()
        
        if not failure_report.failures:
            print("✅ No failures to analyze")
            return []
        
        potential_issues = []
        
        # Group failures by pattern
        pattern_groups = self._group_failures_by_pattern(failure_report.failures)
        
        for pattern_name, pattern_info in self.issue_patterns.items():
            matching_failures = []
            
            for failure in failure_report.failures:
                full_text = f"{failure.error_message} {failure.stack_trace}"
                if re.search(pattern_info["pattern"], full_text, re.IGNORECASE):
                    matching_failures.append(failure)
            
            if len(matching_failures) >= 2:  # At least 2 tests affected
                affected_tests = [f.test_name for f in matching_failures]
                
                potential_issue = PotentialIssue(
                    pattern=pattern_info["pattern"],
                    affected_tests=affected_tests,
                    failure_category=matching_failures[0].category,
                    frequency=len(matching_failures),
                    suggested_title=pattern_info["title"],
                    suggested_description=f"{pattern_info['description']} (affects {len(matching_failures)} tests)",
                    suggested_priority=pattern_info["priority"]
                )
                
                potential_issues.append(potential_issue)
        
        print(f"🎯 Found {len(potential_issues)} potential known issues")
        return potential_issues
    
    def _group_failures_by_pattern(self, failures) -> Dict[str, List]:
        """Group failures by similar patterns."""
        groups = {}
        
        for failure in failures:
            # Simple grouping by error message similarity
            error_key = failure.error_message[:50] if failure.error_message else "unknown"
            
            if error_key not in groups:
                groups[error_key] = []
            groups[error_key].append(failure)
        
        return groups
    
    def suggest_known_issues(self, auto_create: bool = False) -> List[str]:
        """Suggest creating known issues for recurring failures."""
        potential_issues = self.analyze_failures_for_issues()
        
        if not potential_issues:
            return ["✅ No recurring failure patterns detected"]
        
        suggestions = []
        
        for issue in potential_issues:
            suggestion = f"🎯 Suggested issue: {issue.suggested_title}"
            suggestion += f"\n   Affects {issue.frequency} tests: {', '.join(issue.affected_tests[:3])}"
            if len(issue.affected_tests) > 3:
                suggestion += f" and {len(issue.affected_tests) - 3} more"
            suggestion += f"\n   Priority: {issue.suggested_priority.value}"
            
            suggestions.append(suggestion)
            
            if auto_create:
                # Auto-create the issue
                issue_id = f"AUTO-{len(suggestions):03d}"
                test_pattern = "|".join([t.split("::")[-1] for t in issue.affected_tests[:5]])
                
                try:
                    self.issues_manager.add_known_issue(
                        issue_id=issue_id,
                        title=issue.suggested_title,
                        description=issue.suggested_description,
                        test_pattern=test_pattern,
                        priority=issue.suggested_priority
                    )
                    suggestions.append(f"   ✅ Auto-created issue: {issue_id}")
                except Exception as e:
                    suggestions.append(f"   ❌ Failed to auto-create: {e}")
        
        return suggestions
    
    def update_pytest_configuration(self):
        """Update pytest configuration with known issues markers."""
        print("🔧 Updating pytest configuration...")
        
        # Get active issues
        active_issues = (
            self.issues_manager.get_issues_by_status(IssueStatus.OPEN) +
            self.issues_manager.get_issues_by_status(IssueStatus.IN_PROGRESS)
        )
        
        if not active_issues:
            print("✅ No active issues to configure")
            return
        
        # Update pytest.ini
        pytest_ini = self.project_root / "pytest.ini"
        
        # Read existing content
        existing_content = ""
        if pytest_ini.exists():
            with open(pytest_ini, 'r') as f:
                existing_content = f.read()
        
        # Generate markers section
        markers_section = "\n# Known issue markers (auto-generated)\nmarkers =\n"
        
        for issue in active_issues:
            marker_name = f"xfail_issue_{issue.issue_id.replace('-', '_')}"
            markers_section += f"    {marker_name}: {issue.title} (Issue: {issue.issue_id})\n"
        
        # Update or add markers section
        if "# Known issue markers" in existing_content:
            # Replace existing section
            pattern = r"# Known issue markers.*?(?=\n\[|\n#|\Z)"
            updated_content = re.sub(pattern, markers_section.strip(), existing_content, flags=re.DOTALL)
        else:
            # Add new section
            updated_content = existing_content + "\n" + markers_section
        
        # Write updated content
        with open(pytest_ini, 'w') as f:
            f.write(updated_content)
        
        print(f"✅ Updated pytest.ini with {len(active_issues)} issue markers")
    
    def generate_xfail_decorators(self) -> Dict[str, str]:
        """Generate xfail decorators for known issues."""
        active_issues = (
            self.issues_manager.get_issues_by_status(IssueStatus.OPEN) +
            self.issues_manager.get_issues_by_status(IssueStatus.IN_PROGRESS)
        )
        
        decorators = {}
        
        for issue in active_issues:
            marker_name = f"xfail_issue_{issue.issue_id.replace('-', '_')}"
            decorator = f'@pytest.mark.xfail(reason="{issue.title} (Issue: {issue.issue_id})", strict=False)'
            
            decorators[issue.issue_id] = {
                "marker_name": marker_name,
                "decorator": decorator,
                "affected_tests": issue.affected_tests
            }
        
        return decorators
    
    def check_test_file_markers(self, test_file: Path) -> List[str]:
        """Check if a test file has proper xfail markers for known issues."""
        if not test_file.exists():
            return []
        
        suggestions = []
        
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get active issues
            active_issues = (
                self.issues_manager.get_issues_by_status(IssueStatus.OPEN) +
                self.issues_manager.get_issues_by_status(IssueStatus.IN_PROGRESS)
            )
            
            # Check each issue
            for issue in active_issues:
                # Check if any affected tests are in this file
                file_tests = [t for t in issue.affected_tests if str(test_file) in t]
                
                if file_tests:
                    marker_name = f"xfail_issue_{issue.issue_id.replace('-', '_')}"
                    
                    # Check if marker is already applied
                    if marker_name not in content:
                        suggestions.append(
                            f"💡 Consider adding @pytest.mark.{marker_name} to tests: {', '.join([t.split('::')[-1] for t in file_tests])}"
                        )
        
        except Exception as e:
            suggestions.append(f"⚠️ Error checking {test_file}: {e}")
        
        return suggestions
    
    def auto_apply_markers(self, test_file: Path, dry_run: bool = True) -> List[str]:
        """Automatically apply xfail markers to test functions."""
        if not test_file.exists():
            return ["❌ Test file not found"]
        
        changes = []
        
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Get active issues
            active_issues = (
                self.issues_manager.get_issues_by_status(IssueStatus.OPEN) +
                self.issues_manager.get_issues_by_status(IssueStatus.IN_PROGRESS)
            )
            
            modified_lines = lines.copy()
            
            # Process each issue
            for issue in active_issues:
                file_tests = [t for t in issue.affected_tests if str(test_file) in t]
                
                if not file_tests:
                    continue
                
                marker_name = f"xfail_issue_{issue.issue_id.replace('-', '_')}"
                decorator = f"@pytest.mark.{marker_name}\n"
                
                # Find test functions and add markers
                for i, line in enumerate(modified_lines):
                    if line.strip().startswith("def test_"):
                        test_func_name = line.strip().split("(")[0].replace("def ", "")
                        
                        # Check if this test is affected
                        if any(test_func_name in t for t in file_tests):
                            # Check if marker already exists
                            if i > 0 and marker_name in modified_lines[i-1]:
                                continue
                            
                            # Add marker before function
                            indent = len(line) - len(line.lstrip())
                            indented_decorator = " " * indent + decorator
                            modified_lines.insert(i, indented_decorator)
                            
                            changes.append(f"Added {marker_name} to {test_func_name}")
            
            # Apply changes if not dry run
            if not dry_run and changes:
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.writelines(modified_lines)
                changes.append(f"✅ Applied {len(changes)-1} markers to {test_file}")
            elif dry_run and changes:
                changes.append(f"🔍 Dry run: would apply {len(changes)} markers to {test_file}")
        
        except Exception as e:
            changes.append(f"❌ Error processing {test_file}: {e}")
        
        return changes
    
    def generate_integration_report(self) -> Dict:
        """Generate integration report showing known issues status."""
        print("📊 Generating integration report...")
        
        # Get known issues report
        issues_report = self.issues_manager.generate_report()
        
        # Get failure analysis
        failure_report = self.failure_analyzer.analyze_failures()
        
        # Analyze potential new issues
        potential_issues = self.analyze_failures_for_issues()
        
        # Check pytest configuration
        pytest_ini = self.project_root / "pytest.ini"
        pytest_configured = pytest_ini.exists() and "xfail_issue_" in pytest_ini.read_text()
        
        integration_report = {
            "timestamp": issues_report.timestamp,
            "known_issues_summary": {
                "total_issues": issues_report.total_issues,
                "active_issues": issues_report.issues_by_status.get("open", 0) + issues_report.issues_by_status.get("in_progress", 0),
                "resolved_issues": issues_report.issues_by_status.get("resolved", 0)
            },
            "failure_analysis": {
                "total_failures": failure_report.total_failures,
                "categorized_failures": len(failure_report.failures),
                "potential_new_issues": len(potential_issues)
            },
            "integration_status": {
                "pytest_configured": pytest_configured,
                "markers_updated": len(issues_report.resolution_progress) > 0,
                "auto_detection_enabled": True
            },
            "recommendations": []
        }
        
        # Generate integration recommendations
        if not pytest_configured:
            integration_report["recommendations"].append("🔧 Update pytest configuration with known issue markers")
        
        if potential_issues:
            integration_report["recommendations"].append(f"🎯 Consider creating {len(potential_issues)} new known issues for recurring failures")
        
        if issues_report.stale_issues:
            integration_report["recommendations"].append(f"🕐 Review {len(issues_report.stale_issues)} stale issues")
        
        # Save integration report
        report_file = self.project_root / "test_infrastructure" / "known_issues" / "integration_report.json"
        with open(report_file, 'w') as f:
            json.dump(integration_report, f, indent=2)
        
        print(f"📊 Integration report saved: {report_file}")
        return integration_report


def main():
    """Main function for testing integration."""
    integration = KnownIssuesIntegration()
    
    print("🔧 Testing Known Issues Integration")
    print("=" * 50)
    
    # Analyze failures for potential issues
    suggestions = integration.suggest_known_issues()
    if suggestions:
        print("\n💡 Suggestions:")
        for suggestion in suggestions:
            print(f"  {suggestion}")
    
    # Update pytest configuration
    integration.update_pytest_configuration()
    
    # Generate integration report
    report = integration.generate_integration_report()
    
    print(f"\n📊 Integration Report Summary:")
    print(f"  Active Issues: {report['known_issues_summary']['active_issues']}")
    print(f"  Total Failures: {report['failure_analysis']['total_failures']}")
    print(f"  Potential New Issues: {report['failure_analysis']['potential_new_issues']}")
    print(f"  Pytest Configured: {report['integration_status']['pytest_configured']}")


if __name__ == "__main__":
    main()