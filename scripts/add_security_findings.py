#!/usr/bin/env python3
"""Add security findings to review reports."""

import json
from pathlib import Path

def add_security_findings():
    """Add security-specific findings."""
    issues_file = Path(__file__).parent.parent / "GEO-INFER-INTRA" / "assessment_results" / "comprehensive_review_issues_2025.json"
    
    with open(issues_file) as f:
        issues = json.load(f)
    
    # Add security findings
    security_findings = [
        {
            "module": "MATH",
            "issue": "Use of eval() in theorem prover",
            "details": "GEO-INFER-MATH/src/geo_infer_math/core/theorem_proving/prover.py uses eval() which is a security risk",
            "category": "security",
            "priority": "P1",
            "file": "GEO-INFER-MATH/src/geo_infer_math/core/theorem_proving/prover.py",
            "line": "164, 171"
        },
        {
            "module": "SEC",
            "issue": "Default secret key in authorization",
            "details": "GEO-INFER-SEC/src/geo_infer_sec/core/authorization.py uses 'default_secret_key' as default",
            "category": "security",
            "priority": "P0",
            "file": "GEO-INFER-SEC/src/geo_infer_sec/core/authorization.py",
            "line": "43"
        },
        {
            "module": "SEC",
            "issue": "Simplified encryption implementation",
            "details": "GEO-INFER-SEC/src/geo_infer_sec/utils/security_utils.py uses XOR encryption instead of proper AES",
            "category": "security",
            "priority": "P1",
            "file": "GEO-INFER-SEC/src/geo_infer_sec/utils/security_utils.py",
            "line": "133-134"
        }
    ]
    
    # Add to appropriate priority lists
    for finding in security_findings:
        priority = finding.pop("priority")
        issues[priority].append(finding)
    
    # Save updated issues
    with open(issues_file, "w") as f:
        json.dump(issues, f, indent=2)
    
    print(f"Added {len(security_findings)} security findings")

if __name__ == "__main__":
    add_security_findings()

