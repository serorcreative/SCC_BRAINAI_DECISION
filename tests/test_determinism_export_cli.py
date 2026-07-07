"""Tests de déterminisme, export, explication et CLI."""

from __future__ import annotations

import json

from scc_brainai_decision.cli import main
from scc_brainai_decision.core.config import DecisionConfig
from scc_brainai_decision.engine import DecisionEngine


def _decide(data_dir):
    eng = DecisionEngine(config=DecisionConfig(data_dir=data_dir, integrate_reasoning=False,
                                               integrate_planning=False, integrate_learning=False))
    return eng.decide("Faut-il publier ?",
                      options=[{"name": "Publier", "impact": 0.8, "risk": 0.3, "reversibility": 0.5},
                               {"name": "Différer", "impact": 0.4, "risk": 0.1, "reversibility": 0.9}],
                      urgency=0.5)


def test_deterministic_decision(tmp_path):
    a = _decide(tmp_path / "a")
    b = _decide(tmp_path / "b")
    assert json.dumps(a, sort_keys=True, ensure_ascii=False) == \
           json.dumps(b, sort_keys=True, ensure_ascii=False)


def test_explain_markdown(engine, decision):
    md = engine.explain(decision["id"])
    for section in ("## Options comparées", "## Conditions de validation humaine",
                    "## Critères de succès", "## Manifeste décisionnel"):
        assert section in md
    assert "validation humaine" in md
    assert "not_executed" in md


def test_export_and_report(engine, decision, tmp_path):
    data = engine.export_dict()
    assert data["decisions"]
    jp = engine.export_json(tmp_path / "d.json")
    assert jp.exists()
    report = engine.report()
    assert report["total_decisions"] == 1
    assert report["by_status"].get("proposed") == 1
    assert "by_class" in report


def test_cli_decide_and_validate(tmp_path, capsys):
    cfg = tmp_path / "decision.json"
    cfg.write_text(json.dumps({"paths": {"data_dir": str(tmp_path / "d")},
                               "as_of": "2026-07-06T00:00:00+00:00",
                               "integrate_reasoning": False, "integrate_planning": False,
                               "integrate_learning": False}), encoding="utf-8")
    rc = main(["--config", str(cfg), "decide", "Faut-il publier ?",
               "--option", "Publier|0.8|0.3|0.6|0.5", "--option", "Différer|0.4|0.1|0.8|0.9",
               "--urgency", "0.5"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    did = out["id"]
    assert out["status"] == "proposed"
    rc = main(["--config", str(cfg), "validate", did, "--by", "frederique", "--reason", "go"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["status"] == "validated"


def test_cli_audit(tmp_path, capsys):
    cfg = tmp_path / "decision.json"
    cfg.write_text(json.dumps({"paths": {"data_dir": str(tmp_path / "d")},
                               "integrate_reasoning": False, "integrate_planning": False,
                               "integrate_learning": False}), encoding="utf-8")
    main(["--config", str(cfg), "decide", "Sujet", "--option", "A|0.5"])
    capsys.readouterr()
    rc = main(["--config", str(cfg), "audit"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["ok"] is True
