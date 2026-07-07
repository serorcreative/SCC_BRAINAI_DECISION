"""Validation humaine des décisions — garde-fous de souveraineté.

**Aucune décision souveraine sans validation humaine ; aucune application
automatique.** Une décision naît *proposée* et ne change d'état que par une **action
humaine explicite**, tracée (approbateur, motif, horodatage figé).
"""

from __future__ import annotations

from typing import Any, Dict

from scc_brainai_decision.core.errors import ValidationError
from scc_brainai_decision.core.model import DecisionStatus, can_transition


class HumanValidationPolicy:
    def __init__(self, as_of: str):
        self._as_of = as_of

    def _apply(self, record: Dict[str, Any], target: str, action: str,
               approver: str, reason: str) -> Dict[str, Any]:
        if not approver:
            raise ValidationError("Une validation exige un approbateur humain explicite.")
        current = record.get("status", DecisionStatus.PROPOSED.value)
        if not can_transition(current, target):
            raise ValidationError(f"Transition interdite : {current} -> {target}.")
        record["status"] = target
        record["validation"] = {"action": action, "approver": approver, "reason": reason,
                                "at": self._as_of, "previous": record.get("validation", {})}
        return record

    def validate(self, record: Dict[str, Any], approver: str, reason: str = "") -> Dict[str, Any]:
        return self._apply(record, DecisionStatus.VALIDATED.value, "validate", approver, reason)

    def reject(self, record: Dict[str, Any], approver: str, reason: str = "") -> Dict[str, Any]:
        return self._apply(record, DecisionStatus.REJECTED.value, "reject", approver, reason)

    def revoke(self, record: Dict[str, Any], approver: str, reason: str = "") -> Dict[str, Any]:
        return self._apply(record, DecisionStatus.REVOKED.value, "revoke", approver, reason)


__all__ = ["HumanValidationPolicy"]
