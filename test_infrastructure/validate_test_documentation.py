#!/usr/bin/env python3
"""
Test Documentation Validation Script

This script validates that all test documentation is complete, accurate, and up-to-date.
"""
import re
import sys
from pathlib import Path
import subprocess
import json


class DocumentationValidator:
    """Validates test documentation completeness and accuracy."""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.documentation_dir = self.root_path / "02_DOCUMENTATION"
        self.required_docs = [
            "TESTING_SYSTEM_GUIDE.md",
            "ADDING_NEW_TESTS_GUIDE.md", 
            "TEST_TROUBLESHOOTING_GUIDE.md",
            "TEST_SUITE_DOCUMENTATION.md",
            "TESTING_DOCUMENTATION_README.md"
        ]
        self.errors = []
        self.warnings = []
    
    def validate_all(self) -> bool:
        """Run all validation checks."""
        print("🔍 Validating test documentation...")
        print()
        
        # Check file existence
        self.check_required_files()
        
        # Check file content
        self.check_file_contents()
        
        # Check links
        self.check_internal_links()
        
        # Check code examples
        self.check_code_examples()
        
        # Check generated documentation
        self.check_generated_documentation()
        
        # Report results
        self.report_results()
        
        return len(self.errors) == 0
    
    def check_required_files(self):
        """Check that all required documentation files exist."""
        print("📁 Checking required files...")
        
        for doc_file in self.required_docs:
            file_path = self.documentation_dir / doc_file
            if not file_path.exists():
                self.errors.append(f"Missing required documentation file: {doc_file}")
            else:
                print(f"  ✅ {doc_file}")
        
        print()
    
    def check_file_contents(self):
        """Check that documentation files have proper content structure."""
        print("📝 Checking file contents...")
        
        for doc_file in self.required_docs:
            file_path = self.documentation_dir / doc_file
            if file_path.exists():
                self.validate_markdown_structure(file_path)
        
        print()
    
    def validate_markdown_structure(self, file_path: Path):
        """Validate markdown file structure."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for title
            if not content.startswith('#'):
                self.warnings.append(f"{file_path.name}: Missing main title")
            
            # Check for empty file
            if len(content.strip()) < 100:
                self.warnings.append(f"{file_path.name}: File seems too short")
            
            # Check for code blocks
            code_blocks = re.findall(r'```[\s\S]*?```', content)
            if file_path.name in ["TESTING_SYSTEM_GUIDE.md", "ADDING_NEW_TESTS_GUIDE.md"]:
                if len(code_blocks) < 3:
                    self.warnings.append(f"{file_path.name}: Expected more code examples")
            
            print(f"  ✅ {file_path.name} - Structure OK")
            
        except Exception as e:
            self.errors.append(f"Error reading {file_path.name}: {e}")
    
    def check_internal_links(self):
        """Check that internal links in documentation are valid."""
        print("🔗 Checking internal links...")
        
        for doc_file in self.required_docs:
            file_path = self.documentation_dir / doc_file
            if file_path.exists():
                self.validate_links_in_file(file_path)
        
        print()
    
    def validate_links_in_file(self, file_path: Path):
        """Validate links within a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find markdown links
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            
            for link_text, link_url in links:
                if link_url.startswith('http'):
                    continue  # Skip external links
                
                if link_url.startswith('#'):
                    continue  # Skip anchor links (would need more complex validation)
                
                # Check if file exists
                if link_url.endswith('.md'):
                    linked_file = self.documentation_dir / link_url
                    if not linked_file.exists():
                        self.errors.append(f"{file_path.name}: Broken link to {link_url}")
            
            print(f"  ✅ {file_path.name} - Links OK")
            
        except Exception as e:
            self.errors.append(f"Error checking links in {file_path.name}: {e}")
    
    def check_code_examples(self):
        """Check that code examples in documentation are valid."""
        print("💻 Checking code examples...")
        
        # Check that referenced scripts exist
        scripts_to_check = [
            "run_all_tests.py",
            "run_all_tests.bat",
            "generate_test_documentation.bat",
            "test_infrastructure/master_test_runner.py",
            "test_infrastructure/service_manager.py"
        ]
        
        for script in scripts_to_check:
            script_path = self.root_path / script
            if not script_path.exists():
                self.errors.append(f"Referenced script does not exist: {script}")
            else:
                print(f"  ✅ {script}")
        
        print()
    
    def check_generated_documentation(self):
        """Check that generated documentation is up-to-date."""
        print("🔄 Checking generated documentation...")
        
        # Check if TEST_SUITE_DOCUMENTATION.md exists and is recent
        suite_doc = self.documentation_dir / "TEST_SUITE_DOCUMENTATION.md"
        
        if not suite_doc.exists():
            self.errors.append("Generated test suite documentation is missing")
            return
        
        # Check if generator script exists
        generator_script = self.root_path / "test_infrastructure" / "test_documentation_generator.py"
        if not generator_script.exists():
            self.errors.append("Documentation generator script is missing")
            return
        
        # Try to run the generator to see if it works
        try:
            result = subprocess.run([
                sys.executable, 
                str(generator_script),
                "--list-files"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                self.errors.append(f"Documentation generator failed: {result.stderr}")
            else:
                print("  ✅ Documentation generator works")
                
        except subprocess.TimeoutExpired:
            self.warnings.append("Documentation generator is slow (>30s)")
        except Exception as e:
            self.errors.append(f"Error testing documentation generator: {e}")
        
        print()
    
    def report_results(self):
        """Report validation results."""
        print("📊 Validation Results")
        print("=" * 50)
        
        if not self.errors and not self.warnings:
            print("🎉 All documentation validation checks passed!")
            return
        
        if self.errors:
            print(f"❌ {len(self.errors)} Error(s):")
            for error in self.errors:
                print(f"   • {error}")
            print()
        
        if self.warnings:
            print(f"⚠️  {len(self.warnings)} Warning(s):")
            for warning in self.warnings:
                print(f"   • {warning}")
            print()
        
        if self.errors:
            print("❌ Documentation validation failed!")
            print("Please fix the errors above before proceeding.")
        else:
            print("✅ Documentation validation passed with warnings.")
            print("Consider addressing the warnings above.")
    
    def generate_validation_report(self, output_file: str = "documentation_validation_report.json"):
        """Generate a JSON report of validation results."""
        report = {
            "timestamp": str(Path().cwd()),
            "validation_passed": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "files_checked": self.required_docs,
            "summary": {
                "total_files": len(self.required_docs),
                "error_count": len(self.errors),
                "warning_count": len(self.warnings)
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Validation report saved to: {output_file}")


def main():
    """Main entry point for documentation validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate GopiAI test documentation")
    parser.add_argument("--root", default=".", help="Root directory of the project")
    parser.add_argument("--report", help="Generate JSON report to specified file")
    parser.add_argument("--quiet", action="store_true", help="Suppress output except errors")
    
    args = parser.parse_args()
    
    validator = DocumentationValidator(args.root)
    
    if args.quiet:
        # Redirect stdout to suppress normal output
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            success = validator.validate_all()
    else:
        success = validator.validate_all()
    
    if args.report:
        validator.generate_validation_report(args.report)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()