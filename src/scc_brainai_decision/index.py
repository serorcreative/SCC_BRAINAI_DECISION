"""Index des décisions (recherche déterministe)."""

from __future__ import annotations

from typing import Dict, List, Optional

from scc_brainai_decision.core.clock import canonical
from scc_brainai_decision.core.model import DecisionRecord


class DecisionIndex:
    def __init__(self) -> None:
        self._by_id: Dict[str, DecisionRecord] = {}
        self._text: Dict[str, str] = {}

    def add(self, rec: DecisionRecord) -> None:
        self._by_id[rec.id] = rec
        blob = f"{rec.request.subject} {rec.selected_id} {canonical(rec.qualification)}"
        self._text[rec.id] = blob.lower()

    def rebuild(self, recs: List[DecisionRecord]) -> None:
        self._by_id.clear(); self._text.clear()
        for r in recs:
            self.add(r)

    def get(self, rec_id: str) -> Optional[DecisionRecord]:
        return self._by_id.get(rec_id)

    def search(self, *, status: Optional[str] = None, text: Optional[str] = None,
               limit: int = 50) -> List[DecisionRecord]:
        q = (text or "").strip().lower()
        out: List[DecisionRecord] = []
        for rid in sorted(self._by_id):
            r = self._by_id[rid]
            if status and r.status != status:
                continue
            if q and q not in self._text.get(rid, ""):
                continue
            out.append(r)
        return out[:limit] if limit and limit > 0 else out

    def all(self) -> List[DecisionRecord]:
        return [self._by_id[k] for k in sorted(self._by_id)]

    def __len__(self) -> int:
        return len(self._by_id)


__all__ = ["DecisionIndex"]
