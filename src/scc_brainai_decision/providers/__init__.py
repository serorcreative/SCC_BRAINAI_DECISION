"""Fournisseurs de décision : déterministe (défaut) + emplacements LLM."""

from __future__ import annotations

from scc_brainai_decision.providers.base import BaseProvider, DecisionProvider
from scc_brainai_decision.providers.deterministic import DeterministicDecider
from scc_brainai_decision.providers.external import (
    ChatGPTDecider,
    ClaudeDecider,
    ExternalDecider,
    GeminiDecider,
)
from scc_brainai_decision.providers.registry import ProviderRegistry

__all__ = [
    "DecisionProvider", "BaseProvider", "DeterministicDecider",
    "ExternalDecider", "ClaudeDecider", "ChatGPTDecider", "GeminiDecider",
    "ProviderRegistry",
]
