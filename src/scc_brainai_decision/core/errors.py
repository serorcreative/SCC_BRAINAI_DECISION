"""Hiérarchie d'exceptions de la couche de décision BrainAI."""

from __future__ import annotations


class DecisionError(Exception):
    """Erreur de base de la couche de décision."""


class ConfigError(DecisionError):
    """Configuration absente, illisible ou invalide."""


class SourceUnavailable(DecisionError):
    """Une source (Reasoning, Planning, Learning, API) est indisponible."""


class ValidationError(DecisionError):
    """Transition de validation humaine interdite."""


class NotFoundError(DecisionError):
    """Décision introuvable."""


class RequestError(DecisionError):
    """Demande de décision mal formée (sujet manquant, options invalides)."""


__all__ = ["DecisionError", "ConfigError", "SourceUnavailable", "ValidationError",
           "NotFoundError", "RequestError"]
