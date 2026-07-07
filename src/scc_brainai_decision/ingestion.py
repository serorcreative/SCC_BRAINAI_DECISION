"""Ingestion des options décisionnelles (déterministe).

Construit des :class:`DecisionOption` qualifiées à partir : d'une délibération
Reasoning (options classées + scores), d'un plan Planning (stratégies scorées), et
d'options fournies directement. Chaque option est **tracée** vers sa source.
"""

from __future__ import annotations

from typing import Any, Dict, List

from scc_brainai_decision.core.model import DecisionOption, DecisionRequest

_IRREVERSIBLE = ["supprim", "publier", "publication", "irréversible", "irreversible",
                 "détruire", "detruire", "migration", "production", "basculer",
                 "envoyer", "diffuser", "supprimer"]


def _reversibility(text: str) -> float:
    return 0.2 if any(w in text.lower() for w in _IRREVERSIBLE) else 0.6


def _clamp(v: float) -> float:
    return max(0.0, min(1.0, round(float(v), 3)))


def from_deliberation(delib: Dict[str, Any], urgency: float) -> List[DecisionOption]:
    ranking = (delib.get("arbitration", {}) or {}).get("ranking", [])
    src = f"reasoning:{delib.get('id', '')}"
    options: List[DecisionOption] = []
    for entry in ranking:
        name = entry.get("option", "")
        sc = entry.get("scores", {})
        options.append(DecisionOption(
            name=name, description=f"Option issue de la délibération {delib.get('id','')}.",
            origin="reasoning",
            impact=_clamp(sc.get("benefit", 0.5)), risk=_clamp(sc.get("risk", 0.3)),
            confidence=_clamp(sc.get("confidence", 0.5)),
            reversibility=_reversibility(name), urgency=_clamp(urgency),
            sources=[src], tags=["reasoning"], data={"deliberation_scores": sc}).finalize())
    return options


def from_planset(ps: Dict[str, Any], urgency: float) -> List[DecisionOption]:
    src = f"planning:{ps.get('id', '')}"
    options: List[DecisionOption] = []
    for strat in ps.get("strategies", []):
        sc = strat.get("scores", {})
        name = strat.get("name", "")
        options.append(DecisionOption(
            name=f"Plan : {name}", description=strat.get("description", ""),
            origin="planning",
            impact=_clamp(sc.get("impact", 0.5)), risk=_clamp(sc.get("risk", 0.3)),
            confidence=_clamp(sc.get("coverage", 0.5)),
            reversibility=0.5, urgency=_clamp(urgency),
            sources=[src], tags=["planning"], data={"strategy_scores": sc}).finalize())
    return options


def from_request(request: DecisionRequest) -> List[DecisionOption]:
    options: List[DecisionOption] = []
    for o in request.options:
        name = str(o.get("name", "")).strip()
        if not name:
            continue
        desc = str(o.get("description", ""))
        options.append(DecisionOption(
            name=name, description=desc, origin="manual",
            impact=_clamp(o.get("impact", 0.5)), risk=_clamp(o.get("risk", 0.3)),
            confidence=_clamp(o.get("confidence", 0.5)),
            reversibility=_clamp(o.get("reversibility", _reversibility(name + " " + desc))),
            urgency=_clamp(o.get("urgency", request.urgency)),
            sources=[f"request:{request.id}"], tags=["manual"],
            data={k: v for k, v in o.items() if k not in
                  ("name", "description", "impact", "risk", "confidence", "reversibility", "urgency")}).finalize())
    return options


def dedupe(options: List[DecisionOption]) -> List[DecisionOption]:
    uniq: Dict[str, DecisionOption] = {}
    for o in options:
        uniq.setdefault(o.id, o)
    return sorted(uniq.values(), key=lambda o: o.id)


__all__ = ["from_deliberation", "from_planset", "from_request", "dedupe"]
