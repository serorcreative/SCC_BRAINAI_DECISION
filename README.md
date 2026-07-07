# SCC BrainAI Decision

**Couche officielle de décision de BrainAI.**

Decision **sélectionne, qualifie et formalise** une décision candidate gouvernée.
Il n'est ni Kernel (orchestration), ni Memory (expérience), ni Learning
(apprentissages), ni Reasoning (délibération), ni Planning (plans) :

- **Kernel** orchestre. · **Memory** conserve. · **Learning** apprend. ·
  **Reasoning** délibère. · **Planning** planifie.
- **Decision** reçoit une décision candidate (options directes, ou issue de
  Reasoning/Planning), **compare** les options, les **qualifie** sur cinq axes
  (impact, risque, confiance, réversibilité, urgence), **sélectionne**, puis produit
  une décision candidate **structurée et gouvernée** : justification, conditions de
  validation humaine, critères de succès/échec, conditions de révocation, et
  **manifeste décisionnel** utilisable plus tard par **Execution**.

> **Garde-fous : aucune auto-modification ; aucune décision appliquée
> automatiquement ; aucune décision souveraine sans validation humaine** (une
> décision reste *proposée*). **Fonctionne sans aucune IA** (décision déterministe ;
> LLM optionnel et branchable). Stdlib pur, sans réseau, déterministe.

## Réutilisation, jamais duplication

Decision **ingère** les délibérations de **Reasoning (13)**, les plans de **Planning
(14)**, les enseignements de **Learning (12)** et les doctrines de l'**API (08)** via
leurs **interfaces publiques**, sans les modifier. Le manifeste produit est destiné à
une future couche **Execution** — mais Decision **n'applique jamais**.

## Installation

```bash
cd 15_BRAINAI_DECISION
python -m pip install -e .        # expose la commande `scc-brain-decision`
```

Aucune dépendance externe.

## Utilisation (CLI)

```bash
scc-brain-decision decide "Faut-il publier la nouvelle API en production ?" \
    --option "Publier maintenant|0.8|0.6|0.6|0.2" \
    --option "Publier en beta privée|0.6|0.2|0.7|0.8" \
    --option "Différer|0.3|0.1|0.8|0.9" --urgency 0.5
# --option format : nom|impact|risque|confiance|réversibilité|urgence
scc-brain-decision decide "Choisir l'approche" --deliberation <id>    # ingère Reasoning
scc-brain-decision decide "Choisir la stratégie" --planset <id>       # ingère Planning
scc-brain-decision explain <id>                       # décision lisible (Markdown)
scc-brain-decision validate <id> --by frederique --reason "go"        # validation HUMAINE
scc-brain-decision reject <id> --by frederique
scc-brain-decision search --status proposed
scc-brain-decision report | audit | self-check | providers
```

## Utilisation (Python)

```python
from scc_brainai_decision import DecisionEngine

engine = DecisionEngine()
rec = engine.decide("Faut-il publier ?",
                    options=[{"name": "Publier", "impact": 0.8, "risk": 0.3},
                             {"name": "Différer", "impact": 0.4, "risk": 0.1, "reversibility": 0.9}])
print(rec["qualification"]["class"], rec["status"])          # routine proposed
engine.validate(rec["id"], approver="frederique", reason="go")  # humain requis
```

## Composants

`DecisionEngine` · `DecisionRequest` · `DecisionOption` · `DecisionRecord` ·
`HumanValidationPolicy` · `ProviderRegistry` (LLM optionnel) · `DecisionGateway`
(intégration Reasoning/Planning/Learning/API).

Détails : [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) ·
[`docs/DECISION_MODEL.md`](docs/DECISION_MODEL.md) ·
[`docs/QUALIFICATION_GOVERNANCE.md`](docs/QUALIFICATION_GOVERNANCE.md) ·
[`docs/GOVERNANCE_SAFETY.md`](docs/GOVERNANCE_SAFETY.md).

## Tests

```bash
python -m pytest -q      # 28 tests (déterministes ; 2 intégrations Reasoning/Planning réelles)
```
