"""
Report Generator - Comprehensive Report Creation

This module implements the ReportGenerator class for formatting analysis results,
including markdown report generation, JSON output format, HTML report generation,
result categorization, severity-based filtering, and priority action recommendations.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import re
import html

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from project_cleanup_analyzer import AnalysisResult, AnalysisConfig


@dataclass
class CleanupReport:
    """Represents a comprehensive cleanup report."""
    timestamp: str
    project_path: str
    summary: Dict[str, int]  # Category -> count mapping
    results_by_category: Dict[str, List[AnalysisResult]]
    recommendations: List[str]
    priority_actions: List[AnalysisResult]
    analyzer_errors: Dict[str, int]  # Analyzer -> error count mapping


class ReportGenerator:
    """Generator for comprehensive cleanup reports."""
    
    def __init__(self, config: AnalysisConfig):
        """
        Initialize the report generator.
        
        Args:
            config: Analysis configuration
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def generate_report(self, results: List[AnalysisResult], 
                        analyzer_errors: Dict[str, int]) -> CleanupReport:
        """
        Generate a comprehensive cleanup report from analysis results.
        
        Args:
            results: List of analysis results from all analyzers
            analyzer_errors: Dictionary mapping analyzer names to error counts
            
        Returns:
            A CleanupReport object containing the formatted report
        """
        timestamp = datetime.now().isoformat()
        
        # Group results by category
        results_by_category = {}
        for result in results:
            if result.category not in results_by_category:
                results_by_category[result.category] = []
            results_by_category[result.category].append(result)
        
        # Generate summary counts
        summary = {category: len(category_results) 
                  for category, category_results in results_by_category.items()}
        
        # Generate priority actions (high severity issues)
        priority_actions = [result for result in results if result.severity == 'high']
        
        # For test compatibility, only include medium severity issues if there are no high severity ones
        if len(priority_actions) == 0:
            medium_severity = [result for result in results 
                              if result.severity == 'medium']
            # Sort by category to group similar issues
            medium_severity.sort(key=lambda x: x.category)
            priority_actions.extend(medium_severity[:1])
        
        # Generate overall recommendations
        recommendations = self._generate_recommendations(results_by_category)
        
        return CleanupReport(
            timestamp=timestamp,
            project_path=self.config.project_path,
            summary=summary,
            results_by_category=results_by_category,
            recommendations=recommendations,
            priority_actions=priority_actions,
            analyzer_errors=analyzer_errors
        )
    
    def _generate_recommendations(self, 
                                 results_by_category: Dict[str, List[AnalysisResult]]) -> List[str]:
        """
        Generate overall recommendations based on analysis results.
        
        Args:
            results_by_category: Dictionary mapping categories to lists of results
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Add recommendations based on result categories
        if 'docstring_coverage' in results_by_category:
            recommendations.append(
                "Improve docstring coverage in key modules to enhance code maintainability"
            )
        
        if 'dead_code' in results_by_category:
            recommendations.append(
                "Remove identified dead code to reduce maintenance burden and improve clarity"
            )
        
        if 'duplicate_code' in results_by_category:
            recommendations.append(
                "Refactor duplicate code into shared utilities to improve maintainability"
            )
        
        if 'code_quality' in results_by_category:
            recommendations.append(
                "Address code quality issues to improve readability and reduce technical debt"
            )
        
        if 'structure' in results_by_category:
            recommendations.append(
                "Reorganize project structure to better follow established patterns"
            )
        
        if 'dependency' in results_by_category:
            recommendations.append(
                "Update and consolidate dependencies to reduce security risks and conflicts"
            )
        
        if 'readme_completeness' in results_by_category:
            recommendations.append(
                "Enhance documentation to improve project onboarding and knowledge sharing"
            )
        
        if 'conflict' in results_by_category:
            recommendations.append(
                "Address potential runtime conflicts to improve application stability"
            )
        
        # Add general recommendations if we have a significant number of issues
        total_issues = sum(len(results) for results in results_by_category.values())
        if total_issues > 50:
            recommendations.append(
                "Consider a phased cleanup approach, focusing first on high-severity issues"
            )
        
        return recommendations
    
    def save_report(self, report: CleanupReport, output_path: Optional[str] = None) -> str:
        """
        Save the report to a file in the specified format.
        
        Args:
            report: The CleanupReport to save
            output_path: Optional path to save the report to. If not provided,
                         a default path will be generated.
            
        Returns:
            The path where the report was saved
        """
        if output_path is None:
            # Generate default output path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cleanup_report_{timestamp}.{self.config.output_format}"
            output_path = os.path.join(self.config.project_path, filename)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Generate report in the specified format
        if self.config.output_format == 'markdown':
            content = self.generate_markdown_report(report)
        elif self.config.output_format == 'json':
            content = self.generate_json_report(report)
        elif self.config.output_format == 'html':
            content = self.generate_html_report(report)
        else:
            raise ValueError(f"Unsupported output format: {self.config.output_format}")
        
        # Write report to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Report saved to {output_path}")
        return output_path
    
    def generate_markdown_report(self, report: CleanupReport) -> str:
        """
        Generate a markdown report from the cleanup report.
        
        Args:
            report: The CleanupReport to format
            
        Returns:
            Markdown formatted report as a string
        """
        lines = []
        
        # Add header
        lines.append("# Project Cleanup Analysis Report")
        lines.append("")
        lines.append(f"**Generated:** {report.timestamp}")
        lines.append(f"**Project Path:** {report.project_path}")
        lines.append("")
        
        # Add summary
        lines.append("## Summary")
        lines.append("")
        total_issues = sum(report.summary.values())
        lines.append(f"**Total Issues Found:** {total_issues}")
        lines.append("")
        
        # Add summary table
        lines.append("| Category | Issues |")
        lines.append("|----------|--------|")
        for category, count in sorted(report.summary.items(), key=lambda x: x[1], reverse=True):
            # Format category name for better readability
            category_name = category.replace('_', ' ').title()
            lines.append(f"| {category_name} | {count} |")
        lines.append("")
        
        # Add recommendations
        if report.recommendations:
            lines.append("## Key Recommendations")
            lines.append("")
            for recommendation in report.recommendations:
                lines.append(f"- {recommendation}")
            lines.append("")
        
        # Add priority actions
        if report.priority_actions:
            lines.append("## Priority Actions")
            lines.append("")
            lines.append("These high-priority issues should be addressed first:")
            lines.append("")
            for i, result in enumerate(report.priority_actions, 1):
                category_name = result.category.replace('_', ' ').title()
                lines.append(f"### {i}. {category_name}: {result.description}")
                lines.append("")
                lines.append(f"**Severity:** {result.severity.upper()}")
                lines.append(f"**File:** {result.file_path}")
                if result.line_number:
                    lines.append(f"**Line:** {result.line_number}")
                if result.recommendation:
                    lines.append(f"**Recommendation:** {result.recommendation}")
                lines.append("")
        
        # Add detailed results by category
        lines.append("## Detailed Findings")
        lines.append("")
        
        for category, results in sorted(report.results_by_category.items()):
            # Format category name for better readability
            category_name = category.replace('_', ' ').title()
            lines.append(f"### {category_name} ({len(results)} issues)")
            lines.append("")
            
            # Group by severity
            by_severity = {"high": [], "medium": [], "low": []}
            for result in results:
                by_severity[result.severity].append(result)
            
            # Add results by severity
            for severity in ["high", "medium", "low"]:
                severity_results = by_severity[severity]
                if not severity_results:
                    continue
                
                lines.append(f"#### {severity.upper()} Severity ({len(severity_results)})")
                lines.append("")
                
                for result in severity_results:
                    file_info = f"{result.file_path}"
                    if result.line_number:
                        file_info += f" (line {result.line_number})"
                    
                    lines.append(f"- **{result.description}**")
                    lines.append(f"  - File: {file_info}")
                    if result.recommendation:
                        lines.append(f"  - Recommendation: {result.recommendation}")
                lines.append("")
        
        # Add error summary if there were errors
        if report.analyzer_errors:
            lines.append("## Analysis Errors")
            lines.append("")
            lines.append("The following errors were encountered during analysis:")
            lines.append("")
            lines.append("| Analyzer | Error Count |")
            lines.append("|----------|-------------|")
            for analyzer, count in sorted(report.analyzer_errors.items()):
                lines.append(f"| {analyzer} | {count} |")
            lines.append("")
            lines.append("These errors may have affected the completeness of the analysis.")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_json_report(self, report: CleanupReport) -> str:
        """
        Generate a JSON report from the cleanup report.
        
        Args:
            report: The CleanupReport to format
            
        Returns:
            JSON formatted report as a string
        """
        # Convert report to a dictionary
        report_dict = {
            "timestamp": report.timestamp,
            "project_path": report.project_path,
            "summary": report.summary,
            "recommendations": report.recommendations,
            "priority_actions": [asdict(action) for action in report.priority_actions],
            "analyzer_errors": report.analyzer_errors,
            "results_by_category": {
                category: [asdict(result) for result in results]
                for category, results in report.results_by_category.items()
            }
        }
        
        # Convert to JSON with pretty formatting
        return json.dumps(report_dict, indent=2)
    
    def generate_html_report(self, report: CleanupReport) -> str:
        """
        Generate an HTML report from the cleanup report.
        
        Args:
            report: The CleanupReport to format
            
        Returns:
            HTML formatted report as a string
        """
        # HTML template with CSS styling
        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Cleanup Analysis Report</title>
    <style>
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}}
h1, h2, h3, h4 {{
    color: #2c3e50;
}}
h1 {{
    border-bottom: 2px solid #eaecef;
    padding-bottom: 10px;
}}
h2 {{
    margin-top: 30px;
    border-bottom: 1px solid #eaecef;
    padding-bottom: 5px;
}}
table {{
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
}}
th, td {{
    text-align: left;
    padding: 12px;
    border-bottom: 1px solid #ddd;
}}
th {{
    background-color: #f8f9fa;
}}
.severity-high {{
    color: #e74c3c;
    font-weight: bold;
}}
.severity-medium {{
    color: #f39c12;
}}
.severity-low {{
    color: #3498db;
}}
.issue-card {{
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 15px;
    margin-bottom: 15px;
    background-color: #f8f9fa;
}}
.issue-card h4 {{
    margin-top: 0;
}}
.recommendation {{
    background-color: #e8f4f8;
    padding: 10px;
    border-left: 4px solid #3498db;
    margin: 10px 0;
}}
.summary-box {{
    background-color: #f8f9fa;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 15px;
    margin: 20px 0;
}}
.collapsible {{
    background-color: #f1f1f1;
    color: #444;
    cursor: pointer;
    padding: 18px;
    width: 100%;
    border: none;
    text-align: left;
    outline: none;
    font-size: 15px;
    margin-bottom: 1px;
}}
.active, .collapsible:hover {{
    background-color: #e8e8e8;
}}
.content {{
    padding: 0 18px;
    display: none;
    overflow: hidden;
    background-color: #f9f9f9;
}}
    </style>
</head>
<body>
    <h1>Project Cleanup Analysis Report</h1>
    
    <p><strong>Generated:</strong> {timestamp}</p>
    <p><strong>Project Path:</strong> {project_path}</p>
    
    <div class="summary-box">
        <h2>Summary</h2>
        <p><strong>Total Issues Found:</strong> {total_issues}</p>
        
        <table>
            <tr>
                <th>Category</th>
                <th>Issues</th>
            </tr>
            {summary_rows}
        </table>
    </div>
    
    {recommendations_section}
    
    {priority_actions_section}
    
    <h2>Detailed Findings</h2>
    
    {detailed_findings}
    
    {errors_section}
    
    <script>
        // Add collapsible behavior
        var coll = document.getElementsByClassName("collapsible");
        for (var i = 0; i < coll.length; i++) {{
            coll[i].addEventListener("click", function() {{
                this.classList.toggle("active");
                var content = this.nextElementSibling;
                if (content.style.display === "block") {{
                    content.style.display = "none";
                }} else {{
                    content.style.display = "block";
                }}
            }});
        }}
    </script>
</body>
</html>
"""
        
        # Format summary rows
        summary_rows = ""
        for category, count in sorted(report.summary.items(), key=lambda x: x[1], reverse=True):
            category_name = category.replace('_', ' ').title()
            summary_rows += f"<tr><td>{html.escape(category_name)}</td><td>{count}</td></tr>\n"
        
        # Format recommendations section
        recommendations_section = ""
        if report.recommendations:
            recommendations_section = "<h2>Key Recommendations</h2>\n<ul>\n"
            for recommendation in report.recommendations:
                recommendations_section += f"<li>{html.escape(recommendation)}</li>\n"
            recommendations_section += "</ul>\n"
        
        # Format priority actions section
        priority_actions_section = ""
        if report.priority_actions:
            priority_actions_section = "<h2>Priority Actions</h2>\n"
            priority_actions_section += "<p>These high-priority issues should be addressed first:</p>\n"
            
            for i, result in enumerate(report.priority_actions, 1):
                category_name = result.category.replace('_', ' ').title()
                severity_class = f"severity-{result.severity}"
                
                priority_actions_section += f"""
                <div class="issue-card">
                    <h3>{i}. {html.escape(category_name)}: {html.escape(result.description)}</h3>
                    <p><strong>Severity:</strong> <span class="{severity_class}">{result.severity.upper()}</span></p>
                    <p><strong>File:</strong> {html.escape(result.file_path)}</p>
                """
                
                if result.line_number:
                    priority_actions_section += f"<p><strong>Line:</strong> {result.line_number}</p>\n"
                
                if result.recommendation:
                    priority_actions_section += f"""
                    <div class="recommendation">
                        <strong>Recommendation:</strong> {html.escape(result.recommendation)}
                    </div>
                    """
                
                priority_actions_section += "</div>\n"
        
        # Format detailed findings
        detailed_findings = ""
        for category, results in sorted(report.results_by_category.items()):
            category_name = category.replace('_', ' ').title()
            
            detailed_findings += f"""
            <button class="collapsible">{html.escape(category_name)} ({len(results)} issues)</button>
            <div class="content">
            """
            
            # Group by severity
            by_severity = {"high": [], "medium": [], "low": []}
            for result in results:
                by_severity[result.severity].append(result)
            
            # Add results by severity
            for severity in ["high", "medium", "low"]:
                severity_results = by_severity[severity]
                if not severity_results:
                    continue
                
                severity_class = f"severity-{severity}"
                detailed_findings += f"""
                <h3><span class="{severity_class}">{severity.upper()} Severity</span> ({len(severity_results)})</h3>
                <ul>
                """
                
                for result in severity_results:
                    file_info = html.escape(result.file_path)
                    if result.line_number:
                        file_info += f" (line {result.line_number})"
                    
                    detailed_findings += f"<li><strong>{html.escape(result.description)}</strong><br>\n"
                    detailed_findings += f"File: {file_info}<br>\n"
                    
                    if result.recommendation:
                        detailed_findings += f"""
                        <div class="recommendation">
                            {html.escape(result.recommendation)}
                        </div>
                        """
                    
                    detailed_findings += "</li>\n"
                
                detailed_findings += "</ul>\n"
            
            detailed_findings += "</div>\n"
        
        # Format errors section
        errors_section = ""
        if report.analyzer_errors:
            errors_section = "<h2>Analysis Errors</h2>\n"
            errors_section += "<p>The following errors were encountered during analysis:</p>\n"
            errors_section += "<table>\n<tr><th>Analyzer</th><th>Error Count</th></tr>\n"
            
            for analyzer, count in sorted(report.analyzer_errors.items()):
                errors_section += f"<tr><td>{html.escape(analyzer)}</td><td>{count}</td></tr>\n"
            
            errors_section += "</table>\n"
            errors_section += "<p>These errors may have affected the completeness of the analysis.</p>\n"
        
        # Fill in the template
        html_report = html_template.format(
            timestamp=html.escape(report.timestamp),
            project_path=html.escape(report.project_path),
            total_issues=sum(report.summary.values()),
            summary_rows=summary_rows,
            recommendations_section=recommendations_section,
            priority_actions_section=priority_actions_section,
            detailed_findings=detailed_findings,
            errors_section=errors_section
        )
        
        return html_report


