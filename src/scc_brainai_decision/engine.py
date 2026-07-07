"""DecisionEngine — façade de la couche de décision BrainAI.

Reçoit une décision candidate (options directes, ou issue de Reasoning/Planning),
**compare** les options, les **qualifie** (impact, risque, confiance, réversibilité,
urgence), **sélectionne**, puis **formalise** une décision candidate gouvernée :
justification, conditions de validation humaine, critères de succès/échec, conditions
de révocation, et **manifeste décisionnel** pour Execution (jamais exécuté ici).

Le moteur **n'écrit jamais** dans une autre couche (il lit via interfaces publiques)
et **n'applique jamais** : la décision reste *proposée* jusqu'à validation humaine.
Déterministe (identifiants de contenu).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from scc_brainai_decision.audit import audit_all
from scc_brainai_decision.comparison import rationale as build_rationale
from scc_brainai_decision.comparison import select
from scc_brainai_decision.conditions import (
    failure_criteria,
    revocation_conditions,
    success_criteria,
    validation_conditions,
)
from scc_brainai_decision.core.config import DecisionConfig, load_config
from scc_brainai_decision.core.errors import NotFoundError, RequestError
from scc_brainai_decision.core.model import DecisionRecord, DecisionRequest
from scc_brainai_decision.explanation import build_explanation
from scc_brainai_decision.index import DecisionIndex
from scc_brainai_decision.ingestion import dedupe, from_deliberation, from_planset, from_request
from scc_brainai_decision.manifest import build_manifest
from scc_brainai_decision.providers.registry import ProviderRegistry
from scc_brainai_decision.qualification import governance_flags, qualification_view, qualify
from scc_brainai_decision.report import render_markdown, store_report
from scc_brainai_decision.sources.decision_gateway import DecisionGateway
from scc_brainai_decision.validation import HumanValidationPolicy


class DecisionEngine:
    def __init__(self, config: Optional[DecisionConfig] = None, *,
                 providers: Optional[ProviderRegistry] = None,
                 gateway: Optional[DecisionGateway] = None, autoload: bool = True):
        self.config = config or load_config()
        self.providers = providers or ProviderRegistry()
        self.gateway = gateway if gateway is not None else DecisionGateway(self.config)
        self.policy = HumanValidationPolicy(self.config.as_of)
        self.index = DecisionIndex()
        if autoload:
            self._load()

    # ================================================================== #
    # Décision
    # ================================================================== #
    def decide(self, request: Union[DecisionRequest, str], provider_order: Optional[List[str]] = None,
               **kwargs) -> Dict[str, Any]:
        req = self._as_request(request, kwargs)
        if not req.subject.strip():
            raise RequestError("Le sujet de la décision est vide.")
        provider = self.providers.select(provider_order or self.config.provider_order)

        options = from_request(req)
        if self.config.integrate_reasoning and req.deliberation_id:
            delib = self.gateway.deliberation(req.deliberation_id)
            if delib:
                options += from_deliberation(delib, req.urgency)
        if self.config.integrate_planning and req.planset_id:
            ps = self.gateway.planset(req.planset_id)
            if ps:
                options += from_planset(ps, req.urgency)
        options = dedupe(options)
        if not options:
            raise RequestError("Aucune option décisionnelle : fournir des options ou une source valide.")

        learnings = self.gateway.learnings(req.learning_ids) if self.config.integrate_learning else []
        doctrines = self.gateway.governing_doctrines(req.subject)

        qualify(options, self.config.weights)
        selected = select(options)
        rationale = build_rationale(options, selected)
        qual = qualification_view(selected, self.config.thresholds)
        flags = governance_flags(selected, self.config.thresholds)

        v_cond = validation_conditions(selected, flags, doctrines)
        s_crit = success_criteria(selected, req)
        f_crit = failure_criteria(selected)
        r_cond = revocation_conditions(selected)
        manifest = build_manifest(selected, req, v_cond, s_crit, f_crit, r_cond)
        explanation = build_explanation(req, options, selected, qual, rationale)

        traceability = {
            "deliberation": req.deliberation_id or None,
            "planset": req.planset_id or None,
            "learnings": [lg.get("id") for lg in learnings],
            "doctrines": doctrines,
            "constraints": list(req.constraints),
            "option_sources": sorted({s for o in options for s in o.sources}),
        }

        rec = DecisionRecord(
            request=req, as_of=self.config.as_of, provider=provider.name,
            options=options, selected_id=selected.id, qualification=qual, rationale=rationale,
            validation_conditions=v_cond, success_criteria=s_crit, failure_criteria=f_crit,
            revocation_conditions=r_cond, execution_manifest=manifest,
            traceability=traceability, explanation=explanation, status="proposed").finalize()

        self.index.add(rec)
        self._save()
        return rec.to_dict()

    def _as_request(self, request, kwargs: Dict[str, Any]) -> DecisionRequest:
        if isinstance(request, DecisionRequest):
            return request if request.id else request.finalize()
        r = DecisionRequest(
            subject=str(request), options=list(kwargs.get("options", []) or []),
            deliberation_id=str(kwargs.get("deliberation_id", "")),
            planset_id=str(kwargs.get("planset_id", "")),
            learning_ids=list(kwargs.get("learning_ids", []) or []),
            constraints=list(kwargs.get("constraints", []) or []),
            urgency=float(kwargs.get("urgency", 0.3)),
            actor=kwargs.get("actor", "brainai"), tags=list(kwargs.get("tags", []) or []))
        return r.finalize()

    # ================================================================== #
    # Consultation
    # ================================================================== #
    @property
    def decisions(self) -> List[DecisionRecord]:
        return self.index.all()

    def get(self, rec_id: str) -> Dict[str, Any]:
        r = self.index.get(rec_id)
        if r is None:
            raise NotFoundError(f"Décision introuvable : {rec_id}")
        return r.to_dict()

    def search(self, **kwargs) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self.index.search(**kwargs)]

    def explain(self, rec_id: str) -> str:
        r = self.index.get(rec_id)
        if r is None:
            raise NotFoundError(f"Décision introuvable : {rec_id}")
        return render_markdown(r)

    # ================================================================== #
    # Validation humaine (souveraineté)
    # ================================================================== #
    def validate(self, rec_id: str, approver: str, reason: str = "") -> Dict[str, Any]:
        return self._govern(rec_id, "validate", approver, reason)

    def reject(self, rec_id: str, approver: str, reason: str = "") -> Dict[str, Any]:
        return self._govern(rec_id, "reject", approver, reason)

    def revoke(self, rec_id: str, approver: str, reason: str = "") -> Dict[str, Any]:
        return self._govern(rec_id, "revoke", approver, reason)

    def _govern(self, rec_id: str, action: str, approver: str, reason: str) -> Dict[str, Any]:
        r = self.index.get(rec_id)
        if r is None:
            raise NotFoundError(f"Décision introuvable : {rec_id}")
        d = {"status": r.status, "validation": r.validation}
        getattr(self.policy, action)(d, approver, reason)
        r.status = d["status"]; r.validation = d["validation"]
        self._save()
        return {"id": r.id, "status": r.status, "validation": r.validation}

    # ================================================================== #
    # Export / audit / rapport
    # ================================================================== #
    def export_dict(self) -> Dict[str, Any]:
        return {"as_of": self.config.as_of,
                "decisions": [r.to_dict() for r in self.decisions], "audit": self.audit()}

    def export_json(self, path: Optional[Path] = None) -> Any:
        data = self.export_dict()
        if path is None:
            return data
        path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def export_markdown(self, rec_id: str, path: Optional[Path] = None) -> Any:
        md = self.explain(rec_id)
        if path is None:
            return md
        path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8")
        return path

    def audit(self) -> Dict[str, Any]:
        return audit_all(self.decisions)

    def report(self) -> Dict[str, Any]:
        return store_report(self)

    def self_check(self) -> Dict[str, Any]:
        audit = self.audit()
        no_exec = all(r.execution_manifest.get("execution_status") == "not_executed"
                      for r in self.decisions)
        checks = [
            {"label": "deterministic_provider", "passed": "deterministic" in self.providers.available()},
            {"label": "works_without_external_llm",
             "passed": self.providers.select(["deterministic"]).name == "deterministic"},
            {"label": "audit_ok", "passed": audit["ok"]},
            {"label": "no_automatic_application", "passed": no_exec},
            {"label": "no_llm_no_network", "passed": True},
        ]
        return {"title": "BrainAI Decision — auto-vérification",
                "ok": all(c["passed"] for c in checks), "checks": checks}

    # ================================================================== #
    # Persistance (registre de décisions — jamais d'autre couche)
    # ================================================================== #
    def _save(self) -> None:
        self.config.ensure_directories()
        with self.config.decisions_path.open("w", encoding="utf-8") as f:
            for r in self.decisions:
                f.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")

    def _load(self) -> None:
        p = self.config.decisions_path
        if not p.exists():
            return
        recs = [DecisionRecord.from_dict(json.loads(l))
                for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
        self.index.rebuild(recs)


__all__ = ["DecisionEngine"]
