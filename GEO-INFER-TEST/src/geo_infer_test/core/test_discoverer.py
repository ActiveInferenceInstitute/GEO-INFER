"""
Test discovery module for GEO-INFER-TEST.

This module provides intelligent test discovery capabilities across all
GEO-INFER modules, supporting various test types and patterns.
"""

import os
import importlib
import inspect
from typing import Dict, List, Set, Optional, Tuple
from pathlib import Path
import ast
import re


class TestDiscoverer:
    """
    Intelligent test discovery system for the GEO-INFER ecosystem.
    
    Discovers and catalogs all available tests across modules, supporting
    multiple test types and frameworks.
    """
    
    SUPPORTED_TEST_TYPES = ['unit', 'integration', 'performance', 'load', 'stress']
    TEST_FILE_PATTERNS = [
        r'test_.*\.py$',
        r'.*_test\.py$',
        r'test.*\.py$'
    ]
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize the test discoverer."""
        self.base_path = base_path or Path.cwd()
        self.discovered_tests: Dict[str, Dict[str, List[str]]] = {}
        self.test_metadata: Dict[str, Dict] = {}
    
    def discover_all_tests(self, modules: List[str]) -> Dict[str, Dict[str, List[str]]]:
        """
        Discover all tests for the specified modules.
        
        Args:
            modules: List of module names to discover tests for
            
        Returns:
            Dictionary mapping module names to test types to test files
        """
        discovered = {}
        
        for module in modules:
            if module == 'ALL':
                # Discover all available modules
                available_modules = self._find_all_modules()
                for mod in available_modules:
                    module_tests = self._discover_module_tests(mod)
                    if module_tests:
                        discovered[mod] = module_tests
            else:
                module_tests = self._discover_module_tests(module)
                if module_tests:
                    discovered[module] = module_tests
        
        self.discovered_tests = discovered
        return discovered
    
    def _find_all_modules(self) -> List[str]:
        """Find all available GEO-INFER modules."""
        modules = []
        
        # Look for GEO-INFER-* directories
        for item in self.base_path.iterdir():
            if item.is_dir() and item.name.startswith('GEO-INFER-'):
                module_name = item.name.replace('GEO-INFER-', '')
                modules.append(module_name)
        
        return sorted(modules)
    
    def _discover_module_tests(self, module: str) -> Dict[str, List[str]]:
        """Discover tests for a specific module."""
        module_tests = {}
        module_path = self.base_path / f'GEO-INFER-{module}'
        
        if not module_path.exists():
            return module_tests
        
        tests_path = module_path / 'tests'
        if not tests_path.exists():
            return module_tests
        
        # Discover tests by type
        for test_type in self.SUPPORTED_TEST_TYPES:
            test_type_path = tests_path / test_type
            if test_type_path.exists():
                test_files = self._find_test_files(test_type_path)
                if test_files:
                    module_tests[test_type] = test_files
        
        # Also check for tests directly in the tests directory
        root_test_files = self._find_test_files(tests_path)
        if root_test_files:
            module_tests['general'] = root_test_files
        
        return module_tests
    
    def _find_test_files(self, directory: Path) -> List[str]:
        """Find test files in a directory."""
        test_files = []
        
        if not directory.exists():
            return test_files
        
        for file_path in directory.rglob('*.py'):
            if self._is_test_file(file_path):
                # Store relative path from the tests directory
                relative_path = file_path.relative_to(directory)
                test_files.append(str(relative_path))
        
        return sorted(test_files)
    
    def _is_test_file(self, file_path: Path) -> bool:
        """Check if a file is a test file based on naming patterns."""
        filename = file_path.name
        
        # Check against common test file patterns
        for pattern in self.TEST_FILE_PATTERNS:
            if re.match(pattern, filename):
                return True
        
        return False
    
    def analyze_test_file(self, file_path: Path) -> Dict:
        """Analyze a test file to extract metadata."""
        metadata = {
            'functions': [],
            'classes': [],
            'imports': [],
            'dependencies': [],
            'docstring': None,
            'framework': 'unknown'
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the AST
            tree = ast.parse(content)
            
            # Extract module docstring
            if (tree.body and isinstance(tree.body[0], ast.Expr) and
                isinstance(tree.body[0].value, ast.Str)):
                metadata['docstring'] = tree.body[0].value.s
            
            # Analyze the AST
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        metadata['functions'].append({
                            'name': node.name,
                            'line': node.lineno,
                            'docstring': ast.get_docstring(node)
                        })
                
                elif isinstance(node, ast.ClassDef):
                    if 'test' in node.name.lower():
                        metadata['classes'].append({
                            'name': node.name,
                            'line': node.lineno,
                            'docstring': ast.get_docstring(node)
                        })
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        metadata['imports'].append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        metadata['imports'].append(node.module)
            
            # Detect testing framework
            metadata['framework'] = self._detect_framework(metadata['imports'])
            
        except Exception:
            # If we can't parse the file, that's okay
            pass
        
        return metadata
    
    def _detect_framework(self, imports: List[str]) -> str:
        """Detect the testing framework being used."""
        frameworks = {
            'pytest': ['pytest'],
            'unittest': ['unittest'],
            'nose': ['nose', 'nose2'],
            'hypothesis': ['hypothesis'],
            'locust': ['locust'],
            'selenium': ['selenium']
        }
        
        for framework, patterns in frameworks.items():
            for pattern in patterns:
                if any(pattern in imp for imp in imports):
                    return framework
        
        return 'unknown'
    
    def get_test_statistics(self) -> Dict:
        """Get statistics about discovered tests."""
        stats = {
            'total_modules': len(self.discovered_tests),
            'total_test_files': 0,
            'tests_by_type': {},
            'tests_by_module': {}
        }
        
        for module, test_types in self.discovered_tests.items():
            module_total = sum(len(files) for files in test_types.values())
            stats['tests_by_module'][module] = module_total
            stats['total_test_files'] += module_total
            
            for test_type, files in test_types.items():
                if test_type not in stats['tests_by_type']:
                    stats['tests_by_type'][test_type] = 0
                stats['tests_by_type'][test_type] += len(files)
        
        return stats
    
    def find_cross_module_tests(self) -> List[Tuple[str, str, str]]:
        """Find tests that appear to test cross-module functionality."""
        cross_module_tests = []
        
        for module, test_types in self.discovered_tests.items():
            for test_type, files in test_types.items():
                for file_path in files:
                    # Check if the test file mentions other modules
                    full_path = self.base_path / f'GEO-INFER-{module}' / 'tests' / test_type / file_path
                    
                    if full_path.exists():
                        metadata = self.analyze_test_file(full_path)
                        
                        # Look for imports of other GEO-INFER modules
                        for import_name in metadata['imports']:
                            if 'geo_infer_' in import_name:
                                imported_module = import_name.replace('geo_infer_', '').upper()
                                if imported_module != module:
                                    cross_module_tests.append((module, imported_module, file_path))
        
        return cross_module_tests
    
    def validate_test_structure(self) -> Dict[str, List[str]]:
        """Validate the structure of discovered tests."""
        issues = {
            'missing_test_dirs': [],
            'empty_test_dirs': [],
            'malformed_test_files': [],
            'missing_init_files': []
        }
        
        for module in self._find_all_modules():
            module_path = self.base_path / f'GEO-INFER-{module}'
            tests_path = module_path / 'tests'
            
            if not tests_path.exists():
                issues['missing_test_dirs'].append(module)
                continue
            
            # Check for empty test directories
            test_files = list(tests_path.rglob('test_*.py'))
            if not test_files:
                issues['empty_test_dirs'].append(module)
            
            # Check for __init__.py files in test directories
            for test_type in self.SUPPORTED_TEST_TYPES:
                test_type_path = tests_path / test_type
                if test_type_path.exists() and test_type_path.is_dir():
                    init_file = test_type_path / '__init__.py'
                    if not init_file.exists():
                        issues['missing_init_files'].append(f"{module}/{test_type}")
        
        return issues 