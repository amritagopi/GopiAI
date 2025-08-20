"""
Duplicate Analyzer - Code Duplication Detection

This module implements the DuplicateAnalyzer class for identifying duplicate code
blocks, similar functions, and refactoring opportunities in Python files using
AST-based similarity detection algorithms.
"""

import ast
import hashlib
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple, Any
from dataclasses import dataclass
import logging
from collections import defaultdict
import difflib

from project_cleanup_analyzer import BaseAnalyzer, AnalysisResult, AnalysisError, AnalysisConfig


@dataclass
class CodeBlock:
    """Represents a code block for duplication analysis."""
    file_path: str
    start_line: int
    end_line: int
    code: str
    ast_hash: str
    normalized_code: str
    block_type: str  # 'function', 'class', 'method', 'block'
    name: str = ""


@dataclass
class FunctionSignature:
    """Represents a function signature for similarity analysis."""
    name: str
    file_path: str
    line_number: int
    parameters: List[str]
    return_annotation: str
    docstring: str
    body_hash: str
    complexity_score: int


@dataclass
class DuplicateGroup:
    """Represents a group of duplicate code blocks."""
    blocks: List[CodeBlock]
    similarity_score: float
    duplicate_type: str  # 'exact', 'similar', 'structural'


class DuplicateAnalyzer(BaseAnalyzer):
    """Analyzer for detecting code duplication and similar code blocks."""
    
    # Minimum lines for a code block to be considered for duplication analysis
    MIN_BLOCK_SIZE = 3
    
    # Similarity thresholds
    EXACT_MATCH_THRESHOLD = 1.0
    SIMILAR_MATCH_THRESHOLD = 0.8
    STRUCTURAL_MATCH_THRESHOLD = 0.6
    
    def __init__(self, config: AnalysisConfig):
        super().__init__(config)
        self.code_blocks: List[CodeBlock] = []
        self.function_signatures: List[FunctionSignature] = []
        self.duplicate_groups: List[DuplicateGroup] = []
        
    def get_analyzer_name(self) -> str:
        """Get the analyzer name."""
        return "Duplicate Analyzer"
    
    def analyze(self, project_path: str) -> List[AnalysisResult]:
        """
        Perform duplicate code analysis on the project.
        
        Args:
            project_path: Path to the project root directory
            
        Returns:
            List of analysis results
        """
        results = []
        project_root = Path(project_path)
        
        try:
            # Get all Python files
            python_files = self.get_project_files(project_path, ['.py'])
            
            if not python_files:
                self.logger.info("No Python files found for analysis")
                return []
            
            self.logger.info(f"Found {len(python_files)} Python files for duplicate analysis")
            
            # Extract code blocks and function signatures
            for file_path in python_files:
                self._extract_code_blocks(file_path)
                self._extract_function_signatures(file_path)
            
            # Find duplicate code blocks
            results.extend(self._find_duplicate_blocks())
            
            # Find similar function signatures
            results.extend(self._find_similar_functions())
            
            # Generate refactoring suggestions
            results.extend(self._suggest_refactoring_opportunities())
            
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=str(project_root),
                error=f"Failed to analyze duplicates: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
        
        return self.filter_results_by_severity(results)
    
    def _extract_code_blocks(self, file_path: Path) -> None:
        """
        Extract code blocks from a Python file for duplication analysis.
        
        Args:
            file_path: Path to the Python file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
                lines = file_content.splitlines()
            
            # Parse the AST
            tree = ast.parse(file_content)
            
            # Extract different types of code blocks
            extractor = CodeBlockExtractor(str(file_path), lines)
            extractor.visit(tree)
            
            # Add extracted blocks to our collection
            self.code_blocks.extend(extractor.blocks)
            
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=str(file_path),
                error=f"Failed to extract code blocks: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
    
    def _extract_function_signatures(self, file_path: Path) -> None:
        """
        Extract function signatures from a Python file for similarity analysis.
        
        Args:
            file_path: Path to the Python file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # Parse the AST
            tree = ast.parse(file_content)
            
            # Extract function signatures
            extractor = FunctionSignatureExtractor(str(file_path))
            extractor.visit(tree)
            
            # Add extracted signatures to our collection
            self.function_signatures.extend(extractor.signatures)
            
        except Exception as e:
            error = AnalysisError(
                analyzer=self.get_analyzer_name(),
                file_path=str(file_path),
                error=f"Failed to extract function signatures: {str(e)}",
                original_exception=e
            )
            self.error_handler.handle_error(error)
    
    def _find_duplicate_blocks(self) -> List[AnalysisResult]:
        """
        Find duplicate code blocks using various similarity measures.
        
        Returns:
            List of analysis results for duplicate blocks
        """
        results = []
        
        # Group blocks by hash for exact matches
        hash_groups = defaultdict(list)
        for block in self.code_blocks:
            if len(block.code.strip().splitlines()) >= self.MIN_BLOCK_SIZE:
                hash_groups[block.ast_hash].append(block)
        
        # Find exact duplicates
        for hash_key, blocks in hash_groups.items():
            if len(blocks) > 1:
                duplicate_group = DuplicateGroup(
                    blocks=blocks,
                    similarity_score=1.0,
                    duplicate_type='exact'
                )
                self.duplicate_groups.append(duplicate_group)
                
                # Create analysis results for exact duplicates
                file_locations = [f"{block.file_path}:{block.start_line}" for block in blocks]
                results.append(AnalysisResult(
                    category="exact_duplicate",
                    severity="high",
                    description=f"Exact duplicate {blocks[0].block_type} found in {len(blocks)} locations: {', '.join(file_locations)}",
                    file_path=blocks[0].file_path,
                    line_number=blocks[0].start_line,
                    recommendation=f"Extract duplicate {blocks[0].block_type} into a shared utility function or module"
                ))
        
        # Find similar blocks (not exact matches)
        similar_blocks = self._find_similar_blocks()
        for group in similar_blocks:
            self.duplicate_groups.append(group)
            
            file_locations = [f"{block.file_path}:{block.start_line}" for block in group.blocks]
            severity = "medium" if group.similarity_score > 0.8 else "low"
            
            results.append(AnalysisResult(
                category="similar_code",
                severity=severity,
                description=f"Similar {group.blocks[0].block_type} blocks ({group.similarity_score:.1%} similarity) found in {len(group.blocks)} locations: {', '.join(file_locations)}",
                file_path=group.blocks[0].file_path,
                line_number=group.blocks[0].start_line,
                recommendation=f"Consider refactoring similar {group.blocks[0].block_type} blocks to reduce duplication"
            ))
        
        return results
    
    def _find_similar_blocks(self) -> List[DuplicateGroup]:
        """
        Find similar (but not exact) code blocks using normalized comparison.
        
        Returns:
            List of duplicate groups for similar blocks
        """
        similar_groups = []
        processed_blocks = set()
        
        for i, block1 in enumerate(self.code_blocks):
            if i in processed_blocks or len(block1.code.strip().splitlines()) < self.MIN_BLOCK_SIZE:
                continue
            
            similar_blocks = [block1]
            
            for j, block2 in enumerate(self.code_blocks[i+1:], i+1):
                if j in processed_blocks or len(block2.code.strip().splitlines()) < self.MIN_BLOCK_SIZE:
                    continue
                
                # Skip if same file and overlapping lines
                if (block1.file_path == block2.file_path and 
                    not (block1.end_line < block2.start_line or block2.end_line < block1.start_line)):
                    continue
                
                # Calculate similarity
                similarity = self._calculate_code_similarity(block1, block2)
                
                if similarity >= self.SIMILAR_MATCH_THRESHOLD:
                    similar_blocks.append(block2)
                    processed_blocks.add(j)
            
            if len(similar_blocks) > 1:
                # Calculate average similarity for the group
                total_similarity = 0
                comparisons = 0
                
                for k in range(len(similar_blocks)):
                    for l in range(k+1, len(similar_blocks)):
                        total_similarity += self._calculate_code_similarity(similar_blocks[k], similar_blocks[l])
                        comparisons += 1
                
                avg_similarity = total_similarity / comparisons if comparisons > 0 else 0
                
                similar_groups.append(DuplicateGroup(
                    blocks=similar_blocks,
                    similarity_score=avg_similarity,
                    duplicate_type='similar'
                ))
                
                processed_blocks.add(i)
        
        return similar_groups
    
    def _calculate_code_similarity(self, block1: CodeBlock, block2: CodeBlock) -> float:
        """
        Calculate similarity between two code blocks.
        
        Args:
            block1: First code block
            block2: Second code block
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Use normalized code for comparison
        normalized1 = block1.normalized_code.strip()
        normalized2 = block2.normalized_code.strip()
        
        if not normalized1 or not normalized2:
            return 0.0
        
        # Use difflib to calculate similarity
        similarity = difflib.SequenceMatcher(None, normalized1, normalized2).ratio()
        
        return similarity
    
    def _find_similar_functions(self) -> List[AnalysisResult]:
        """
        Find functions with similar signatures that might be duplicates.
        
        Returns:
            List of analysis results for similar functions
        """
        results = []
        
        # Group functions by name
        name_groups = defaultdict(list)
        for signature in self.function_signatures:
            name_groups[signature.name].append(signature)
        
        # Find functions with same name but different implementations
        for name, signatures in name_groups.items():
            if len(signatures) > 1:
                # Check if they have different implementations
                unique_bodies = set(sig.body_hash for sig in signatures)
                if len(unique_bodies) > 1:
                    file_locations = [f"{sig.file_path}:{sig.line_number}" for sig in signatures]
                    results.append(AnalysisResult(
                        category="duplicate_function_name",
                        severity="medium",
                        description=f"Function '{name}' defined in multiple locations with different implementations: {', '.join(file_locations)}",
                        file_path=signatures[0].file_path,
                        line_number=signatures[0].line_number,
                        recommendation=f"Consider renaming or consolidating function '{name}' to avoid confusion"
                    ))
        
        # Find functions with similar signatures but different names
        for i, sig1 in enumerate(self.function_signatures):
            for sig2 in self.function_signatures[i+1:]:
                if sig1.file_path == sig2.file_path:
                    continue  # Skip functions in the same file
                
                # Check parameter similarity
                param_similarity = self._calculate_parameter_similarity(sig1.parameters, sig2.parameters)
                
                # Check body similarity
                body_similarity = 1.0 if sig1.body_hash == sig2.body_hash else 0.0
                
                # Combined similarity score
                overall_similarity = (param_similarity + body_similarity) / 2
                
                if overall_similarity >= 0.8 and sig1.name != sig2.name:
                    results.append(AnalysisResult(
                        category="similar_function_signature",
                        severity="low",
                        description=f"Functions '{sig1.name}' ({sig1.file_path}:{sig1.line_number}) and '{sig2.name}' ({sig2.file_path}:{sig2.line_number}) have similar signatures ({overall_similarity:.1%} similarity)",
                        file_path=sig1.file_path,
                        line_number=sig1.line_number,
                        recommendation="Consider if these functions can be consolidated or if one is redundant"
                    ))
        
        return results
    
    def _calculate_parameter_similarity(self, params1: List[str], params2: List[str]) -> float:
        """
        Calculate similarity between two parameter lists.
        
        Args:
            params1: First parameter list
            params2: Second parameter list
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not params1 and not params2:
            return 1.0
        
        if not params1 or not params2:
            return 0.0
        
        # Use set intersection for basic similarity
        set1 = set(params1)
        set2 = set(params2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _suggest_refactoring_opportunities(self) -> List[AnalysisResult]:
        """
        Generate refactoring suggestions based on duplicate analysis.
        
        Returns:
            List of analysis results with refactoring suggestions
        """
        results = []
        
        # Analyze duplicate groups for refactoring opportunities
        for group in self.duplicate_groups:
            if len(group.blocks) >= 2:
                # Suggest creating a utility function for exact duplicates
                if group.duplicate_type == 'exact' and group.blocks[0].block_type == 'function':
                    results.append(AnalysisResult(
                        category="refactoring_opportunity",
                        severity="medium",
                        description=f"Refactoring opportunity: Extract duplicate function '{group.blocks[0].name}' to a shared module",
                        file_path=group.blocks[0].file_path,
                        line_number=group.blocks[0].start_line,
                        recommendation="Create a shared utility module and import the function where needed"
                    ))
                
                # Suggest creating a base class for similar classes
                elif group.blocks[0].block_type == 'class' and len(group.blocks) >= 2:
                    class_names = [block.name for block in group.blocks if block.name]
                    if class_names:
                        results.append(AnalysisResult(
                            category="refactoring_opportunity",
                            severity="medium",
                            description=f"Refactoring opportunity: Similar classes {', '.join(class_names)} could benefit from a common base class",
                            file_path=group.blocks[0].file_path,
                            line_number=group.blocks[0].start_line,
                            recommendation="Consider creating a base class to share common functionality"
                        ))
        
        # Suggest consolidating similar functions
        function_groups = defaultdict(list)
        for signature in self.function_signatures:
            if signature.complexity_score > 10:  # High complexity functions
                function_groups[signature.name].append(signature)
        
        for name, signatures in function_groups.items():
            if len(signatures) > 1:
                results.append(AnalysisResult(
                    category="refactoring_opportunity",
                    severity="low",
                    description=f"Complex function '{name}' appears in multiple locations and might benefit from refactoring",
                    file_path=signatures[0].file_path,
                    line_number=signatures[0].line_number,
                    recommendation="Consider breaking down complex functions into smaller, reusable components"
                ))
        
        return results
    
    def get_duplicate_summary(self) -> Dict[str, Any]:
        """Get a summary of the duplicate analysis."""
        return {
            'total_code_blocks': len(self.code_blocks),
            'total_functions': len(self.function_signatures),
            'duplicate_groups': len(self.duplicate_groups),
            'exact_duplicates': len([g for g in self.duplicate_groups if g.duplicate_type == 'exact']),
            'similar_blocks': len([g for g in self.duplicate_groups if g.duplicate_type == 'similar']),
            'files_with_duplicates': len(set(block.file_path for group in self.duplicate_groups for block in group.blocks))
        }


class CodeBlockExtractor(ast.NodeVisitor):
    """AST visitor to extract code blocks for duplication analysis."""
    
    def __init__(self, file_path: str, lines: List[str]):
        self.file_path = file_path
        self.lines = lines
        self.blocks: List[CodeBlock] = []
    
    def visit_FunctionDef(self, node):
        """Visit a function definition."""
        self._extract_block(node, 'function', node.name)
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        """Visit an async function definition."""
        self._extract_block(node, 'function', node.name)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Visit a class definition."""
        self._extract_block(node, 'class', node.name)
        self.generic_visit(node)
    
    def visit_If(self, node):
        """Visit an if statement."""
        if self._is_significant_block(node):
            self._extract_block(node, 'block', 'if_block')
        self.generic_visit(node)
    
    def visit_For(self, node):
        """Visit a for loop."""
        if self._is_significant_block(node):
            self._extract_block(node, 'block', 'for_loop')
        self.generic_visit(node)
    
    def visit_While(self, node):
        """Visit a while loop."""
        if self._is_significant_block(node):
            self._extract_block(node, 'block', 'while_loop')
        self.generic_visit(node)
    
    def _is_significant_block(self, node) -> bool:
        """Check if a block is significant enough for duplication analysis."""
        # Calculate approximate line count
        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
            line_count = node.end_lineno - node.lineno + 1
            return line_count >= DuplicateAnalyzer.MIN_BLOCK_SIZE
        return False
    
    def _extract_block(self, node, block_type: str, name: str) -> None:
        """Extract a code block from an AST node."""
        try:
            start_line = node.lineno
            end_line = getattr(node, 'end_lineno', start_line)
            
            if end_line is None:
                end_line = start_line
            
            # Extract code lines
            code_lines = self.lines[start_line-1:end_line]
            code = '\n'.join(code_lines)
            
            # Generate AST hash
            ast_hash = self._generate_ast_hash(node)
            
            # Generate normalized code
            normalized_code = self._normalize_code(code)
            
            block = CodeBlock(
                file_path=self.file_path,
                start_line=start_line,
                end_line=end_line,
                code=code,
                ast_hash=ast_hash,
                normalized_code=normalized_code,
                block_type=block_type,
                name=name
            )
            
            self.blocks.append(block)
            
        except Exception as e:
            # Skip blocks that can't be processed
            pass
    
    def _generate_ast_hash(self, node) -> str:
        """Generate a hash of the AST structure."""
        try:
            # Use ast.dump to get a string representation of the AST
            ast_str = ast.dump(node, annotate_fields=False, include_attributes=False)
            return hashlib.md5(ast_str.encode()).hexdigest()
        except Exception:
            return ""
    
    def _normalize_code(self, code: str) -> str:
        """Normalize code for similarity comparison."""
        try:
            # Parse and unparse to normalize formatting
            tree = ast.parse(code)
            # Remove docstrings and comments for comparison
            normalized = ast.unparse(tree) if hasattr(ast, 'unparse') else code
            return normalized
        except Exception:
            # If parsing fails, return original code
            return code


class FunctionSignatureExtractor(ast.NodeVisitor):
    """AST visitor to extract function signatures for similarity analysis."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.signatures: List[FunctionSignature] = []
    
    def visit_FunctionDef(self, node):
        """Visit a function definition."""
        self._extract_signature(node)
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        """Visit an async function definition."""
        self._extract_signature(node)
        self.generic_visit(node)
    
    def _extract_signature(self, node) -> None:
        """Extract function signature information."""
        try:
            # Extract parameters
            parameters = []
            for arg in node.args.args:
                param_name = arg.arg
                if arg.annotation:
                    param_name += f": {ast.unparse(arg.annotation) if hasattr(ast, 'unparse') else 'annotated'}"
                parameters.append(param_name)
            
            # Extract return annotation
            return_annotation = ""
            if node.returns:
                return_annotation = ast.unparse(node.returns) if hasattr(ast, 'unparse') else "annotated"
            
            # Extract docstring
            docstring = ""
            if (node.body and isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, ast.Constant) and 
                isinstance(node.body[0].value.value, str)):
                docstring = node.body[0].value.value
            
            # Generate body hash (excluding docstring)
            body_nodes = node.body[1:] if docstring else node.body
            body_hash = self._generate_body_hash(body_nodes)
            
            # Calculate complexity score (simple metric)
            complexity_score = self._calculate_complexity(node)
            
            signature = FunctionSignature(
                name=node.name,
                file_path=self.file_path,
                line_number=node.lineno,
                parameters=parameters,
                return_annotation=return_annotation,
                docstring=docstring,
                body_hash=body_hash,
                complexity_score=complexity_score
            )
            
            self.signatures.append(signature)
            
        except Exception as e:
            # Skip functions that can't be processed
            pass
    
    def _generate_body_hash(self, body_nodes: List[ast.stmt]) -> str:
        """Generate a hash of the function body."""
        try:
            body_str = ""
            for node in body_nodes:
                body_str += ast.dump(node, annotate_fields=False, include_attributes=False)
            return hashlib.md5(body_str.encode()).hexdigest()
        except Exception:
            return ""
    
    def _calculate_complexity(self, node) -> int:
        """Calculate a simple complexity score for the function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Add complexity for control flow statements
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity


if __name__ == "__main__":
    # Test the DuplicateAnalyzer
    import sys
    import logging
    from project_cleanup_analyzer import AnalysisConfig
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Test with current directory
    project_path = "."
    
    try:
        config = AnalysisConfig(project_path=project_path)
        analyzer = DuplicateAnalyzer(config)
        
        print(f"Testing {analyzer.get_analyzer_name()}...")
        results = analyzer.analyze(project_path)
        
        print(f"Analysis complete. Found {len(results)} results:")
        
        # Group results by category
        by_category = {}
        for result in results:
            if result.category not in by_category:
                by_category[result.category] = []
            by_category[result.category].append(result)
        
        for category, category_results in by_category.items():
            print(f"\n{category.upper()} ({len(category_results)} issues):")
            for result in category_results[:3]:  # Show only first 3 results per category
                print(f"  - {result.severity.upper()}: {result.description}")
                if result.recommendation:
                    print(f"    Recommendation: {result.recommendation}")
            
            if len(category_results) > 3:
                print(f"    ... and {len(category_results) - 3} more issues")
        
        # Print duplicate summary
        summary = analyzer.get_duplicate_summary()
        print(f"\nDUPLICATE ANALYSIS SUMMARY:")
        print(f"  Total code blocks analyzed: {summary['total_code_blocks']}")
        print(f"  Total functions analyzed: {summary['total_functions']}")
        print(f"  Duplicate groups found: {summary['duplicate_groups']}")
        print(f"  Exact duplicates: {summary['exact_duplicates']}")
        print(f"  Similar blocks: {summary['similar_blocks']}")
        print(f"  Files with duplicates: {summary['files_with_duplicates']}")
        
        if analyzer.error_handler.has_errors():
            print(f"\nErrors encountered: {analyzer.error_handler.get_error_summary()}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)