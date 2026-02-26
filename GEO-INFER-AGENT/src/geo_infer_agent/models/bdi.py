"""
Compatibility shim for the legacy bdi.py module.

All classes previously defined here have been migrated to the ``bdi/``
package:
  - Belief, Desire, Plan  →  geo_infer_agent.models.bdi.agent
  - BDIState, BDIAgent    →  geo_infer_agent.models.bdi.agent
  - BeliefBase            →  geo_infer_agent.models.bdi.belief
  - DesireSet             →  geo_infer_agent.models.bdi.desire
  - PlanLibrary           →  geo_infer_agent.models.bdi.plan

Import from those submodules directly.  This file exists only so that any
third-party code that does ``import geo_infer_agent.models.bdi`` (as a *file*)
still receives useful error guidance.  In practice Python resolves
``geo_infer_agent.models.bdi`` to the *package* (directory), so this file is
not importable via normal import machinery and is superseded.
"""

# NOTE: Python's import system resolves ``geo_infer_agent.models.bdi`` to the
# bdi/ package directory.  This file (bdi.py) is therefore NOT reached by any
# standard import.  It is kept only for historical reference and can be
# removed in a future cleanup pass once all callers have been confirmed to use
# the package API.
