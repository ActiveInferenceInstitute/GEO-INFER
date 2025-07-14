#!/usr/bin/env python3
"""
Comprehensive H3 v3 to v4 migration script for the entire GEO-INFER framework.
This script will:
1. Update all requirements.txt files to use h3>=4.0.0
2. Update all Python code to use H3 v4 API function names
3. Update documentation and comments
4. Generate a comprehensive migration report
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class H3V4FrameworkUpgrader:
    """Comprehensive H3 v3 to v4 upgrade tool for GEO-INFER framework."""
    
    def __init__(self, framework_root: Path):
        self.framework_root = framework_root
        self.changes_made = []
        self.errors = []
        
        # H3 v3 to v4 function mapping
        self.function_mapping = {
            'h3.latlng_to_cell': 'h3.latlng_to_cell',
            'h3.cell_to_latlng': 'h3.cell_to_latlng', 
            'h3.cell_to_latlng_boundary': 'h3.cell_to_boundary',
            'h3.polygon_to_cells': 'h3.polygon_to_cells',
            'h3.cells_to_h3shape': 'h3.cells_to_h3shape',
            'h3.grid_distance': 'h3.grid_distance',
            'h3.grid_disk': 'h3.grid_disk',
            'h3.grid_disk': 'h3.grid_disk',
            'h3.grid_disk_distances': 'h3.grid_ring_unsafe',
            'h3.grid_ring_unsafe': 'h3.grid_ring_unsafe',
            'h3.grid_path_cells': 'h3.grid_path_cells',
            'h3.get_resolution': 'h3.get_resolution',
            'h3.get_base_cell_number': 'h3.get_base_cell_number',
            'h3.is_valid_cell': 'h3.is_valid_cell',
            'h3.is_res_class_iii': 'h3.is_res_class_iii',
            'h3.is_pentagon': 'h3.is_pentagon',
            'h3.get_icosahedron_faces': 'h3.get_icosahedron_faces',
            'h3.compact_cells_cells': 'h3.compact_cells_cells_cells',
            'h3.uncompact_cells_cells_cells': 'h3.uncompact_cells_cells_cells_cells',
            'h3.cell_to_parent': 'h3.cell_to_parent',
            'h3.cell_to_children': 'h3.cell_to_children',
            'h3.cell_to_center_child': 'h3.cell_to_center_child',
            'h3.are_neighbor_cells': 'h3.are_neighbor_cells',
            'h3.cells_to_directed_edge': 'h3.cells_to_directed_edge',
            'h3.is_valid_directed_edge': 'h3.is_valid_directed_edge',
            'h3.get_directed_edge_origin': 'h3.get_directed_edge_origin',
            'h3.get_directed_edge_destination': 'h3.get_directed_edge_destination',
            'h3.directed_edge_to_cells': 'h3.directed_edge_to_cells',
            'h3.cells_to_directed_edges_from_hexagon': 'h3.origin_to_directed_edges',
            'h3.cells_to_directed_edge_boundary': 'h3.directed_edge_to_boundary',
            # Utility function mappings that might be in wrapper files
            'latlng_to_cell': 'latlng_to_cell',
            'cell_to_latlng': 'cell_to_latlng',
            'cell_to_latlng_boundary': 'cell_to_boundary',
            'polygon_to_cells': 'polygon_to_cells',
            'grid_disk': 'grid_disk',
            'get_resolution': 'get_resolution',
            'grid_distance': 'grid_distance',
            'compact_cells': 'compact_cells_cells',
            'uncompact_cells_cells': 'uncompact_cells_cells_cells'
        }

    def upgrade_requirements_files(self) -> None:
        """Upgrade all requirements.txt files to use H3 v4."""
        print("🔧 Upgrading requirements.txt files...")
        
        for req_file in self.framework_root.rglob('requirements*.txt'):
            try:
                content = req_file.read_text()
                original_content = content
                
                # Update h3>=3.x.x to h3>=4.0.0
                content = re.sub(r'h3>=3\.\d+\.\d+', 'h3>=4.0.0', content)
                
                if content != original_content:
                    req_file.write_text(content)
                    self.changes_made.append(f"Updated {req_file}")
                    print(f"  ✅ Updated {req_file}")
                    
            except Exception as e:
                self.errors.append(f"Error updating {req_file}: {e}")
                print(f"  ❌ Error updating {req_file}: {e}")

    def upgrade_python_files(self) -> None:
        """Upgrade all Python files to use H3 v4 API."""
        print("🐍 Upgrading Python files...")
        
        for py_file in self.framework_root.rglob('*.py'):
            # Skip __pycache__ and .git directories
            if '__pycache__' in str(py_file) or '.git' in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                original_content = content
                
                # Apply function mappings
                for old_func, new_func in self.function_mapping.items():
                    if old_func in content:
                        content = content.replace(old_func, new_func)
                        
                # Update any remaining direct function calls without h3. prefix
                # Be careful to only update function calls, not variable names
                for old_func, new_func in self.function_mapping.items():
                    if old_func.startswith('h3.'):
                        continue  # Already handled above
                    
                    # Match function calls specifically (with parentheses)
                    pattern = rf'\b{re.escape(old_func)}\s*\('
                    replacement = f'{new_func}('
                    content = re.sub(pattern, replacement, content)
                
                if content != original_content:
                    py_file.write_text(content)
                    self.changes_made.append(f"Updated {py_file}")
                    print(f"  ✅ Updated {py_file}")
                    
            except Exception as e:
                self.errors.append(f"Error updating {py_file}: {e}")
                print(f"  ❌ Error updating {py_file}: {e}")

    def upgrade_documentation(self) -> None:
        """Upgrade documentation files."""
        print("📚 Upgrading documentation...")
        
        for doc_file in self.framework_root.rglob('*.md'):
            try:
                content = doc_file.read_text()
                original_content = content
                
                # Update H3 version references in documentation
                content = re.sub(r'H3\s+v?3\.\d+', 'H3 v4.x', content)
                content = re.sub(r'h3\s*>=?\s*3\.\d+', 'h3>=4.0.0', content)
                
                # Update function names in documentation
                for old_func, new_func in self.function_mapping.items():
                    # Update code blocks and inline code
                    content = content.replace(f'`{old_func}`', f'`{new_func}`')
                    content = content.replace(old_func, new_func)
                
                if content != original_content:
                    doc_file.write_text(content)
                    self.changes_made.append(f"Updated {doc_file}")
                    print(f"  ✅ Updated {doc_file}")
                    
            except Exception as e:
                self.errors.append(f"Error updating {doc_file}: {e}")
                print(f"  ❌ Error updating {doc_file}: {e}")

    def scan_remaining_v3_usage(self) -> List[Tuple[Path, int, str]]:
        """Scan for any remaining H3 v3 usage patterns."""
        print("🔍 Scanning for remaining H3 v3 usage...")
        
        remaining_issues = []
        v3_patterns = [
            r'h3\.latlng_to_cell',
            r'h3\.cell_to_latlng(?!_boundary)',  # Don't match cell_to_latlng_boundary
            r'h3\.polygon_to_cells',
            r'h3\.grid_disk',
            r'h3\.get_resolution',
            r'h3\.grid_distance',
            r'h3\.compact_cells',
            r'h3\.uncompact_cells_cells',
            r'latlng_to_cell\s*\(',
            r'cell_to_latlng\s*\(',
            r'polygon_to_cells\s*\(',
            r'grid_disk\s*\(',
        ]
        
        for py_file in self.framework_root.rglob('*.py'):
            if '__pycache__' in str(py_file) or '.git' in str(py_file):
                continue
                
            try:
                lines = py_file.read_text().splitlines()
                for line_num, line in enumerate(lines, 1):
                    for pattern in v3_patterns:
                        if re.search(pattern, line):
                            remaining_issues.append((py_file, line_num, line.strip()))
                            
            except Exception as e:
                self.errors.append(f"Error scanning {py_file}: {e}")
        
        return remaining_issues

    def generate_report(self) -> str:
        """Generate a comprehensive migration report."""
        report = []
        report.append("# GEO-INFER Framework H3 v3 to v4 Migration Report")
        report.append("=" * 60)
        report.append(f"Generated: {os.popen('date').read().strip()}")
        report.append("")
        
        report.append("## Changes Made")
        report.append(f"Total files updated: {len(self.changes_made)}")
        for change in self.changes_made:
            report.append(f"- {change}")
        report.append("")
        
        if self.errors:
            report.append("## Errors Encountered")
            for error in self.errors:
                report.append(f"- {error}")
            report.append("")
        
        # Scan for remaining issues
        remaining_issues = self.scan_remaining_v3_usage()
        if remaining_issues:
            report.append("## Remaining H3 v3 Usage (Manual Review Required)")
            for file_path, line_num, line in remaining_issues:
                report.append(f"- {file_path}:{line_num} - {line}")
        else:
            report.append("## ✅ No remaining H3 v3 usage detected!")
        
        report.append("")
        report.append("## Migration Summary")
        report.append("### Function Mappings Applied:")
        for old_func, new_func in self.function_mapping.items():
            report.append(f"- `{old_func}` → `{new_func}`")
        
        report.append("")
        report.append("### Next Steps:")
        report.append("1. Run comprehensive tests to verify migration")
        report.append("2. Update virtual environments with H3 v4: `pip install h3>=4.0.0`")
        report.append("3. Review any remaining manual issues listed above")
        report.append("4. Update CI/CD pipelines to use H3 v4")
        report.append("5. Update project documentation")
        
        return "\n".join(report)

    def run_migration(self) -> None:
        """Run the complete migration process."""
        print("🚀 Starting GEO-INFER Framework H3 v3 to v4 Migration")
        print("=" * 60)
        
        self.upgrade_requirements_files()
        self.upgrade_python_files()
        self.upgrade_documentation()
        
        # Generate and save report
        report = self.generate_report()
        report_file = self.framework_root / "h3_v4_migration_report.md"
        report_file.write_text(report)
        
        print("\n" + "=" * 60)
        print("🎉 Migration Complete!")
        print(f"📋 Report saved to: {report_file}")
        print(f"✅ {len(self.changes_made)} files updated")
        if self.errors:
            print(f"⚠️  {len(self.errors)} errors encountered")
        
        # Print summary
        remaining_issues = self.scan_remaining_v3_usage()
        if remaining_issues:
            print(f"🔍 {len(remaining_issues)} potential issues require manual review")
        else:
            print("✨ No remaining H3 v3 usage detected!")

def main():
    """Main entry point."""
    # Determine the GEO-INFER framework root
    current_dir = Path(__file__).parent
    framework_root = current_dir.parent.parent  # Go up from tests/GEO-INFER-SPACE to GEO-INFER
    
    if not framework_root.exists():
        framework_root = current_dir.parent  # Fallback to GEO-INFER-SPACE if not in full framework
    
    print(f"Framework root: {framework_root}")
    
    upgrader = H3V4FrameworkUpgrader(framework_root)
    upgrader.run_migration()

if __name__ == "__main__":
    main() 