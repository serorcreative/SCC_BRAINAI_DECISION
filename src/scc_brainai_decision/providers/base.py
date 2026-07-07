"""Contrat des fournisseurs de décision — point d'extension pour un futur LLM.

La décision **ne dépend d'aucun LLM** : sa qualification et sa sélection par défaut
sont déterministes (règles). Un LLM pourra plus tard *enrichir* l'analyse
décisionnelle (proposer des options, affiner une qualification, critiquer un choix)
**sans jamais** en devenir un prérequis ni valider/appliquer quoi que ce soit.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@runtime_checkable
class DecisionProvider(Protocol):
    name: str

    def available(self) -> bool: ...

    def suggest_options(self, subject: str, options: List[str]) -> Optional[List[Dict[str, Any]]]: ...

    def refine_qualification(self, option: Dict[str, Any]) -> Optional[Dict[str, float]]: ...

    def critique(self, decision: Dict[str, Any]) -> Optional[str]: ...


class BaseProvider:
    name = "base"

    def available(self) -> bool:
        return False

    def suggest_options(self, subject: str, options: List[str]) -> Optional[List[Dict[str, Any]]]:
        return None

    def refine_qualification(self, option: Dict[str, Any]) -> Optional[Dict[str, float]]:
        return None

    def critique(self, decision: Dict[str, Any]) -> Optional[str]:
        return None


__all__ = ["DecisionProvider", "BaseProvider"]
