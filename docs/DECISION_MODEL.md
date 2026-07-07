# Modèle de décision

## 1. La demande (`DecisionRequest`) — entrée

```json
{
  "id": "dreq_…", "subject": "Faut-il publier la nouvelle API en production ?",
  "options": [{"name": "Publier", "impact": 0.8, "risk": 0.6, "reversibility": 0.2}],
  "deliberation_id": "", "planset_id": "", "learning_ids": [],
  "constraints": [], "urgency": 0.5, "actor": "brainai"
}
```

Les options peuvent être **fournies directement**, et/ou **ingérées** depuis une
délibération Reasoning (`deliberation_id`) ou un plan Planning (`planset_id`).

## 2. L'option (`DecisionOption`) — qualifiée sur cinq axes

```json
{
  "id": "opt_…", "name": "Publier en beta privée", "origin": "manual",
  "impact": 0.6, "risk": 0.2, "confidence": 0.7, "reversibility": 0.8, "urgency": 0.5,
  "score": 0.72, "selected": true, "sources": ["request:…"], "hash": "…"
}
```

- `origin` : `reasoning` / `planning` / `manual` (traçabilité de provenance) ;
- cinq axes bornés 0..1 ; `score` = composite pondéré.

## 3. La décision (`DecisionRecord`) — formelle et gouvernée

```
{ request, options[], selected_id, qualification{axes, score, flags, class},
  rationale{retained, why_retained, discarded[]},
  validation_conditions[], success_criteria[], failure_criteria[], revocation_conditions[],
  execution_manifest{…, execution_status: "not_executed"},
  traceability, explanation, status, validation }
```

- **qualification** : les 5 axes de l'option retenue + `class` (routine / sensible /
  critique) + drapeaux de gouvernance.
- **rationale** : pourquoi l'option est **retenue** et pourquoi les autres sont
  **écartées** (par axe).
- **conditions & critères** : validation humaine, succès, échec, révocation.
- **execution_manifest** : destiné à Execution, `execution_status = not_executed`.
- **status** : `proposed` → `validated` | `rejected` ; `validated` → `revoked`.

## 4. Traçabilité (aval → amont)

```
Décision ──▶ Option retenue ──▶ sources (request / reasoning:… / planning:…)
   │
   └──▶ traceability { deliberation, planset, learnings, doctrines, option_sources }
```

Chaque option cite ses sources ; la décision référence délibération/plan/
enseignements/doctrines intégrés.

## 5. Déterminisme

Identifiants dérivés du **contenu** ; scoring et sélection purs ; horodatage figé
(`as_of`). Décider deux fois sur la même demande produit la **même** décision
(vérifié en processus et cross-process).
