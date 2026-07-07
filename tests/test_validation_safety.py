"""Tests des garde-fous : validation humaine, non-application, audit."""

from __future__ import annotations

import pytest

from scc_brainai_decision.core.errors import ValidationError
from scc_brainai_decision.providers.registry import ProviderRegistry


def test_decision_starts_proposed(decision):
    assert decision["status"] == "proposed"


def test_validate_requires_human(engine, decision):
    with pytest.raises(ValidationError):
        engine.validate(decision["id"], "")


def test_validate_then_revoke(engine, decision):
    did = decision["id"]
    engine.validate(did, "frederique", "go")
    assert engine.get(did)["status"] == "validated"
    assert engine.get(did)["validation"]["approver"] == "frederique"
    engine.revoke(did, "frederique", "contexte changé")
    assert engine.get(did)["status"] == "revoked"


def test_illegal_transition_refused(engine, decision):
    did = decision["id"]
    engine.validate(did, "frederique")
    with pytest.raises(ValidationError):
        engine.reject(did, "frederique")


def test_reject_flow(engine, decision):
    engine.reject(decision["id"], "frederique", "hors périmètre")
    assert engine.get(decision["id"])["status"] == "rejected"


def test_audit_ok(engine, decision):
    assert engine.audit()["ok"] is True


def test_audit_detects_tampering(engine, decision):
    did = decision["id"]
    rec = engine.index.get(did)
    rec.options[0].name = "TAMPERED"
    a = engine.audit()
    assert a["per_decision"][did]["integrity"]["ok"] is False


def test_self_check_no_application(engine, decision):
    sc = engine.self_check()
    assert sc["ok"] is True
    labels = {c["label"] for c in sc["checks"]}
    assert {"no_automatic_application", "works_without_external_llm", "no_llm_no_network"} <= labels


def test_status_survives_reload(config, decision):
    from scc_brainai_decision.engine import DecisionEngine
    e1 = DecisionEngine(config=config)
    did = e1.decisions[0].id
    e1.validate(did, "frederique", "go")
    e2 = DecisionEngine(config=config)   # relit depuis le disque
    assert e2.get(did)["status"] == "validated"
    assert e2.audit()["ok"] is True


def test_providers_fallback():
    reg = ProviderRegistry()
    assert "deterministic" in reg.available()
    for name in ("claude", "chatgpt", "gemini"):
        assert name in reg.names() and name not in reg.available()
    assert reg.select(["claude", "chatgpt"]).name == "deterministic"
