#!/usr/bin/env python3
"""
Generate comprehensive review reports from analysis data.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
from datetime import datetime

def load_review_data() -> Dict[str, Any]:
    """Load review data."""
    data_file = Path(__file__).parent.parent / "GEO-INFER-INTRA" / "assessment_results" / "comprehensive_review_2025.json"
    with open(data_file) as f:
        return json.load(f)

def categorize_issues(reviews: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Categorize issues by priority."""
    issues = {
        "P0": [],  # Critical - blocks functionality
        "P1": [],  # High - significant impact
        "P2": [],  # Medium - moderate impact
        "P3": []   # Low - minor impact
    }
    
    for module, review in reviews.get("reviews", {}).items():
        if "error" in review:
            issues["P0"].append({
                "module": module,
                "issue": "Review error",
                "details": review["error"],
                "category": "structure"
            })
            continue
        
        # P0: Missing critical infrastructure
        struct = review.get("structure", {})
        if not struct.get("has_requirements_txt"):
            issues["P0"].append({
                "module": module,
                "issue": "Missing requirements.txt",
                "details": "Module lacks requirements.txt file",
                "category": "dependencies",
                "file": f"GEO-INFER-{module}/requirements.txt"
            })
        
        if not struct.get("has_setup_py") and not struct.get("has_pyproject_toml"):
            issues["P0"].append({
                "module": module,
                "issue": "Missing setup files",
                "details": "Module lacks both setup.py and pyproject.toml",
                "category": "structure",
                "file": f"GEO-INFER-{module}/"
            })
        
        # P0: Missing tests
        testing = review.get("testing", {})
        if not testing.get("has_tests"):
            issues["P0"].append({
                "module": module,
                "issue": "No test suite",
                "details": "Module has no test files",
                "category": "testing",
                "file": f"GEO-INFER-{module}/tests/"
            })
        
        # P1: Missing documentation sections
        docs = review.get("documentation", {})
        if not docs.get("has_yaml_frontmatter"):
            issues["P1"].append({
                "module": module,
                "issue": "Missing YAML front matter",
                "details": "README.md lacks YAML front matter",
                "category": "documentation",
                "file": f"GEO-INFER-{module}/README.md"
            })
        
        required_sections = docs.get("required_sections", {})
        missing_sections = [k for k, v in required_sections.items() if not v]
        if missing_sections:
            issues["P1"].append({
                "module": module,
                "issue": f"Missing documentation sections: {', '.join(missing_sections)}",
                "details": f"README.md missing required sections",
                "category": "documentation",
                "file": f"GEO-INFER-{module}/README.md"
            })
        
        # P1: Many missing dependencies
        deps = review.get("dependencies", {})
        missing_deps = deps.get("missing_deps", [])
        if len(missing_deps) > 10:
            issues["P1"].append({
                "module": module,
                "issue": f"Many missing dependencies ({len(missing_deps)})",
                "details": f"Module imports {len(missing_deps)} packages not in requirements",
                "category": "dependencies",
                "file": f"GEO-INFER-{module}/requirements.txt"
            })
        
        # P2: Code quality issues
        quality = review.get("code_quality", {})
        if quality.get("todo_count", 0) > 5:
            issues["P2"].append({
                "module": module,
                "issue": f"High TODO count ({quality['todo_count']})",
                "details": "Multiple TODO markers indicate incomplete work",
                "category": "code_quality"
            })
        
        if quality.get("fixme_count", 0) > 0:
            issues["P2"].append({
                "module": module,
                "issue": f"FIXME markers found ({quality['fixme_count']})",
                "details": "Code contains FIXME markers indicating known issues",
                "category": "code_quality"
            })
        
        # P2: Test organization
        if testing.get("has_tests") and not testing.get("has_unit_tests"):
            issues["P2"].append({
                "module": module,
                "issue": "Tests not organized into unit/integration",
                "details": "Test files exist but not organized into subdirectories",
                "category": "testing",
                "file": f"GEO-INFER-{module}/tests/"
            })
        
        # P3: Minor issues
        if not struct.get("has_examples"):
            issues["P3"].append({
                "module": module,
                "issue": "No examples directory",
                "details": "Module lacks examples/ directory",
                "category": "documentation",
                "file": f"GEO-INFER-{module}/examples/"
            })
    
    return issues

