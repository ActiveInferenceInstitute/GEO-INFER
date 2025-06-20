#!/usr/bin/env python3
"""
Comprehensive Integration Example Assessment Tool

Systematically runs all GEO-INFER integration examples and generates detailed reports.
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ExampleAssessment:
    """Assessment result for a single example."""
    name: str
    category: str
    status: str  # 'implemented', 'partial', 'missing', 'error'
    has_readme: bool = False
    has_script: bool = False
    has_config: bool = False
    has_tests: bool = False
    documentation_quality: float = 0.0
    modules_identified: List[str] = field(default_factory=list)
    complexity_score: int = 1
    recommendations: List[str] = field(default_factory=list)

class IntegrationAssessor:
    """Comprehensive assessment tool for integration examples."""
    
    def __init__(self, examples_dir: Path):
        self.examples_dir = examples_dir
        self.assessments: List[ExampleAssessment] = []
        self.logger = self._setup_logging()
        
        # Known GEO-INFER modules
        self.modules = [
            'DATA', 'SPACE', 'TIME', 'AI', 'HEALTH', 'AG', 'IOT', 'RISK',
            'API', 'APP', 'BAYES', 'ACT', 'AGENT', 'SIM', 'ECON', 'CIV',
            'NORMS', 'ORG', 'BIO', 'COMMS', 'LOG', 'MATH', 'OPS', 'SEC'
        ]
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for assessment."""
        logger = logging.getLogger('integration_assessor')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def assess_example(self, example_path: Path) -> ExampleAssessment:
        """Assess a single integration example."""
        category = example_path.parent.name
        name = example_path.name
        
        assessment = ExampleAssessment(
            name=name,
            category=category,
            status='missing'
        )
        
        try:
            # Check for README
            readme_path = example_path / 'README.md'
            if readme_path.exists():
                assessment.has_readme = True
                assessment.documentation_quality += 0.3
                
                # Analyze README content
                try:
                    content = readme_path.read_text()
                    
                    # Look for modules mentioned
                    for module in self.modules:
                        if f'GEO-INFER-{module}' in content or module in content:
                            if module not in assessment.modules_identified:
                                assessment.modules_identified.append(module)
                    
                    # Quality indicators
                    if 'Learning Objectives' in content:
                        assessment.documentation_quality += 0.1
                    if 'Modules Used' in content:
                        assessment.documentation_quality += 0.1
                    if 'Integration' in content:
                        assessment.documentation_quality += 0.1
                    if len(content) > 1000:
                        assessment.documentation_quality += 0.2
                    if '```python' in content:
                        assessment.documentation_quality += 0.1
                    if 'mermaid' in content.lower():
                        assessment.documentation_quality += 0.1
                    
                except Exception as e:
                    self.logger.warning(f"Error reading README for {name}: {e}")
            
            # Check for executable scripts
            script_paths = [
                example_path / 'scripts' / 'run_example.py',
                example_path / 'scripts' / f'run_{name}.py',
                example_path / 'run_example.py',
                example_path / 'main.py'
            ]
            
            for script_path in script_paths:
                if script_path.exists():
                    assessment.has_script = True
                    break
            
            # Check for configuration
            config_paths = [
                example_path / 'config',
                example_path / 'config.yaml',
                example_path / 'config.json'
            ]
            
            for config_path in config_paths:
                if config_path.exists():
                    assessment.has_config = True
                    break
            
            # Check for tests
            test_paths = [
                example_path / 'tests',
                example_path / 'test_example.py',
                example_path / 'test_integration.py'
            ]
            
            for test_path in test_paths:
                if test_path.exists():
                    assessment.has_tests = True
                    break
            
            # Determine status
            if assessment.has_readme and assessment.has_script:
                assessment.status = 'implemented'
            elif assessment.has_readme:
                assessment.status = 'partial'
            else:
                assessment.status = 'missing'
            
            # Calculate complexity
            assessment.complexity_score = min(len(assessment.modules_identified), 5)
            
            # Generate recommendations
            if not assessment.has_readme:
                assessment.recommendations.append("Add comprehensive README.md")
            if not assessment.has_script:
                assessment.recommendations.append("Implement runnable example script")
            if not assessment.has_config:
                assessment.recommendations.append("Add configuration files")
            if not assessment.has_tests:
                assessment.recommendations.append("Add integration tests")
            if assessment.documentation_quality < 0.7:
                assessment.recommendations.append("Improve documentation quality")
            
        except Exception as e:
            assessment.status = 'error'
            assessment.recommendations.append(f"Fix assessment error: {e}")
            self.logger.error(f"Error assessing {name}: {e}")
        
        return assessment
    
    def run_comprehensive_assessment(self) -> Dict[str, Any]:
        """Run comprehensive assessment of all examples."""
        self.logger.info("Starting comprehensive integration example assessment...")
        
        start_time = time.time()
        
        # Discover all example directories
        example_dirs = []
        for category_dir in self.examples_dir.iterdir():
            if not category_dir.is_dir():
                continue
            
            for example_dir in category_dir.iterdir():
                if example_dir.is_dir():
                    example_dirs.append(example_dir)
        
        self.logger.info(f"Found {len(example_dirs)} potential examples")
        
        # Assess each example
        for example_dir in example_dirs:
            assessment = self.assess_example(example_dir)
            self.assessments.append(assessment)
            
            status_emoji = {
                'implemented': '✅',
                'partial': '🟡',
                'missing': '❌',
                'error': '💥'
            }.get(assessment.status, '❓')
            
            self.logger.info(f"{status_emoji} {assessment.category}/{assessment.name} - {assessment.status}")
        
        execution_time = time.time() - start_time
        
        # Generate comprehensive report
        report = self._generate_report(execution_time)
        
        # Save results
        self._save_results(report)
        
        return report
    
    def _generate_report(self, execution_time: float) -> Dict[str, Any]:
        """Generate comprehensive assessment report."""
        # Calculate statistics
        total_examples = len(self.assessments)
        implemented = len([a for a in self.assessments if a.status == 'implemented'])
        partial = len([a for a in self.assessments if a.status == 'partial'])
        missing = len([a for a in self.assessments if a.status == 'missing'])
        errors = len([a for a in self.assessments if a.status == 'error'])
        
        # Module usage statistics
        module_usage = {}
        for assessment in self.assessments:
            for module in assessment.modules_identified:
                module_usage[module] = module_usage.get(module, 0) + 1
        
        # Category statistics
        category_stats = {}
        for assessment in self.assessments:
            category = assessment.category
            if category not in category_stats:
                category_stats[category] = {
                    'total': 0, 'implemented': 0, 'partial': 0, 'missing': 0, 'error': 0
                }
            category_stats[category]['total'] += 1
            category_stats[category][assessment.status] += 1
        
        # Documentation quality analysis
        avg_doc_quality = (
            sum(a.documentation_quality for a in self.assessments) / total_examples
            if total_examples > 0 else 0
        )
        
        # Generate overall recommendations
        overall_recommendations = []
        
        implementation_rate = implemented / total_examples * 100 if total_examples > 0 else 0
        if implementation_rate < 50:
            overall_recommendations.append(
                "🚨 LOW IMPLEMENTATION RATE: Less than 50% of examples are fully implemented"
            )
        elif implementation_rate < 80:
            overall_recommendations.append(
                "⚠️ MODERATE IMPLEMENTATION RATE: Some examples need completion"
            )
        
        if avg_doc_quality < 0.6:
            overall_recommendations.append(
                "📚 DOCUMENTATION NEEDS IMPROVEMENT: Average quality is below 60%"
            )
        
        if missing > 0:
            overall_recommendations.append(
                f"🏗️ IMPLEMENT MISSING EXAMPLES: {missing} examples need basic implementation"
            )
        
        if partial > 0:
            overall_recommendations.append(
                f"🔧 COMPLETE PARTIAL EXAMPLES: {partial} examples need executable scripts"
            )
        
        return {
            'timestamp': datetime.now().isoformat(),
            'execution_time': execution_time,
            'summary': {
                'total_examples': total_examples,
                'implemented': implemented,
                'partial': partial,
                'missing': missing,
                'errors': errors,
                'implementation_rate': implementation_rate,
                'average_documentation_quality': avg_doc_quality
            },
            'category_statistics': category_stats,
            'module_usage': module_usage,
            'overall_recommendations': overall_recommendations,
            'detailed_assessments': [
                {
                    'name': a.name,
                    'category': a.category,
                    'status': a.status,
                    'has_readme': a.has_readme,
                    'has_script': a.has_script,
                    'has_config': a.has_config,
                    'has_tests': a.has_tests,
                    'documentation_quality': a.documentation_quality,
                    'modules_identified': a.modules_identified,
                    'complexity_score': a.complexity_score,
                    'recommendations': a.recommendations
                }
                for a in self.assessments
            ]
        }
    
    def _save_results(self, report: Dict[str, Any]) -> None:
        """Save assessment results."""
        # Create results directory
        results_dir = self.examples_dir.parent / 'assessment_results'
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save JSON report
        json_file = results_dir / f'integration_assessment_{timestamp}.json'
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save markdown summary
        md_file = results_dir / f'integration_summary_{timestamp}.md'
        self._generate_markdown_summary(report, md_file)
        
        # Save latest (overwrite)
        latest_json = results_dir / 'latest_assessment.json'
        with open(latest_json, 'w') as f:
            json.dump(report, f, indent=2)
        
        latest_md = results_dir / 'latest_summary.md'
        self._generate_markdown_summary(report, latest_md)
        
        self.logger.info(f"Results saved to {results_dir}")
    
    def _generate_markdown_summary(self, report: Dict[str, Any], output_file: Path) -> None:
        """Generate markdown summary report."""
        with open(output_file, 'w') as f:
            f.write("# GEO-INFER Integration Examples Assessment\n\n")
            f.write(f"**Generated**: {report['timestamp']}\n")
            f.write(f"**Assessment Time**: {report['execution_time']:.2f} seconds\n\n")
            
            # Executive Summary
            summary = report['summary']
            f.write("## 📊 Executive Summary\n\n")
            f.write(f"- **Total Examples**: {summary['total_examples']}\n")
            f.write(f"- **Fully Implemented**: {summary['implemented']} ({summary['implementation_rate']:.1f}%)\n")
            f.write(f"- **Partially Implemented**: {summary['partial']}\n")
            f.write(f"- **Missing Implementation**: {summary['missing']}\n")
            f.write(f"- **Errors**: {summary['errors']}\n")
            f.write(f"- **Average Documentation Quality**: {summary['average_documentation_quality']:.1%}\n\n")
            
            # Status indicator
            impl_rate = summary['implementation_rate']
            if impl_rate >= 80:
                status = "🟢 EXCELLENT"
            elif impl_rate >= 60:
                status = "🟡 GOOD"
            else:
                status = "🔴 NEEDS IMPROVEMENT"
            
            f.write(f"### Overall Status: {status}\n\n")
            
            # Key Recommendations
            f.write("## 🎯 Key Recommendations\n\n")
            for i, rec in enumerate(report['overall_recommendations'], 1):
                f.write(f"{i}. {rec}\n")
            f.write("\n")
            
            # Category Statistics
            f.write("## 📂 Category Analysis\n\n")
            f.write("| Category | Total | Implemented | Partial | Missing | Success Rate |\n")
            f.write("|----------|-------|-------------|---------|---------|-------------|\n")
            
            for category, stats in report['category_statistics'].items():
                success_rate = stats['implemented'] / stats['total'] * 100 if stats['total'] > 0 else 0
                f.write(f"| {category} | {stats['total']} | {stats['implemented']} | {stats['partial']} | {stats['missing']} | {success_rate:.1f}% |\n")
            f.write("\n")
            
            # Module Usage
            f.write("## 🔧 Module Usage Analysis\n\n")
            f.write("| Module | Usage Count | Coverage |\n")
            f.write("|--------|-------------|----------|\n")
            
            total_examples = summary['total_examples']
            for module, count in sorted(report['module_usage'].items(), key=lambda x: x[1], reverse=True):
                coverage = count / total_examples * 100 if total_examples > 0 else 0
                f.write(f"| {module} | {count} | {coverage:.1f}% |\n")
            f.write("\n")
            
            # Detailed Results by Status
            f.write("## 📋 Detailed Results\n\n")
            
            assessments = report['detailed_assessments']
            
            for status in ['implemented', 'partial', 'missing', 'error']:
                status_assessments = [a for a in assessments if a['status'] == status]
                if not status_assessments:
                    continue
                
                status_emoji = {
                    'implemented': '✅',
                    'partial': '🟡',
                    'missing': '❌',
                    'error': '💥'
                }[status]
                
                f.write(f"### {status_emoji} {status.title()} Examples ({len(status_assessments)})\n\n")
                
                for assessment in status_assessments:
                    f.write(f"#### {assessment['category']}/{assessment['name']}\n")
                    f.write(f"- **Documentation Quality**: {assessment['documentation_quality']:.1%}\n")
                    f.write(f"- **Modules Identified**: {', '.join(assessment['modules_identified']) if assessment['modules_identified'] else 'None'}\n")
                    f.write(f"- **Complexity Score**: {assessment['complexity_score']}/5\n")
                    f.write(f"- **Components**: README: {'✅' if assessment['has_readme'] else '❌'}, Script: {'✅' if assessment['has_script'] else '❌'}, Config: {'✅' if assessment['has_config'] else '❌'}, Tests: {'✅' if assessment['has_tests'] else '❌'}\n")
                    
                    if assessment['recommendations']:
                        f.write(f"- **Recommendations**: {'; '.join(assessment['recommendations'])}\n")
                    
                    f.write("\n")
            
            f.write("---\n")
            f.write("*Generated by GEO-INFER Integration Assessment Tool*\n")

def main():
    """Main function to run assessment."""
    print("🔍 GEO-INFER Integration Examples Assessment")
    print("=" * 50)
    
    examples_dir = Path(__file__).parent.parent / 'examples'
    assessor = IntegrationAssessor(examples_dir)
    
    try:
        report = assessor.run_comprehensive_assessment()
        
        # Display key results
        summary = report['summary']
        print(f"\n📊 Assessment Results:")
        print(f"Total Examples: {summary['total_examples']}")
        print(f"Implemented: {summary['implemented']} ({summary['implementation_rate']:.1f}%)")
        print(f"Partial: {summary['partial']}")
        print(f"Missing: {summary['missing']}")
        print(f"Documentation Quality: {summary['average_documentation_quality']:.1%}")
        
        print(f"\n🎯 Top Recommendations:")
        for rec in report['overall_recommendations'][:3]:
            print(f"- {rec}")
        
        print(f"\n📁 Detailed report saved to: assessment_results/")
        
        return 0
        
    except Exception as e:
        print(f"❌ Assessment failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 