"""Rapports de décision — résumé d'une décision et du registre."""

from __future__ import annotations

from typing import Any, Dict, List

from scc_brainai_decision.core.model import DecisionRecord


def record_summary(rec: DecisionRecord) -> Dict[str, Any]:
    selected = next((o for o in rec.options if o.id == rec.selected_id), None)
    return {
        "id": rec.id, "subject": rec.request.subject,
        "options": len(rec.options),
        "selected": selected.name if selected else None,
        "class": rec.qualification.get("class"),
        "status": rec.status,
    }


def store_report(engine) -> Dict[str, Any]:
    recs = engine.decisions
    by_status: Dict[str, int] = {}
    by_class: Dict[str, int] = {}
    for r in recs:
        by_status[r.status] = by_status.get(r.status, 0) + 1
        c = r.qualification.get("class", "?")
        by_class[c] = by_class.get(c, 0) + 1
    audit = engine.audit()
    return {
        "as_of": engine.config.as_of,
        "total_decisions": len(recs),
        "by_status": dict(sorted(by_status.items())),
        "by_class": dict(sorted(by_class.items())),
        "audit_ok": audit["ok"],
        "decisions": [record_summary(r) for r in recs],
        "safety_note": "Toute décision est candidate ; aucune application automatique ; validation humaine requise.",
    }


def render_markdown(rec: DecisionRecord) -> str:
    q = rec.qualification
    lines: List[str] = [
        f"# Décision — {rec.id}",
        "",
        f"> `as_of` : {rec.as_of} · fournisseur : {rec.provider} · statut : **{rec.status}**",
        "",
        f"**Sujet** : {rec.request.subject}",
        "",
        "## Options comparées", "",
        "| Option | Score | Impact | Risque | Confiance | Réversibilité | Retenue |",
        "|--------|-------|--------|--------|-----------|---------------|---------|",
    ]
    for o in sorted(rec.options, key=lambda x: (-x.score, x.id)):
        lines.append(f"| {o.name} | {o.score} | {o.impact} | {o.risk} | {o.confidence} "
                     f"| {o.reversibility} | {'✅' if o.selected else ''} |")
    lines += ["", "## Qualification de l'option retenue", "",
              f"- classe de gouvernance : **{q.get('class')}**",
              f"- drapeaux : {q.get('flags')}",
              "", "## Pourquoi ce choix", "", rec.rationale.get("why_retained", ""), ""]
    if rec.rationale.get("discarded"):
        lines.append("Options écartées :")
        for d in rec.rationale["discarded"]:
            lines.append(f"- {d['option']} (score {d['score']}) — {d['why']}")
        lines.append("")
    for title, key in (("Conditions de validation humaine", "validation_conditions"),
                       ("Critères de succès", "success_criteria"),
                       ("Critères d'échec", "failure_criteria"),
                       ("Conditions de révocation", "revocation_conditions")):
        lines += [f"## {title}", ""]
        for item in getattr(rec, key):
            lines.append(f"- {item}")
        lines.append("")
    lines += ["## Manifeste décisionnel (pour Execution, plus tard)", "",
              f"- option : {rec.execution_manifest.get('selected_option')} · "
              f"`execution_status = {rec.execution_manifest.get('execution_status')}` · "
              f"`requires_human_validation = {rec.execution_manifest.get('requires_human_validation')}`",
              "",
              "> Décision **candidate** : validation humaine explicite requise ; "
              "jamais appliquée automatiquement.",
              "",
              "*Décision déterministe BrainAI — sans réseau ni LLM obligatoire.*"]
    return "\n".join(lines) + "\n"


__all__ = ["record_summary", "store_report", "render_markdown"]
