"""Primitives déterministes : sérialisation canonique et empreintes.

La décision est **entièrement déterministe** : les identifiants des options et des
enregistrements de décision dérivent de leur **contenu**. Stdlib pur.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def short_id(prefix: str, obj: Any) -> str:
    return f"{prefix}_{digest(obj)[:12]}"


__all__ = ["canonical", "digest", "short_id"]