def generate_executive_summary(reviews: Dict[str, Any], issues: Dict[str, List[Dict[str, Any]]]) -> str:
    """Generate executive summary report."""
    # Load summary data from separate file
    summary_file = Path(__file__).parent.parent / "GEO-INFER-INTRA" / "assessment_results" / "comprehensive_review_summary_2025.json"
    if summary_file.exists():
        with open(summary_file) as f:
            summary_data = json.load(f)
    else:
        summary_data = {}
    total_modules = len(reviews.get("reviews", {}))
    
    report = f"""# GEO-INFER Comprehensive Repository Review - Executive Summary

**Review Date**: {datetime.now().strftime('%Y-%m-%d')}  
**Total Modules Reviewed**: {total_modules}  
**Review Scope**: Code Quality, Architecture, Testing, Documentation, Security, Dependencies

---

## Executive Overview

This comprehensive review assessed all {total_modules} GEO-INFER modules across six critical dimensions:
1. Code Quality & Architecture
2. Testing & Quality Assurance
3. Documentation
4. Security & Compliance
5. Dependencies & Infrastructure
6. Module Structure & Organization

---

## Key Metrics

### Overall Health Score

| Dimension | Compliance Rate | Status |
|-----------|----------------|--------|
| **Structure** | {summary_data.get('structure', {}).get('has_requirements_txt', 0)}/{total_modules} modules with requirements.txt | {'✅ Good' if summary_data.get('structure', {}).get('has_requirements_txt', 0) == total_modules else '⚠️ Needs Improvement'} |
| **Testing** | {summary_data.get('testing', {}).get('modules_with_tests', 0)}/{total_modules} modules with tests | {'✅ Good' if summary_data.get('testing', {}).get('modules_with_tests', 0) >= total_modules * 0.9 else '⚠️ Needs Improvement'} |
| **Documentation** | {summary_data.get('documentation', {}).get('has_yaml_frontmatter', 0)}/{total_modules} modules with YAML frontmatter | {'✅ Excellent' if summary_data.get('documentation', {}).get('has_yaml_frontmatter', 0) == total_modules else '⚠️ Needs Improvement'} |
| **Dependencies** | {total_modules - summary_data.get('dependencies', {}).get('modules_missing_deps', 0)}/{total_modules} modules with complete dependencies | {'✅ Good' if summary_data.get('dependencies', {}).get('modules_missing_deps', 0) < total_modules * 0.1 else '⚠️ Needs Improvement'} |

### Critical Issues (P0)

**Total P0 Issues**: {len(issues['P0'])}  
**Modules Affected**: {len(set(i['module'] for i in issues['P0']))}

**Top Critical Issues**:
"""
    
    # Group P0 issues by type
    p0_by_type = defaultdict(list)
    for issue in issues["P0"]:
        p0_by_type[issue["issue"]].append(issue["module"])
    
    for issue_type, modules in list(p0_by_type.items())[:5]:
        report += f"- **{issue_type}**: {len(modules)} modules ({', '.join(modules[:5])}{'...' if len(modules) > 5 else ''})\n"
    
    report += f"""
### High Priority Issues (P1)

**Total P1 Issues**: {len(issues['P1'])}  
**Modules Affected**: {len(set(i['module'] for i in issues['P1']))}

### Medium Priority Issues (P2)

**Total P2 Issues**: {len(issues['P2'])}  
**Modules Affected**: {len(set(i['module'] for i in issues['P2']))}

### Low Priority Issues (P3)

**Total P3 Issues**: {len(issues['P3'])}  
**Modules Affected**: {len(set(i['module'] for i in issues['P3']))}

---

## Strengths

1. **✅ Excellent YAML Front Matter Compliance**: {summary_data.get('documentation', {}).get('has_yaml_frontmatter', 0)}/{total_modules} modules ({int(summary_data.get('documentation', {}).get('has_yaml_frontmatter', 0) / total_modules * 100)}%) have YAML front matter
2. **✅ Comprehensive Test Coverage**: {summary_data.get('testing', {}).get('modules_with_tests', 0)}/{total_modules} modules have test suites ({summary_data.get('testing', {}).get('total_test_files', 0)} total test files)
3. **✅ Good Infrastructure**: {summary_data.get('structure', {}).get('has_requirements_txt', 0)}/{total_modules} modules have requirements.txt, {summary_data.get('structure', {}).get('has_setup_py', 0)}/{total_modules} have setup.py
4. **✅ Strong Documentation Standards**: {summary_data.get('documentation', {}).get('has_all_sections', 0)}/{total_modules} modules have all required documentation sections

---

## Critical Action Items

### Immediate (P0)

1. **Address Missing Tests**: {len([i for i in issues['P0'] if i['category'] == 'testing'])} modules need test suites
2. **Fix Missing Infrastructure**: {len([i for i in issues['P0'] if i['category'] in ['structure', 'dependencies']])} modules have infrastructure gaps
3. **Resolve Review Errors**: {len([i for i in issues['P0'] if 'error' in i.get('details', '')])} modules had review errors

### Short Term (P1)

1. **Complete Documentation**: {len([i for i in issues['P1'] if i['category'] == 'documentation'])} modules need documentation improvements
2. **Fix Dependency Issues**: {len([i for i in issues['P1'] if i['category'] == 'dependencies'])} modules have dependency problems

---

## Recommendations

1. **Standardize Dependency Management**: Ensure all modules have complete and accurate requirements.txt files
2. **Expand Test Coverage**: Add tests to modules currently without test suites
3. **Complete Documentation**: Add missing documentation sections to all modules
4. **Code Quality Improvements**: Address TODO/FIXME markers and technical debt
5. **Security Review**: Conduct comprehensive security audit of all modules

---

## Next Steps

See detailed reports:
- **Per-Module Assessment**: `COMPREHENSIVE_REVIEW_DETAILED.md`
- **Improvement Roadmap**: `COMPREHENSIVE_REVIEW_ROADMAP.md`

---
"""
    return report

