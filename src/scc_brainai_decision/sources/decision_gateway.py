"""Passerelle décisionnelle — intègre les couches SCC (interfaces publiques).

Réutilise, **sans les modifier** : Reasoning (13) pour une délibération, Planning
(14) pour un plan, Learning (12) pour des enseignements validés, et l'API (08) pour
les doctrines/ADR (contraintes). Localisation dynamique ; intégration **optionnelle
et dégradable** : une source absente est ignorée, la décision continue.
"""

from __future__ import annotations

import importlib
import re
import sys
from typing import Any, Dict, List, Optional

from scc_brainai_decision.core.config import DecisionConfig

_STOP = {"faut", "il", "une", "des", "les", "la", "le", "de", "du", "et", "ou", "à",
         "the", "a", "of", "to", "should", "we"}


def _keywords(text: str, limit: int = 6) -> List[str]:
    toks = re.findall(r"[a-zàâäéèêëîïôöùûüç0-9\-]{3,}", (text or "").lower())
    out: List[str] = []
    for t in toks:
        if t not in _STOP and t not in out:
            out.append(t)
    return sorted(out)[:limit]


class DecisionGateway:
    def __init__(self, config: DecisionConfig, reasoning_engine: Optional[Any] = None,
                 planning_engine: Optional[Any] = None, learning_engine: Optional[Any] = None,
                 api: Optional[Any] = None):
        self._config = config
        self._reason = reasoning_engine
        self._plan = planning_engine
        self._learn = learning_engine
        self._api = api
        self._tried = {"reason": reasoning_engine is not None, "plan": planning_engine is not None,
                       "learn": learning_engine is not None, "api": api is not None}

    def _add_path(self, path) -> bool:
        if not path.exists():
            return False
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
        return True

    def _load(self, key, path, module, attr):
        cur = getattr(self, f"_{key}")
        if cur is None and not self._tried[key]:
            self._tried[key] = True
            if self._add_path(path):
                try:
                    obj = getattr(importlib.import_module(module), attr)
                    setattr(self, f"_{key}", obj() if attr != "SccApi" else obj())
                except Exception:  # noqa: BLE001
                    setattr(self, f"_{key}", None)
        return getattr(self, f"_{key}")

    def _reasoning(self):
        return self._load("reason", self._config.reasoning_src, "scc_brainai_reasoning", "ReasoningEngine")

    def _planning(self):
        return self._load("plan", self._config.planning_src, "scc_brainai_planning", "PlanningEngine")

    def _learning(self):
        return self._load("learn", self._config.learning_src, "scc_brainai_learning", "LearningEngine")

    def _api_obj(self):
        return self._load("api", self._config.api_src, "scc_api", "SccApi")

    def available(self) -> Dict[str, bool]:
        return {"reasoning": self._reasoning() is not None, "planning": self._planning() is not None,
                "learning": self._learning() is not None, "api": self._api_obj() is not None}

    # -- intégrations --------------------------------------------------- #
    def deliberation(self, delib_id: str) -> Optional[Dict[str, Any]]:
        eng = self._reasoning()
        if eng is None or not delib_id:
            return None
        try:
            return eng.get(delib_id)
        except Exception:  # noqa: BLE001
            return None

    def planset(self, ps_id: str) -> Optional[Dict[str, Any]]:
        eng = self._planning()
        if eng is None or not ps_id:
            return None
        try:
            return eng.get(ps_id)
        except Exception:  # noqa: BLE001
            return None

    def learnings(self, ids: List[str]) -> List[Dict[str, Any]]:
        eng = self._learning()
        if eng is None or not ids:
            return []
        out = []
        for lid in ids:
            try:
                out.append(eng.get(lid))
            except Exception:  # noqa: BLE001
                continue
        return out

    def governing_doctrines(self, subject: str) -> List[str]:
        api = self._api_obj()
        if api is None:
            return []
        seen: List[str] = []
        for kw in _keywords(subject):
            try:
                nodes = api.dispatch("graph.search", {"type": "Doctrine", "query": kw, "limit": 3}).to_dict().get("data", [])
            except Exception:  # noqa: BLE001
                nodes = []
            for n in nodes:
                if n["id"] not in seen:
                    seen.append(n["id"])
        return sorted(seen)


__all__ = ["DecisionGateway"]
