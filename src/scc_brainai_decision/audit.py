"""Audit de la décision : intégrité, traçabilité, sûreté (gouvernance).

* **intégrité** : l'empreinte de chaque option correspond à son contenu ;
* **traçabilité** : chaque option cite une source ; l'option retenue existe ;
* **sûreté** : toute décision non-proposée porte un approbateur **humain** ; le
  manifeste n'est pas exécuté ; la décision n'est jamais marquée souveraine.
"""

from __future__ import annotations

from typing import Any, Dict, List

from scc_brainai_decision.core.model import DecisionRecord, DecisionStatus


def audit_record(rec: DecisionRecord) -> Dict[str, Any]:
    integrity_broken = sorted(o.id for o in rec.options if not o.verify())
    untraced = sorted(o.id for o in rec.options if not o.sources)
    ids = {o.id for o in rec.options}
    dangling = [] if rec.selected_id in ids else [rec.selected_id]

    safe = True
    reasons: List[str] = []
    if rec.status != DecisionStatus.PROPOSED.value and not rec.validation.get("approver"):
        safe = False; reasons.append("décision non-proposée sans approbateur humain")
    m = rec.execution_manifest
    if m.get("execution_status") not in (None, "not_executed"):
        safe = False; reasons.append("manifeste marqué exécuté (application non permise)")
    if m.get("sovereign") is True:
        safe = False; reasons.append("décision marquée souveraine")

    return {
        "ok": not integrity_broken and not untraced and not dangling and safe,
        "integrity": {"ok": not integrity_broken, "broken": integrity_broken},
        "traceability": {"ok": not untraced and not dangling,
                         "untraced": untraced, "dangling_selected": dangling},
        "safety": {"ok": safe, "reasons": reasons, "status": rec.status},
        "options": len(rec.options),
    }


def audit_all(recs: List[DecisionRecord]) -> Dict[str, Any]:
    reports = {r.id: audit_record(r) for r in recs}
    return {"ok": all(x["ok"] for x in reports.values()) if reports else True,
            "count": len(recs), "per_decision": reports}


__all__ = ["audit_record", "audit_all"]