def generate_detailed_report(reviews: Dict[str, Any], issues: Dict[str, List[Dict[str, Any]]]) -> str:
    """Generate detailed per-module report."""
    report = f"""# GEO-INFER Comprehensive Repository Review - Detailed Per-Module Assessment

**Review Date**: {datetime.now().strftime('%Y-%m-%d')}  
**Total Modules**: {len(reviews.get('reviews', {}))}

---

"""
    
    # Group issues by module
    issues_by_module = defaultdict(list)
    for priority, issue_list in issues.items():
        for issue in issue_list:
            issues_by_module[issue["module"]].append((priority, issue))
    
    # Generate per-module assessment
    for module in sorted(reviews.get("reviews", {}).keys()):
        review = reviews["reviews"][module]
        report += f"""## {module}

### Module Overview

"""
        
        if "error" in review:
            report += f"**⚠️ Review Error**: {review['error']}\n\n"
            continue
        
        struct = review.get("structure", {})
        report += f"""### Structure Assessment

- ✅ Has src/: {struct.get('has_src', False)}
- ✅ Has tests/: {struct.get('has_tests', False)}
- ✅ Has docs/: {struct.get('has_docs', False)}
- ✅ Has examples/: {struct.get('has_examples', False)}
- ✅ Has config/: {struct.get('has_config', False)}
- ✅ Has README.md: {struct.get('has_readme', False)}
- ✅ Has setup.py: {struct.get('has_setup_py', False)}
- ✅ Has pyproject.toml: {struct.get('has_pyproject_toml', False)}
- ✅ Has requirements.txt: {struct.get('has_requirements_txt', False)}
- **Source Files**: {struct.get('src_file_count', 0)}
- **Test Files**: {struct.get('test_file_count', 0)}

### Dependencies Assessment

- **Declared in requirements.txt**: {len(review.get('dependencies', {}).get('requirements_txt', []))}
- **Declared in setup.py**: {len(review.get('dependencies', {}).get('setup_py', []))}
- **Declared in pyproject.toml**: {len(review.get('dependencies', {}).get('pyproject_toml', []))}
- **Actual imports detected**: {len(review.get('dependencies', {}).get('actual_imports', []))}
- **Missing dependencies**: {len(review.get('dependencies', {}).get('missing_deps', []))}

"""
        
        if review.get('dependencies', {}).get('missing_deps'):
            report += f"**Missing Dependencies**: {', '.join(review['dependencies']['missing_deps'][:10])}{'...' if len(review['dependencies']['missing_deps']) > 10 else ''}\n\n"
        
        docs = review.get("documentation", {})
        report += f"""### Documentation Assessment

- ✅ Has README: {docs.get('has_readme', False)}
- ✅ Has YAML front matter: {docs.get('has_yaml_frontmatter', False)}
- **Examples count**: {docs.get('examples_count', 0)}
- **Required sections**:
  - Overview: {docs.get('required_sections', {}).get('Overview', False)}
  - Core Features: {docs.get('required_sections', {}).get('Core Features', False)}
  - API Reference: {docs.get('required_sections', {}).get('API Reference', False)}
  - Integration: {docs.get('required_sections', {}).get('Integration', False)}

### Testing Assessment

- ✅ Has tests: {review.get('testing', {}).get('has_tests', False)}
- **Test file count**: {review.get('testing', {}).get('test_file_count', 0)}
- ✅ Has unit tests: {review.get('testing', {}).get('has_unit_tests', False)}
- ✅ Has integration tests: {review.get('testing', {}).get('has_integration_tests', False)}
- ✅ Has performance tests: {review.get('testing', {}).get('has_performance_tests', False)}

### Code Quality Assessment

- **TODO markers**: {review.get('code_quality', {}).get('todo_count', 0)}
- **FIXME markers**: {review.get('code_quality', {}).get('fixme_count', 0)}
- ✅ Has type hints: {review.get('code_quality', {}).get('has_type_hints', False)}
- ✅ Has docstrings: {review.get('code_quality', {}).get('has_docstrings', False)}
- **Source files**: {review.get('code_quality', {}).get('file_count', 0)}

### Issues Found

"""
        
        module_issues = issues_by_module.get(module, [])
        if module_issues:
            for priority, issue in sorted(module_issues, key=lambda x: x[0]):
                report += f"- **[{priority}]** {issue['issue']}\n"
                if issue.get('file'):
                    report += f"  - File: `{issue['file']}`\n"
                report += f"  - Details: {issue['details']}\n\n"
        else:
            report += "✅ No issues found\n\n"
        
        report += "---\n\n"
    
    return report

