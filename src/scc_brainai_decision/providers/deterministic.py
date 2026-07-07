"""Décideur déterministe — la qualification/sélection par défaut de BrainAI Decision.

Aucun LLM, aucun réseau : la décision est portée par des règles pures. Ce fournisseur
garantit que Decision **fonctionne toujours**, même sans IA.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from scc_brainai_decision.providers.base import BaseProvider


class DeterministicDecider(BaseProvider):
    name = "deterministic"

    def available(self) -> bool:
        return True

    def suggest_options(self, subject: str, options: List[str]) -> Optional[List[Dict[str, Any]]]:
        return None

    def refine_qualification(self, option: Dict[str, Any]) -> Optional[Dict[str, float]]:
        return None

    def critique(self, decision: Dict[str, Any]) -> Optional[str]:
        return None


__all__ = ["DeterministicDecider"]
