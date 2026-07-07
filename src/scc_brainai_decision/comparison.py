"""Comparaison des options et sélection (déterministe) + justification."""

from __future__ import annotations

from typing import Any, Dict, List

from scc_brainai_decision.core.model import DecisionOption


def select(options: List[DecisionOption]) -> DecisionOption:
    ranked = sorted(options, key=lambda o: (-o.score, o.id))
    best = ranked[0]
    for o in options:
        o.selected = (o.id == best.id)
        o.seal()
    return best


def rationale(options: List[DecisionOption], selected: DecisionOption) -> Dict[str, Any]:
    others = [o for o in options if o.id != selected.id]
    discarded = []
    for o in sorted(others, key=lambda x: (-x.score, x.id)):
        reason = _why_worse(selected, o)
        discarded.append({"option": o.name, "score": o.score, "why": reason})
    return {
        "retained": selected.name,
        "why_retained": (f"Meilleur score composite ({selected.score}) : équilibre "
                         f"impact {selected.impact} / risque {selected.risk} / "
                         f"confiance {selected.confidence} / réversibilité {selected.reversibility}."),
        "discarded": discarded,
    }


def _why_worse(sel: DecisionOption, other: DecisionOption) -> str:
    diffs = []
    if other.impact < sel.impact:
        diffs.append("impact moindre")
    if other.risk > sel.risk:
        diffs.append("risque supérieur")
    if other.confidence < sel.confidence:
        diffs.append("confiance moindre")
    if other.reversibility < sel.reversibility:
        diffs.append("moins réversible")
    return ", ".join(diffs) if diffs else f"score global inférieur ({other.score} < {sel.score})."


__all__ = ["select", "rationale"]
