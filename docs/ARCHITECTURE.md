# Architecture de BrainAI Decision

## 1. Position dans SCC

Decision (`15`) est la couche qui **formalise une décision**. Elle se situe entre la
délibération/planification (Reasoning 13, Planning 14) et l'exécution future
(Execution) : elle transforme des options en une décision candidate gouvernée, prête
à être validée par un humain puis exécutée **plus tard**.

```
   Reasoning (13)     Planning (14)     Learning (12)     API (08)
   (délibérations)    (plans)           (enseignements)   (doctrines/ADR)
        \                 \                 \                \
         \ interfaces publiques (lecture)                     \
          ─────────────────────────────────────────────────────
   ▶ Decision (15) ── DecisionEngine : options -> qualification (5 axes)
        │              -> sélection -> conditions/critères -> MANIFESTE DÉCISIONNEL
        │                 (décision candidate, proposée)          │
   data/decisions.jsonl (registre — seul espace d'écriture)       ▼  (Execution, plus tard)
```

## 2. Distinction des rôles

| Couche | Rôle |
|--------|------|
| Reasoning (13) | délibère → décision **candidate légère** (quelle option) |
| Planning (14) | construit un plan d'action |
| **Decision (15)** | **sélectionne, qualifie et formalise** une décision **gouvernée** |

Aucune duplication : Reasoning tranche un problème ; Decision **qualifie et
gouverne** la décision (5 axes, conditions de validation, critères de succès/échec,
révocation, manifeste). C'est le passage d'une intention à une **décision opposable**.

## 3. Chaîne de décision (déterministe)

```
DecisionRequest
  │  ingestion : options directes + Reasoning (délibération) + Planning (plan)
  ▼
qualify()          -> score composite (impact ↑, risque ↓, confiance ↑, réversibilité ↑)
select()           -> option retenue + justification (retenue / écartées)
governance_flags() -> classe (routine / sensible / critique)
conditions         -> validation humaine, succès, échec, révocation
build_manifest()   -> manifeste décisionnel (execution_status = not_executed)
```

Chaque étape est **pure** : mêmes entrées ⇒ même décision. Identifiants dérivés du
contenu.

## 4. Composants

```
core/        config (as_of, poids, seuils) · errors · clock (digest) · model (Option/Request/Record)
providers/   base · deterministic (défaut) · external (Claude/ChatGPT/Gemini) · registry
sources/     decision_gateway (Reasoning/Planning/Learning/API, lecture seule)
ingestion    options depuis délibération / plan / requête
qualification · comparison · conditions · manifest · explanation
validation   HumanValidationPolicy (souveraineté humaine)
index        DecisionIndex · audit · report
engine       DecisionEngine (façade)
cli          scc-brain-decision
```

## 5. Frontière de sûreté

Le `DecisionEngine` **ne détient aucune API d'écriture** vers une autre couche : il
lit (interfaces publiques) et n'écrit que dans son registre de décisions. Il
**n'applique jamais** : le manifeste porte `execution_status = not_executed`, et la
décision reste **proposée** jusqu'à validation humaine (voir
[`GOVERNANCE_SAFETY.md`](GOVERNANCE_SAFETY.md)).

## 6. Invariants tenus

| Invariant | Comment |
|-----------|---------|
| Aucun composant modifié | intégration via interfaces publiques seules |
| Aucune auto-modification | aucun accès en écriture hors du registre de décisions |
| Aucune application automatique | manifeste `not_executed` ; jamais exécuté ici |
| Aucune décision souveraine sans humain | décision `proposed` + `HumanValidationPolicy` |
| Fonctionne sans LLM | décision déterministe ; LLM optionnel |
| Aucun réseau / dépendance externe | stdlib pur ; adaptateurs LLM non branchés |
| Déterminisme maximal | identifiants de contenu + horodatage figé + règles pures |
