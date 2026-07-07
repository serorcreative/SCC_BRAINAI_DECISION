"""Test d'intégration : ingérer Reasoning (13) et Planning (14) via interfaces publiques.

Construit une délibération réelle (Reasoning) et un plan réel (Planning) dans des
stores isolés, injecte un DecisionGateway pointant dessus, et vérifie que la décision
ingère bien leurs options — sans modifier aucun composant. Ignoré proprement si les
couches ne sont pas localisables.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_REASON = _ROOT / "13_BRAINAI_REASONING" / "src"
_PLAN = _ROOT / "14_BRAINAI_PLANNING" / "src"

_available = _REASON.exists() and _PLAN.exists()
if _available:
    for p in (_REASON, _PLAN):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))

pytestmark = pytest.mark.skipif(not _available, reason="Reasoning/Planning non localisables.")


def test_decide_from_reasoning(tmp_path):
    from scc_brainai_reasoning.core.config import ReasoningConfig
    from scc_brainai_reasoning.engine import ReasoningEngine
    from scc_brainai_decision.core.config import DecisionConfig
    from scc_brainai_decision.engine import DecisionEngine
    from scc_brainai_decision.sources.decision_gateway import DecisionGateway

    reason = ReasoningEngine(config=ReasoningConfig(data_dir=tmp_path / "r", ground_facts=False))
    delib = reason.reason("Approche A ou B ?",
                          options=[{"name": "Approche A", "benefit": 0.8}, {"name": "Approche B", "benefit": 0.4}])

    cfg = DecisionConfig(data_dir=tmp_path / "d", integrate_reasoning=True,
                         integrate_planning=False, integrate_learning=False)
    eng = DecisionEngine(config=cfg, gateway=DecisionGateway(cfg, reasoning_engine=reason))
    rec = eng.decide("Choisir l'approche", deliberation_id=delib["id"])

    origins = {o["origin"] for o in rec["options"]}
    assert "reasoning" in origins
    assert any(s.startswith("reasoning:") for o in rec["options"] for s in o["sources"])
    assert rec["traceability"]["deliberation"] == delib["id"]
    assert rec["status"] == "proposed"
    assert eng.audit()["ok"] is True


def test_decide_from_planning(tmp_path):
    from scc_brainai_planning.core.config import PlanningConfig
    from scc_brainai_planning.engine import PlanningEngine
    from scc_brainai_decision.core.config import DecisionConfig
    from scc_brainai_decision.engine import DecisionEngine
    from scc_brainai_decision.sources.decision_gateway import DecisionGateway

    planning = PlanningEngine(config=PlanningConfig(data_dir=tmp_path / "p",
                                                    integrate_learning=False, integrate_reasoning=False))
    ps = planning.plan("Construire la couche API")

    cfg = DecisionConfig(data_dir=tmp_path / "d", integrate_reasoning=False,
                         integrate_planning=True, integrate_learning=False)
    eng = DecisionEngine(config=cfg, gateway=DecisionGateway(cfg, planning_engine=planning))
    rec = eng.decide("Choisir la stratégie de plan", planset_id=ps["id"])

    origins = {o["origin"] for o in rec["options"]}
    assert "planning" in origins
    assert rec["traceability"]["planset"] == ps["id"]
    # chaque option de plan cite sa source
    assert any(s.startswith("planning:") for o in rec["options"] for s in o["sources"])
    assert eng.audit()["ok"] is True
