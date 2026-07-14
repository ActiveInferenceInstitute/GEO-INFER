"""Normative integration for governance rule translation and compliance."""

from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Optional normative integration
try:
    from geo_infer_norms.core.normative_inference import (
        NormativeInference as NormativeSystemManager,
    )

    NORMS_AVAILABLE = True
except ImportError:
    NORMS_AVAILABLE = False
    logger.warning("GEO-INFER-NORMS not available, normative features disabled")


class NormativeGovernanceIntegration:
    """
    Integrate normative systems with governance rules.

    Provides:
    - Translation of governance rules to normative rules
    - Compliance checking with norms
    - Norm violation detection
    - Norm-governance alignment

    References:
    - Normative reasoning for governance
    - Compliance frameworks
    """

    def __init__(self):
        """Initialize normative governance integration."""
        if NORMS_AVAILABLE:
            try:
                self.norms_manager = NormativeSystemManager()
                self.norms_available = True
            except Exception as e:
                logger.warning(f"Could not initialize NormativeSystemManager: {e}")
                self.norms_manager = None
                self.norms_available = False
        else:
            self.norms_manager = None
            self.norms_available = False
            logger.warning(
                "Normative integration disabled - GEO-INFER-NORMS not available"
            )

    def translate_governance_rules_to_norms(
        self,
        governance_rules: List[Dict[str, Any]],
        normative_framework: str = "default",
    ) -> Dict[str, Any]:
        """
        Translate governance rules to normative rules.

        Parameters:
        -----------
        governance_rules : List[Dict[str, Any]]
            Governance rules to translate
        normative_framework : str
            Target normative framework

        Returns:
        --------
        Dict[str, Any]
            Translated normative rules
        """
        translation = {
            "translated": True,
            "normative_rules": [],
            "translation_quality": 0.0,
            "untranslatable_rules": [],
        }

        if not self.norms_available:
            translation["translated"] = False
            translation["reason"] = "Normative module not available"
            return translation

        # Translate each governance rule
        for rule in governance_rules:
            rule_type = rule.get("type", "unknown")
            rule_description = rule.get("description", "")

            # Map governance rule types to normative rule types
            norm_mapping = {
                "boundary": "membership_norm",
                "choice": "decision_norm",
                "information": "information_norm",
                "monitoring": "monitoring_norm",
                "sanction": "enforcement_norm",
                "conflict_resolution": "conflict_norm",
            }

            norm_type = norm_mapping.get(rule_type, "general_norm")

            # Create normative rule representation
            normative_rule = {
                "norm_id": f"norm_{rule.get('id', 'unknown')}",
                "norm_type": norm_type,
                "description": rule_description,
                "governance_rule_id": rule.get("id", "unknown"),
                "conditions": rule.get("conditions", []),
                "consequences": rule.get("consequences", []),
            }

            translation["normative_rules"].append(normative_rule)

        # Calculate translation quality
        if governance_rules:
            translation["translation_quality"] = len(
                translation["normative_rules"]
            ) / len(governance_rules)

        return translation

    def check_compliance_with_norms(
        self,
        governance_actions: List[Dict[str, Any]],
        normative_rules: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Check governance actions for compliance with normative rules.

        Parameters:
        -----------
        governance_actions : List[Dict[str, Any]]
            Actions to check
        normative_rules : List[Dict[str, Any]]
            Normative rules to check against

        Returns:
        --------
        Dict[str, Any]
            Compliance checking results
        """
        compliance = {
            "checked": True,
            "compliant_actions": [],
            "violations": [],
            "compliance_rate": 0.0,
        }

        if not self.norms_available:
            compliance["checked"] = False
            compliance["reason"] = "Normative module not available"
            return compliance

        # Check each action against norms
        for action in governance_actions:
            action_type = action.get("type", "unknown")
            action_actor = action.get("actor", "unknown")

            # Simplified compliance checking
            # In real implementation, would use normative reasoning
            is_compliant = True
            violated_norms = []

            for norm in normative_rules:
                norm_type = norm.get("norm_type", "")
                norm_conditions = norm.get("conditions", [])

                # Check if action violates norm conditions
                # Simplified: check if action type matches norm type and conditions
                if norm_type in ["decision_norm", "action_norm"]:
                    # Check if action meets norm conditions
                    if norm_conditions:
                        # Simplified compliance check
                        is_compliant = True  # Would implement real checking

                if not is_compliant:
                    violated_norms.append(norm.get("norm_id", "unknown"))

            if is_compliant:
                compliance["compliant_actions"].append(
                    {
                        "action_id": action.get("id", "unknown"),
                        "action_type": action_type,
                        "actor": action_actor,
                    }
                )
            else:
                compliance["violations"].append(
                    {
                        "action_id": action.get("id", "unknown"),
                        "action_type": action_type,
                        "actor": action_actor,
                        "violated_norms": violated_norms,
                    }
                )

        # Calculate compliance rate
        if governance_actions:
            compliance["compliance_rate"] = len(compliance["compliant_actions"]) / len(
                governance_actions
            )

        return compliance

    def detect_norm_violations(
        self,
        governance_structure: Dict[str, Any],
        normative_rules: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Detect norm violations in governance structure.

        Parameters:
        -----------
        governance_structure : Dict[str, Any]
            Governance structure to analyze
        normative_rules : List[Dict[str, Any]]
            Normative rules to check

        Returns:
        --------
        Dict[str, Any]
            Violation detection results
        """
        violations = {
            "violations_detected": False,
            "violations": [],
            "violation_count": 0,
        }

        if not self.norms_available:
            violations["violations_detected"] = False
            violations["reason"] = "Normative module not available"
            return violations

        # Check governance entities against norms
        entities = governance_structure.get("entities", [])

        for entity in entities:
            _entity_responsibilities = entity.get("responsibilities", [])

            # Check if entity structure violates any norms
            for norm in normative_rules:
                norm_type = norm.get("norm_type", "")
                _norm_conditions = norm.get("conditions", [])

                # Simplified violation detection
                # In real implementation, would use normative reasoning engine
                if "membership_norm" in norm_type:
                    # Check if entity membership is properly defined
                    if not entity.get("stakeholders"):
                        violations["violations"].append(
                            {
                                "entity_id": entity.get("entity_id", "unknown"),
                                "norm_id": norm.get("norm_id", "unknown"),
                                "violation_type": "membership_violation",
                                "description": "Entity lacks defined stakeholder membership",
                            }
                        )

        violations["violation_count"] = len(violations["violations"])
        violations["violations_detected"] = violations["violation_count"] > 0

        return violations

    def align_norms_with_governance(
        self,
        governance_rules: List[Dict[str, Any]],
        existing_norms: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Align normative rules with governance rules.

        Parameters:
        -----------
        governance_rules : List[Dict[str, Any]]
            Governance rules
        existing_norms : List[Dict[str, Any]]
            Existing normative rules

        Returns:
        --------
        Dict[str, Any]
            Alignment analysis
        """
        alignment = {
            "aligned": True,
            "alignment_score": 0.0,
            "conflicts": [],
            "gaps": [],
        }

        if not self.norms_available:
            alignment["aligned"] = False
            alignment["reason"] = "Normative module not available"
            return alignment

        # Check for conflicts between governance rules and norms
        for gov_rule in governance_rules:
            _gov_rule_type = gov_rule.get("type", "")
            gov_description = gov_rule.get("description", "").lower()

            for norm in existing_norms:
                _norm_type = norm.get("norm_type", "")
                norm_description = norm.get("description", "").lower()

                # Check for conflicts (simplified)
                if "conflict" in gov_description and "conflict" in norm_description:
                    # Potential conflict - would need deeper analysis
                    alignment["conflicts"].append(
                        {
                            "governance_rule": gov_rule.get("id", "unknown"),
                            "norm": norm.get("norm_id", "unknown"),
                            "conflict_type": "potential_conflict",
                        }
                    )

        # Check for gaps (governance rules without corresponding norms)
        gov_rule_types = set(r.get("type", "") for r in governance_rules)
        norm_types = set(n.get("norm_type", "") for n in existing_norms)

        # Map between rule types
        type_mapping = {
            "boundary": "membership_norm",
            "choice": "decision_norm",
            "information": "information_norm",
        }

        mapped_norm_types = set(type_mapping.get(gt, "") for gt in gov_rule_types)
        gaps = mapped_norm_types - norm_types

        if gaps:
            alignment["gaps"].extend(list(gaps))

        # Calculate alignment score
        if existing_norms:
            conflict_penalty = len(alignment["conflicts"]) * 0.1
            gap_penalty = len(alignment["gaps"]) * 0.05
            alignment["alignment_score"] = max(
                0.0, 1.0 - conflict_penalty - gap_penalty
            )
        else:
            alignment["alignment_score"] = 0.5  # Neutral if no norms to compare

        return alignment
