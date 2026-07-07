"""Modèle de décision BrainAI.

Une **DecisionOption** est une option décisionnelle qualifiée sur cinq axes
(impact, risque, confiance, réversibilité, urgence). Un **DecisionRecord** est la
décision candidate **formalisée et gouvernée** : option retenue, justification,
conditions de validation humaine, critères de succès/échec, conditions de
révocation, et **manifeste décisionnel** utilisable plus tard par Execution.

Tout est déterministe (identifiants dérivés du contenu) et **gouverné** : une
décision reste *proposée* jusqu'à validation humaine ; elle n'est jamais appliquée.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar, Dict, List

from scc_brainai_decision.core.clock import digest, short_id

# Les cinq axes de qualification décisionnelle.
QUAL_AXES = ("impact", "risk", "confidence", "reversibility", "urgency")


class DecisionStatus(str, Enum):
    PROPOSED = "proposed"
    VALIDATED = "validated"
    REJECTED = "rejected"
    REVOKED = "revoked"


_TRANSITIONS = {
    "proposed": {"validated", "rejected"},
    "validated": {"revoked"},
    "rejected": set(),
    "revoked": set(),
}


def can_transition(current: str, target: str) -> bool:
    return target in _TRANSITIONS.get(current, set())


@dataclass
class DecisionOption:
    """Option décisionnelle qualifiée (tracée, scorée)."""

    name: str = ""
    description: str = ""
    origin: str = "manual"                 # reasoning / planning / manual
    impact: float = 0.5
    risk: float = 0.3
    confidence: float = 0.5
    reversibility: float = 0.5
    urgency: float = 0.3
    score: float = 0.0
    selected: bool = False
    sources: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    id: str = ""
    hash: str = ""

    KIND: ClassVar[str] = "option"

    def qualification(self) -> Dict[str, float]:
        return {"impact": self.impact, "risk": self.risk, "confidence": self.confidence,
                "reversibility": self.reversibility, "urgency": self.urgency}

    def _identity(self) -> Dict[str, Any]:
        return {"name": self.name, "origin": self.origin}

    def _content(self) -> Dict[str, Any]:
        return {**self._identity(), "description": self.description,
                **self.qualification(), "sources": sorted(self.sources)}

    def finalize(self) -> "DecisionOption":
        self.id = short_id("opt", self._identity())
        self.hash = digest({**self._content(), "score": self.score})
        return self

    def seal(self) -> "DecisionOption":
        self.hash = digest({**self._content(), "score": self.score})
        return self

    def verify(self) -> bool:
        return self.hash == digest({**self._content(), "score": self.score})

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "kind": self.KIND, "name": self.name,
                "description": self.description, "origin": self.origin,
                "impact": self.impact, "risk": self.risk, "confidence": self.confidence,
                "reversibility": self.reversibility, "urgency": self.urgency,
                "score": self.score, "selected": self.selected,
                "sources": list(self.sources), "tags": list(self.tags),
                "data": dict(self.data), "hash": self.hash}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "DecisionOption":
        o = cls(name=str(d.get("name", "")), description=str(d.get("description", "")),
                origin=str(d.get("origin", "manual")),
                impact=float(d.get("impact", 0.5)), risk=float(d.get("risk", 0.3)),
                confidence=float(d.get("confidence", 0.5)),
                reversibility=float(d.get("reversibility", 0.5)),
                urgency=float(d.get("urgency", 0.3)), score=float(d.get("score", 0.0)),
                selected=bool(d.get("selected", False)), sources=list(d.get("sources", []) or []),
                tags=list(d.get("tags", []) or []), data=dict(d.get("data", {}) or {}))
        o.id = str(d.get("id", "")) or o.finalize().id
        o.hash = str(d.get("hash", "")) or o.hash
        return o


@dataclass
class DecisionRequest:
    """Demande de décision : options directes et/ou sources à intégrer."""

    subject: str
    options: List[Dict[str, Any]] = field(default_factory=list)
    deliberation_id: str = ""
    planset_id: str = ""
    learning_ids: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    urgency: float = 0.3
    actor: str = "brainai"
    tags: List[str] = field(default_factory=list)
    id: str = ""

    def finalize(self) -> "DecisionRequest":
        self.id = short_id("dreq", {"subject": self.subject, "options": self.options,
                                    "deliberation_id": self.deliberation_id,
                                    "planset_id": self.planset_id})
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "subject": self.subject, "options": list(self.options),
                "deliberation_id": self.deliberation_id, "planset_id": self.planset_id,
                "learning_ids": list(self.learning_ids), "constraints": list(self.constraints),
                "urgency": self.urgency, "actor": self.actor, "tags": list(self.tags)}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "DecisionRequest":
        r = cls(subject=str(d.get("subject", "")), options=list(d.get("options", []) or []),
                deliberation_id=str(d.get("deliberation_id", "")),
                planset_id=str(d.get("planset_id", "")),
                learning_ids=list(d.get("learning_ids", []) or []),
                constraints=list(d.get("constraints", []) or []),
                urgency=float(d.get("urgency", 0.3)), actor=str(d.get("actor", "brainai")),
                tags=list(d.get("tags", []) or []))
        r.id = str(d.get("id", "")) or r.finalize().id
        return r


@dataclass
class DecisionRecord:
    """Décision candidate formalisée et gouvernée."""

    request: DecisionRequest
    as_of: str = ""
    options: List[DecisionOption] = field(default_factory=list)
    selected_id: str = ""
    qualification: Dict[str, Any] = field(default_factory=dict)
    rationale: Dict[str, Any] = field(default_factory=dict)
    validation_conditions: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    failure_criteria: List[str] = field(default_factory=list)
    revocation_conditions: List[str] = field(default_factory=list)
    execution_manifest: Dict[str, Any] = field(default_factory=dict)
    traceability: Dict[str, Any] = field(default_factory=dict)
    explanation: Dict[str, Any] = field(default_factory=dict)
    status: str = DecisionStatus.PROPOSED.value
    validation: Dict[str, Any] = field(default_factory=dict)
    provider: str = "deterministic"
    id: str = ""

    def finalize(self) -> "DecisionRecord":
        self.id = short_id("dec", {"request": self.request.id, "selected": self.selected_id,
                                   "options": [o.id for o in self.options]})
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "as_of": self.as_of, "provider": self.provider,
                "request": self.request.to_dict(),
                "options": [o.to_dict() for o in self.options],
                "selected_id": self.selected_id, "qualification": dict(self.qualification),
                "rationale": dict(self.rationale),
                "validation_conditions": list(self.validation_conditions),
                "success_criteria": list(self.success_criteria),
                "failure_criteria": list(self.failure_criteria),
                "revocation_conditions": list(self.revocation_conditions),
                "execution_manifest": dict(self.execution_manifest),
                "traceability": dict(self.traceability), "explanation": dict(self.explanation),
                "status": self.status, "validation": dict(self.validation)}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "DecisionRecord":
        rec = cls(request=DecisionRequest.from_dict(d.get("request", {})),
                  as_of=str(d.get("as_of", "")), provider=str(d.get("provider", "deterministic")),
                  options=[DecisionOption.from_dict(x) for x in d.get("options", [])],
                  selected_id=str(d.get("selected_id", "")),
                  qualification=dict(d.get("qualification", {}) or {}),
                  rationale=dict(d.get("rationale", {}) or {}),
                  validation_conditions=list(d.get("validation_conditions", []) or []),
                  success_criteria=list(d.get("success_criteria", []) or []),
                  failure_criteria=list(d.get("failure_criteria", []) or []),
                  revocation_conditions=list(d.get("revocation_conditions", []) or []),
                  execution_manifest=dict(d.get("execution_manifest", {}) or {}),
                  traceability=dict(d.get("traceability", {}) or {}),
                  explanation=dict(d.get("explanation", {}) or {}),
                  status=str(d.get("status", "proposed")),
                  validation=dict(d.get("validation", {}) or {}))
        rec.id = str(d.get("id", "")) or rec.finalize().id
        return rec


__all__ = ["QUAL_AXES", "DecisionStatus", "can_transition",
           "DecisionOption", "DecisionRequest", "DecisionRecord"]
