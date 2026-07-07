"""Qualification décisionnelle : score composite et drapeaux de gouvernance.

Score = impact ↑, risque ↓, confiance ↑, réversibilité ↑ (l'urgence est un drapeau
de gouvernance, non un critère de qualité). Déterministe et borné.
"""

from __future__ import annotations

from typing import Any, Dict, List

from scc_brainai_decision.core.model import DecisionOption


def score_option(o: DecisionOption, weights: Dict[str, float]) -> float:
    return round(
        weights.get("impact", 0.30) * o.impact
        + weights.get("risk", 0.30) * (1.0 - o.risk)
        + weights.get("confidence", 0.20) * o.confidence
        + weights.get("reversibility", 0.20) * o.reversibility, 4)


def qualify(options: List[DecisionOption], weights: Dict[str, float]) -> List[DecisionOption]:
    for o in options:
        o.score = score_option(o, weights)
        o.seal()
    return options


def governance_flags(o: DecisionOption, thresholds: Dict[str, float]) -> Dict[str, bool]:
    return {
        "high_impact": o.impact >= thresholds.get("high_impact", 0.7),
        "high_risk": o.risk >= thresholds.get("high_risk", 0.6),
        "low_reversibility": o.reversibility <= thresholds.get("low_reversibility", 0.4),
        "high_urgency": o.urgency >= thresholds.get("high_urgency", 0.7),
    }


def qualification_view(o: DecisionOption, thresholds: Dict[str, float]) -> Dict[str, Any]:
    return {**o.qualification(), "score": o.score, "flags": governance_flags(o, thresholds),
            "class": _class(o, thresholds)}


def _class(o: DecisionOption, thresholds: Dict[str, float]) -> str:
    """Classe de gouvernance : critique si irréversible+impactante, sinon sensible/routine."""
    flags = governance_flags(o, thresholds)
    if flags["low_reversibility"] and flags["high_impact"]:
        return "critique"        # analogue T3 : garde-fou humain renforcé
    if flags["high_risk"] or flags["high_impact"]:
        return "sensible"
    return "routine"


__all__ = ["score_option", "qualify", "governance_flags", "qualification_view"]
