"""Adaptateurs LLM externes — emplacements d'extension (non branchés en V1).

Matérialisent la place d'un LLM (Claude, ChatGPT, Gemini…) dans l'analyse
décisionnelle, **sans aucun appel réseau**. Indisponibles tant qu'un transport n'est
pas fourni ; le moteur les ignore alors et décide de façon déterministe.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from scc_brainai_decision.providers.base import BaseProvider


class ExternalDecider(BaseProvider):
    name = "external"

    def __init__(self, client: Optional[Any] = None):
        self._client = client

    def available(self) -> bool:
        return self._client is not None

    def _guard(self):
        raise NotImplementedError(
            f"Fournisseur '{self.name}' : transport non implémenté dans le socle (aucun réseau).")

    def suggest_options(self, subject: str, options: List[str]) -> Optional[List[Dict[str, Any]]]:
        if not self.available():
            return None
        self._guard()

    def refine_qualification(self, option: Dict[str, Any]) -> Optional[Dict[str, float]]:
        if not self.available():
            return None
        self._guard()

    def critique(self, decision: Dict[str, Any]) -> Optional[str]:
        if not self.available():
            return None
        self._guard()


class ClaudeDecider(ExternalDecider):
    name = "claude"


class ChatGPTDecider(ExternalDecider):
    name = "chatgpt"


class GeminiDecider(ExternalDecider):
    name = "gemini"


KNOWN_EXTERNAL = {"claude": ClaudeDecider, "chatgpt": ChatGPTDecider, "gemini": GeminiDecider}

__all__ = ["ExternalDecider", "ClaudeDecider", "ChatGPTDecider", "GeminiDecider", "KNOWN_EXTERNAL"]
