import os
import glob

# --- Configuration ---

ROOT_DIR = "."

# Module Categories (Based on AGENTS.md)
CORE_AGENT_MODULES = ["GEO-INFER-AGENT", "GEO-INFER-ACT", "GEO-INFER-ANT", "GEO-INFER-SIM", "GEO-INFER-COG"]

DOMAIN_MODULES = [
    "GEO-INFER-AG", "GEO-INFER-HEALTH", "GEO-INFER-LOG", "GEO-INFER-RISK", 
    "GEO-INFER-IOT", "GEO-INFER-TRANSPORT", "GEO-INFER-WATER", "GEO-INFER-FOREST",
    "GEO-INFER-MARINE", "GEO-INFER-ENERGY", "GEO-INFER-EMERGENCY", "GEO-INFER-EDU",
    "GEO-INFER-BIO", "GEO-INFER-CLIMATE", "GEO-INFER-ECON", "GEO-INFER-PLACE",
    "GEO-INFER-CIV"
]

INFRASTRUCTURE_MODULES = [
    "GEO-INFER-SPACE", "GEO-INFER-TIME", "GEO-INFER-DATA", "GEO-INFER-MATH",
    "GEO-INFER-BAYES", "GEO-INFER-AI", "GEO-INFER-API", "GEO-INFER-APP",
    "GEO-INFER-SEC", "GEO-INFER-OPS", "GEO-INFER-GIT", "GEO-INFER-INTRA",
    "GEO-INFER-REQ", "GEO-INFER-NORMS", "GEO-INFER-ORG", "GEO-INFER-PEP",
    "GEO-INFER-COMMS", "GEO-INFER-SPM", "GEO-INFER-TEST", "GEO-INFER-EXAMPLES",
    "GEO-INFER-METAGOV", "GEO-INFER-VIZ" # VIZ might be new
]

# Signpost HTML
SIGNPOST = """
<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="../GEO-INFER-INTRA/README.md">📚 Documentation</a>
</div>

---
"""

# Templates
TEMPLATE_AGENTS_FRAMEWORK = """# {module_name} Agent Integration

{signpost}

## 🤖 Module Agent Capabilities

This module provides **Infrastructure Support** for the GEO-INFER Multi-Agent System.

### Framework Capabilities
| Capability | Description | Status |
|------------|-------------|--------|
| **Feature 1** | Description of how this module supports agents | 🟡 Alpha |
| **Feature 2** | Description of integration points | 🟡 Alpha |

## 🔌 Integration Patterns

### Using {module_name} in Agents

```python
# Example of agent using this module
from {pkg_name} import SomeCoreComponent

def agent_logic(agent):
    # Use component
    result = SomeCoreComponent.process(agent.state)
    return result
```
"""

TEMPLATE_AGENTS_DOMAIN = """# {module_name} Agent Applications

{signpost}

## 🤖 Module Agent Capabilities

This module implements **Domain-Specific Agents** for the GEO-INFER Multi-Agent System.

### Integration Status
| Agent Type | Purpose | Status |
|------------|---------|--------|
| **DomainAgent** | Primary agent for this domain | 🟡 Alpha |
| **MonitoringAgent** | Observes domain-specific metrics | 🔮 Planned |

## 🕵️ Active Agents

### 1. Domain Agent (Example)
**Role**: Manage domain-specific operations.
**Sensors**: Inputs from SPACE, TIME, IOT.
**Actuators**: Decisions logged to DATA or API.

```python
# Example instantiation
from geo_infer_agent import BaseAgent
# from {pkg_name} import specialized_logic
```

## 🔌 Integration Patterns
This module's agents coordinate via `GEO-INFER-AGENT` registry.
"""

def get_pkg_name(module_name):
    return module_name.replace("-", "_").lower()

def update_file_signpost(filepath, is_markdown=True):
    if not os.path.exists(filepath):
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if signpost already exists (loose check)
    if "🌍 GEO-INFER Core" in content and "🤖 Agent Architecture" in content:
        # Already has signpost, maybe check if it's up to date?
        # For now, assume if it exists, it's fine.
        # OR: Rewrite it if we want to enforce specific structure.
        # Let's simple check.
        # Actually, let's prepend if missing.
        print(f"  [SKIP] Signpost exists in {filepath}")
        return False
    else:
        # Prepend signpost
        # Handle Front Matter (--- ... ---)
        if content.startswith("---"):
            # Find end of front matter
            end_fm = content.find("---", 3)
            if end_fm != -1:
                # Insert after front matter
                new_content = content[:end_fm+3] + "\n" + SIGNPOST + content[end_fm+3:]
            else:
                 new_content = SIGNPOST + content
        else:
             new_content = SIGNPOST + content
        
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"  [UPDATED] Added signpost to {filepath}")
        return True

def create_agents_md(module_path, module_name):
    filepath = os.path.join(module_path, "AGENTS.md")
    if os.path.exists(filepath):
        return False
    
    pkg_name = get_pkg_name(module_name)
    
    if module_name in DOMAIN_MODULES:
        template = TEMPLATE_AGENTS_DOMAIN
    else:
        template = TEMPLATE_AGENTS_FRAMEWORK
        
    content = template.format(module_name=module_name, pkg_name=pkg_name, signpost=SIGNPOST)
    
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"  [CREATED] AGENTS.md in {module_name}")
    return True

def main():
    modules = glob.glob("GEO-INFER-*")
    modules.sort()
    
    print(f"Found {len(modules)} modules.")
    
    for module in modules:
        if not os.path.isdir(module):
            continue
            
        print(f"Processing {module}...")
        
        # 1. Update README.md
        readme_path = os.path.join(module, "README.md")
        if os.path.exists(readme_path):
            update_file_signpost(readme_path)
        else:
            print(f"  [WARNING] No README.md in {module}")
            
        # 2. Update/Create AGENTS.md
        if not create_agents_md(module, module):
            # If it existed, check signpost
            update_file_signpost(os.path.join(module, "AGENTS.md"))

if __name__ == "__main__":
    main()