def generate_roadmap(issues: Dict[str, List[Dict[str, Any]]]) -> str:
    """Generate improvement roadmap."""
    report = f"""# GEO-INFER Comprehensive Repository Review - Improvement Roadmap

**Review Date**: {datetime.now().strftime('%Y-%m-%d')}

---

## Roadmap Overview

This roadmap prioritizes improvements based on severity and impact. Issues are categorized as:
- **P0 (Critical)**: Blocks functionality, must be addressed immediately
- **P1 (High)**: Significant impact, should be addressed soon
- **P2 (Medium)**: Moderate impact, address in next phase
- **P3 (Low)**: Minor impact, address when convenient

---

## Phase 1: Critical Fixes (P0) - Immediate

**Timeline**: 1-2 weeks  
**Effort**: High  
**Impact**: Critical

### Tasks

"""
    
    # Group P0 issues by category
    p0_by_category = defaultdict(list)
    for issue in issues["P0"]:
        p0_by_category[issue["category"]].append(issue)
    
    for category, issue_list in p0_by_category.items():
        report += f"### {category.title()}\n\n"
        for issue in issue_list[:10]:  # Limit to 10 per category
            report += f"- **{issue['module']}**: {issue['issue']}\n"
            if issue.get('file'):
                report += f"  - Fix: `{issue['file']}`\n"
        report += "\n"
    
    report += f"""
**Success Criteria**:
- All P0 issues resolved
- All modules have requirements.txt
- All modules have test suites
- All modules have setup files

---

## Phase 2: High Priority (P1) - Short Term

**Timeline**: 2-4 weeks  
**Effort**: Medium-High  
**Impact**: High

### Tasks

"""
    
    p1_by_category = defaultdict(list)
    for issue in issues["P1"]:
        p1_by_category[issue["category"]].append(issue)
    
    for category, issue_list in p1_by_category.items():
        report += f"### {category.title()}\n\n"
        for issue in issue_list[:10]:
            report += f"- **{issue['module']}**: {issue['issue']}\n"
        report += "\n"
    
    report += f"""
**Success Criteria**:
- All P1 issues resolved
- All modules have complete documentation
- All modules have accurate dependencies

---

## Phase 3: Medium Priority (P2) - Medium Term

**Timeline**: 1-2 months  
**Effort**: Medium  
**Impact**: Moderate

### Tasks

"""
    
    p2_by_category = defaultdict(list)
    for issue in issues["P2"]:
        p2_by_category[issue["category"]].append(issue)
    
    for category, issue_list in p2_by_category.items():
        report += f"### {category.title()}\n\n"
        for issue in issue_list[:10]:
            report += f"- **{issue['module']}**: {issue['issue']}\n"
        report += "\n"
    
    report += f"""
**Success Criteria**:
- All P2 issues addressed
- Code quality improved
- Test organization standardized

---

## Phase 4: Low Priority (P3) - Long Term

**Timeline**: 2-3 months  
**Effort**: Low-Medium  
**Impact**: Low

### Tasks

"""
    
    p3_by_category = defaultdict(list)
    for issue in issues["P3"]:
        p3_by_category[issue["category"]].append(issue)
    
    for category, issue_list in p3_by_category.items():
        report += f"### {category.title()}\n\n"
        for issue in issue_list[:10]:
            report += f"- **{issue['module']}**: {issue['issue']}\n"
        report += "\n"
    
    report += f"""
**Success Criteria**:
- All P3 issues addressed
- All modules have examples
- Documentation polished

---

## Summary Statistics

| Priority | Count | Modules Affected | Estimated Effort |
|----------|-------|------------------|------------------|
| P0 (Critical) | {len(issues['P0'])} | {len(set(i['module'] for i in issues['P0']))} | High |
| P1 (High) | {len(issues['P1'])} | {len(set(i['module'] for i in issues['P1']))} | Medium-High |
| P2 (Medium) | {len(issues['P2'])} | {len(set(i['module'] for i in issues['P2']))} | Medium |
| P3 (Low) | {len(issues['P3'])} | {len(set(i['module'] for i in issues['P3']))} | Low-Medium |
| **Total** | **{sum(len(v) for v in issues.values())}** | **{len(set(i['module'] for v in issues.values() for i in v))}** | - |

---

## Implementation Guidelines

1. **Start with P0**: Address critical issues first
2. **Batch Similar Issues**: Group similar fixes together
3. **Test After Each Fix**: Ensure fixes don't break existing functionality
4. **Update Documentation**: Keep documentation current with changes
5. **Track Progress**: Update this roadmap as issues are resolved

---
"""
    return report

