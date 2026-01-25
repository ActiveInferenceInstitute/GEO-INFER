#!/usr/bin/env python3
"""Test import of CascadianAgriculturalH3Backend"""

import sys
import os
from pathlib import Path

# Add paths
cascadia_dir = Path(__file__).parent
project_root = cascadia_dir.parents[2]
place_src_path = project_root / 'GEO-INFER-PLACE' / 'src'
space_src_path = project_root / 'GEO-INFER-SPACE' / 'src'

for p in [place_src_path, space_src_path]:
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))
        print(f"Added to path: {p}")

# Set OSC repo path
osc_repo_path = project_root / 'GEO-INFER-SPACE' / 'repo'
os.environ['OSC_REPOS_DIR'] = str(osc_repo_path)
print(f"Set OSC_REPOS_DIR to {osc_repo_path}")

try:
    from geo_infer_place.core.unified_backend import CascadianAgriculturalH3Backend
    print("✅ Successfully imported CascadianAgriculturalH3Backend")
except ImportError as e:
    print(f"❌ Failed to import CascadianAgriculturalH3Backend: {e}")
    import traceback
    traceback.print_exc()
