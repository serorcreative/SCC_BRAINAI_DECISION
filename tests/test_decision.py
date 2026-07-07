"""Tests de la construction de décision (comparaison, qualification, formalisation)."""

from __future__ import annotations

import pytest

from scc_brainai_decision.core.errors import RequestError


def test_decision_structure(decision):
    d = decision
    for key in ("request", "options", "selected_id", "qualification", "rationale",
                "validation_conditions", "success_criteria", "failure_criteria",
                "revocation_conditions", "execution_manifest", "traceability", "explanation"):
        assert key in d
    assert len(d["options"]) == 3


def test_compares_and_selects_best(decision):
    scored = {o["name"]: o["score"] for o in decision["options"]}
    selected = next(o for o in decision["options"] if o["selected"])
    assert selected["score"] == max(scored.values())
    # « Publier en beta privée » : meilleur équilibre risque/réversibilité
    assert selected["name"] == "Publier en beta privée"


def test_five_qualification_axes(decision):
    for o in decision["options"]:
        for axis in ("impact", "risk", "confidence", "reversibility", "urgency"):
            assert 0.0 <= o[axis] <= 1.0


def test_governance_class_and_flags(decision):
    q = decision["qualification"]
    assert q["class"] in ("routine", "sensible", "critique")
    assert set(q["flags"]) == {"high_impact", "high_risk", "low_reversibility", "high_urgency"}


def test_critical_option_enriched_conditions(engine):
    d = engine.decide("Migration production irréversible",
                      options=[{"name": "Basculer", "impact": 0.9, "risk": 0.7,
                                "confidence": 0.6, "reversibility": 0.15, "urgency": 0.8}])
    assert d["qualification"]["class"] == "critique"
    conds = " ".join(d["validation_conditions"])
    assert "ADR" in conds                      # SCC-DOC-0009
    assert "irréversible" in conds             # garde-fou renforcé
    assert "mitigation" in conds               # risque élevé


def test_conditions_and_criteria_present(decision):
    assert decision["validation_conditions"]
    assert len(decision["success_criteria"]) >= 3
    assert len(decision["failure_criteria"]) >= 3
    assert len(decision["revocation_conditions"]) >= 3


def test_explanation_why_retained_and_discarded(decision):
    ex = decision["explanation"]
    assert ex["retained"] == "Publier en beta privée"
    assert ex["why_retained"]
    assert len(ex["discarded"]) == 2
    assert all("why" in d for d in ex["discarded"])


def test_manifest_for_execution_not_executed(decision):
    m = decision["execution_manifest"]
    assert m["executable"] is True
    assert m["execution_status"] == "not_executed"
    assert m["requires_human_validation"] is True
    assert m["sovereign"] is False
    # le manifeste embarque critères et conditions
    assert m["preconditions"] and m["success_criteria"] and m["abort_conditions"]


def test_traceability_sources(decision):
    tr = decision["traceability"]
    assert "option_sources" in tr
    for o in decision["options"]:
        assert o["sources"]


def test_no_options_rejected(engine):
    with pytest.raises(RequestError):
        engine.decide("Sujet sans options")


def test_empty_subject_rejected(engine):
    with pytest.raises(RequestError):
        engine.decide("   ", options=[{"name": "X"}])
