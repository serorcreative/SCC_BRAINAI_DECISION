"""Fixtures des tests de décision (isolées, déterministes, hermétiques).

L'intégration Reasoning/Planning/Learning est désactivée par défaut ; un test dédié
vérifie l'intégration réelle via leurs interfaces publiques.
"""

from __future__ import annotations

import pytest

from scc_brainai_decision.core.config import DecisionConfig
from scc_brainai_decision.engine import DecisionEngine


@pytest.fixture
def config(tmp_path):
    return DecisionConfig(data_dir=tmp_path / "data", integrate_reasoning=False,
                          integrate_planning=False, integrate_learning=False)


@pytest.fixture
def engine(config):
    return DecisionEngine(config=config)


@pytest.fixture
def decision(engine):
    return engine.decide(
        "Faut-il publier la nouvelle API en production ?",
        options=[{"name": "Publier maintenant", "impact": 0.8, "risk": 0.6, "confidence": 0.6, "reversibility": 0.2},
                 {"name": "Publier en beta privée", "impact": 0.6, "risk": 0.2, "confidence": 0.7, "reversibility": 0.8},
                 {"name": "Différer", "impact": 0.3, "risk": 0.1, "confidence": 0.8, "reversibility": 0.9}],
        urgency=0.5)