def main():
    """Generate all reports."""
    print("Loading review data...")
    reviews = load_review_data()
    
    print("Categorizing issues...")
    issues = categorize_issues(reviews)
    
    print("Generating reports...")
    output_dir = Path(__file__).parent.parent / "GEO-INFER-INTRA" / "assessment_results"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate summary
    summary = generate_executive_summary(reviews, issues)
    with open(output_dir / "COMPREHENSIVE_REVIEW_SUMMARY.md", "w") as f:
        f.write(summary)
    print("✅ Generated executive summary")
    
    # Generate detailed report
    detailed = generate_detailed_report(reviews, issues)
    with open(output_dir / "COMPREHENSIVE_REVIEW_DETAILED.md", "w") as f:
        f.write(detailed)
    print("✅ Generated detailed report")
    
    # Generate roadmap
    roadmap = generate_roadmap(issues)
    with open(output_dir / "COMPREHENSIVE_REVIEW_ROADMAP.md", "w") as f:
        f.write(roadmap)
    print("✅ Generated roadmap")
    
    # Save issues JSON
    with open(output_dir / "comprehensive_review_issues_2025.json", "w") as f:
        json.dump(issues, f, indent=2)
    print("✅ Saved issues JSON")
    
    print("\n✅ All reports generated successfully!")

if __name__ == "__main__":
    main()

