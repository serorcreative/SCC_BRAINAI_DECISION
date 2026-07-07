"""SCC BrainAI Decision — couche officielle de décision de BrainAI.

**Sélectionne, qualifie et formalise** une décision candidate gouvernée : reçoit une
décision candidate (options directes, ou issue de Reasoning/Planning), compare les
options, les qualifie (impact, risque, confiance, réversibilité, urgence),
sélectionne, puis produit une décision candidate structurée — justification,
conditions de validation humaine, critères de succès/échec, conditions de révocation,
et **manifeste décisionnel** utilisable plus tard par Execution.

Decision n'est ni Kernel, ni Memory, ni Learning, ni Reasoning, ni Planning. Il
**réutilise** leurs interfaces publiques, sans modifier aucun composant.

Garde-fous : aucune auto-modification ; **aucune décision appliquée
automatiquement** ; **aucune décision souveraine sans validation humaine** (une
décision reste *proposée*). Fonctionne **sans aucune IA** (décision déterministe ;
LLM optionnel et branchable). Stdlib pur, sans réseau, déterministe.
"""

from __future__ import annotations

__version__ = "1.0.0"

from scc_brainai_decision.core.config import DecisionConfig, load_config
from scc_brainai_decision.core.model import (
    DecisionOption,
    DecisionRecord,
    DecisionRequest,
    DecisionStatus,
)
from scc_brainai_decision.engine import DecisionEngine
from scc_brainai_decision.providers.registry import ProviderRegistry
from scc_brainai_decision.validation import HumanValidationPolicy

__all__ = [
    "__version__",
    "DecisionEngine",
    "DecisionConfig",
    "load_config",
    "DecisionRequest",
    "DecisionOption",
    "DecisionRecord",
    "DecisionStatus",
    "ProviderRegistry",
    "HumanValidationPolicy",
]
