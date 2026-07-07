"""Manifeste décisionnel — destiné à Execution **plus tard**, jamais exécuté ici.

Porte explicitement ``execution_status = not_executed`` et
``requires_human_validation = true`` : rien ne s'exécute sans validation humaine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from scc_brainai_decision.core.model import DecisionOption, DecisionRequest


def build_manifest(selected: DecisionOption, request: DecisionRequest,
                   validation_conditions: List[str], success_criteria: List[str],
                   failure_criteria: List[str], revocation_conditions: List[str]) -> Dict[str, Any]:
    return {
        "selected_option": selected.name,
        "selected_option_id": selected.id,
        "origin": selected.origin,
        "plan_ref": request.planset_id or None,
        "deliberation_ref": request.deliberation_id or None,
        "executable": True,
        "execution_status": "not_executed",
        "requires_human_validation": True,
        "sovereign": False,
        "preconditions": list(validation_conditions),
        "success_criteria": list(success_criteria),
        "failure_criteria": list(failure_criteria),
        "abort_conditions": list(revocation_conditions),
    }


__all__ = ["build_manifest"]