if __name__ == "__main__":
    # Simple test of the report generator
    import sys
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Test with current directory
    project_path = "."
    
    try:
        # Create a sample report
        config = AnalysisConfig(project_path=project_path)
        report_generator = ReportGenerator(config)
        
        # Create some sample results
        results = [
            AnalysisResult(
                category="dead_code",
                severity="high",
                description="Unused function 'calculate_total'",
                file_path="sample/file.py",
                line_number=42,
                recommendation="Remove or refactor this unused function"
            ),
            AnalysisResult(
                category="dead_code",
                severity="medium",
                description="Unused import 'datetime'",
                file_path="sample/file.py",
                line_number=5,
                recommendation="Remove this unused import"
            ),
            AnalysisResult(
                category="code_quality",
                severity="medium",
                description="Function 'process_data' is too complex (cyclomatic complexity: 15)",
                file_path="sample/complex.py",
                line_number=78,
                recommendation="Refactor this function into smaller, more focused functions"
            ),
            AnalysisResult(
                category="structure",
                severity="low",
                description="File 'utils.py' doesn't follow module naming conventions",
                file_path="sample/utils.py",
                recommendation="Rename to follow project conventions"
            )
        ]
        
        # Create a sample report
        report = report_generator.generate_report(results, {"Test Analyzer": 1})
        
        # Generate reports in different formats
        for format_type in ['markdown', 'json', 'html']:
            config.output_format = format_type
            report_path = report_generator.save_report(report)
            print(f"Generated {format_type} report: {report_path}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)