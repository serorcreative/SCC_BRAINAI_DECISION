"""Noyau de la couche de décision : config, erreurs, modèle."""

from __future__ import annotations

from scc_brainai_decision.core.clock import canonical, digest, short_id
from scc_brainai_decision.core.config import DecisionConfig, load_config
from scc_brainai_decision.core.errors import (
    ConfigError,
    DecisionError,
    NotFoundError,
    RequestError,
    SourceUnavailable,
    ValidationError,
)
from scc_brainai_decision.core.model import (
    QUAL_AXES,
    DecisionOption,
    DecisionRecord,
    DecisionRequest,
    DecisionStatus,
    can_transition,
)

__all__ = [
    "canonical", "digest", "short_id",
    "DecisionConfig", "load_config",
    "DecisionError", "ConfigError", "SourceUnavailable", "ValidationError",
    "NotFoundError", "RequestError",
    "QUAL_AXES", "DecisionStatus", "can_transition",
    "DecisionOption", "DecisionRequest", "DecisionRecord",
]
