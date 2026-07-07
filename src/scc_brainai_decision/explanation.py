"""Explication décisionnelle — pourquoi une option est retenue ou écartée."""

from __future__ import annotations

from typing import Any, Dict, List

from scc_brainai_decision.core.model import DecisionOption


def build_explanation(request, options: List[DecisionOption], selected: DecisionOption,
                      qualification: Dict[str, Any], rationale: Dict[str, Any]) -> Dict[str, Any]:
    narrative: List[str] = [
        f"Sujet : « {request.subject.strip()} ».",
        f"{len(options)} option(s) comparée(s) sur cinq axes "
        "(impact, risque, confiance, réversibilité, urgence).",
        f"Option retenue : « {selected.name} » — {rationale['why_retained']}",
        f"Classe de gouvernance : {qualification.get('class')}.",
        "Décision CANDIDATE : validation humaine explicite requise ; jamais appliquée "
        "automatiquement.",
    ]
    return {
        "options": [{"name": o.name, "score": o.score, "selected": o.selected,
                     "qualification": o.qualification()} for o in
                    sorted(options, key=lambda x: (-x.score, x.id))],
        "retained": rationale["retained"],
        "why_retained": rationale["why_retained"],
        "discarded": rationale["discarded"],
        "narrative": narrative,
    }


__all__ = ["build_explanation"]
