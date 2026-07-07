"""Conditions de gouvernance : validation humaine, critères succès/échec, révocation.

Règles **déterministes** dérivées de la qualification de l'option retenue. Elles
matérialisent les garde-fous SCC (garde-fou humain, ADR, mitigation…) sans jamais
appliquer la décision.
"""

from __future__ import annotations

from typing import Any, Dict, List

from scc_brainai_decision.core.model import DecisionOption, DecisionRequest


def validation_conditions(selected: DecisionOption, flags: Dict[str, bool],
                          doctrines: List[str]) -> List[str]:
    conds: List[str] = ["Validation humaine explicite par un approbateur identifié."]
    if flags.get("low_reversibility"):
        conds.append("Action quasi-irréversible : garde-fou humain renforcé (analogue règle T3).")
    if flags.get("high_impact"):
        conds.append("Décision structurante : produire un ADR (SCC-DOC-0009) avant exécution.")
    if flags.get("high_risk"):
        conds.append("Risque élevé : plan de mitigation validé requis avant exécution.")
    if flags.get("high_urgency"):
        conds.append("Urgence élevée : tracer la fenêtre temporelle et l'autorité décisionnaire.")
    for d in doctrines:
        conds.append(f"Conformité vérifiée à la doctrine {d}.")
    return conds


def success_criteria(selected: DecisionOption, request: DecisionRequest) -> List[str]:
    crit = [
        f"L'objectif « {request.subject.strip()} » est atteint par « {selected.name} ».",
        "Aucune contrainte n'est violée.",
        "Aucune alerte critique post-exécution (Control Plane).",
    ]
    if selected.data.get("strategy_scores") or selected.origin == "planning":
        crit.append("Toutes les tâches du plan associé aboutissent sans blocage.")
    return crit


def failure_criteria(selected: DecisionOption) -> List[str]:
    return [
        "L'objectif n'est pas atteint dans le périmètre défini.",
        "Une contrainte ou une doctrine est enfreinte.",
        "Apparition d'un risque critique non anticipé.",
        "Nécessité d'un retour arrière (rollback).",
    ]


def revocation_conditions(selected: DecisionOption) -> List[str]:
    return [
        "Un critère d'échec est constaté.",
        "Le contexte ayant justifié la décision change significativement.",
        "Un veto de gouvernance (Sécurité / Gardien de la Fondation / Qualité) est émis.",
        "Décision explicitement révoquée par un humain.",
    ]


__all__ = ["validation_conditions", "success_criteria", "failure_criteria", "revocation_conditions"]
