#!/usr/bin/env python3
"""Run the fast Cascadia integration profile."""

from run_comprehensive_validation import (
    check_configuration_contract,
    check_h3_integration,
    check_main_script_contract,
    check_module_structure,
    main,
)

FOCUSED_CHECKS = (
    ("main script contract", check_main_script_contract),
    ("configuration contract", check_configuration_contract),
    ("module structure", check_module_structure),
    ("H3 integration", check_h3_integration),
)


if __name__ == "__main__":
    raise SystemExit(main(FOCUSED_CHECKS))
