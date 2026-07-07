"""Configuration de la couche de décision BrainAI (JSON, sans dépendance).

La décision **sélectionne, qualifie et formalise** une décision candidate gouvernée.
Elle peut *intégrer* les délibérations de Reasoning (13), les plans de Planning (14),
les enseignements de Learning (12) et les doctrines/ADR de l'API (08) via leurs
interfaces publiques — de façon **optionnelle et dégradable**. Elle ne possède ni ne
modifie aucune autre couche.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from scc_brainai_decision.core.errors import ConfigError

DECISION_ROOT = Path(__file__).resolve().parents[3]       # .../15_BRAINAI_DECISION
DEFAULT_SCC_ROOT = DECISION_ROOT.parent                    # .../01_CCSC
DEFAULT_CONFIG_PATH = DECISION_ROOT / "config" / "decision.json"

DEFAULT_AS_OF = "2026-07-06T00:00:00+00:00"

# Pondérations de qualification décisionnelle (déterministes, bornées).
# impact ↑, risque ↓, confiance ↑, réversibilité ↑ (l'urgence est un drapeau de
# gouvernance, non un critère de qualité).
DEFAULT_WEIGHTS = {"impact": 0.30, "risk": 0.30, "confidence": 0.20, "reversibility": 0.20}

# Seuils de gouvernance déclenchant des conditions de validation renforcées.
DEFAULT_THRESHOLDS = {"high_impact": 0.7, "high_risk": 0.6, "low_reversibility": 0.4, "high_urgency": 0.7}


@dataclass
class DecisionConfig:
    decision_root: Path = DECISION_ROOT
    scc_root: Path = DEFAULT_SCC_ROOT
    data_dir: Path = DECISION_ROOT / "data"
    as_of: str = DEFAULT_AS_OF
    integrate_reasoning: bool = True
    integrate_planning: bool = True
    integrate_learning: bool = True
    weights: Dict[str, float] = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))
    thresholds: Dict[str, float] = field(default_factory=lambda: dict(DEFAULT_THRESHOLDS))
    provider_order: List[str] = field(default_factory=lambda: ["deterministic"])
    extra: Dict[str, Any] = field(default_factory=dict)

    @property
    def reasoning_src(self) -> Path:
        return self.scc_root / "13_BRAINAI_REASONING" / "src"

    @property
    def planning_src(self) -> Path:
        return self.scc_root / "14_BRAINAI_PLANNING" / "src"

    @property
    def learning_src(self) -> Path:
        return self.scc_root / "12_BRAINAI_LEARNING" / "src"

    @property
    def api_src(self) -> Path:
        return self.scc_root / "08_API" / "src"

    @property
    def decisions_path(self) -> Path:
        return self.data_dir / "decisions.jsonl"

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> Dict[str, Any]:
        return {"decision_root": str(self.decision_root), "scc_root": str(self.scc_root),
                "data_dir": str(self.data_dir), "as_of": self.as_of,
                "integrate_reasoning": self.integrate_reasoning,
                "integrate_planning": self.integrate_planning,
                "integrate_learning": self.integrate_learning,
                "weights": dict(self.weights), "thresholds": dict(self.thresholds),
                "provider_order": list(self.provider_order)}


def _resolve(base: Path, value: str) -> Path:
    p = Path(value).expanduser()
    return p if p.is_absolute() else (base / p).resolve()


def load_config(path: Optional[Path] = None) -> DecisionConfig:
    config = DecisionConfig()
    target = Path(path) if path else DEFAULT_CONFIG_PATH
    if not target.exists():
        if path is not None:
            raise ConfigError(f"Configuration introuvable : {target}")
        return config
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"Configuration illisible ({target}) : {exc}") from exc

    base = config.decision_root
    if "scc_root" in raw:
        config.scc_root = _resolve(base, raw["scc_root"])
    paths = raw.get("paths", {})
    if "data_dir" in paths:
        config.data_dir = _resolve(base, paths["data_dir"])
    config.as_of = str(raw.get("as_of", DEFAULT_AS_OF))
    config.integrate_reasoning = bool(raw.get("integrate_reasoning", True))
    config.integrate_planning = bool(raw.get("integrate_planning", True))
    config.integrate_learning = bool(raw.get("integrate_learning", True))
    if "weights" in raw:
        config.weights = {**DEFAULT_WEIGHTS, **dict(raw["weights"])}
    if "thresholds" in raw:
        config.thresholds = {**DEFAULT_THRESHOLDS, **dict(raw["thresholds"])}
    config.provider_order = list(raw.get("provider_order", config.provider_order))
    config.extra = dict(raw.get("extra", {}))
    return config


__all__ = ["DECISION_ROOT", "DEFAULT_SCC_ROOT", "DEFAULT_AS_OF", "DEFAULT_WEIGHTS",
           "DEFAULT_THRESHOLDS", "DecisionConfig", "load_config"]
