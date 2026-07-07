# Qualification & gouvernance décisionnelle

## 1. Les cinq axes

Chaque option est qualifiée sur cinq axes bornés 0..1 :

| Axe | Sens | Effet sur le score |
|-----|------|--------------------|
| **impact** | importance de la décision | ↑ favorable |
| **risque** | dangerosité | ↓ favorable (on utilise `1 − risque`) |
| **confiance** | degré de certitude | ↑ favorable |
| **réversibilité** | facilité à défaire | ↑ favorable (sécurité) |
| **urgence** | pression temporelle | **drapeau de gouvernance** (pas un critère de qualité) |

## 2. Score composite

```
score = w_impact·impact + w_risk·(1 − risque) + w_confidence·confiance + w_reversibility·réversibilité
défaut : 0.30 / 0.30 / 0.20 / 0.20
```

L'option de meilleur score est **retenue** (départage déterministe par identifiant).
L'urgence n'entre **pas** dans le score : elle module les **conditions de validation**.

## 3. Drapeaux et classe de gouvernance

Des seuils (configurables) lèvent des drapeaux : `high_impact`, `high_risk`,
`low_reversibility`, `high_urgency`. La **classe** en découle :

| Classe | Condition | Conséquence |
|--------|-----------|-------------|
| **critique** | faible réversibilité **et** fort impact | garde-fou humain renforcé (analogue **règle T3**) |
| **sensible** | fort risque **ou** fort impact | vigilance accrue |
| **routine** | sinon | validation humaine standard |

## 4. Conditions générées (déterministes)

Selon la classe et les drapeaux de l'option retenue :

- **Validation humaine** : toujours ; renforcée si irréversible (T3), ADR si
  structurante (SCC-DOC-0009), plan de mitigation si risque élevé, traçage temporel
  si urgence élevée, conformité aux **doctrines** pertinentes (ancrées via l'API).
- **Critères de succès** : objectif atteint, contraintes respectées, aucune alerte
  critique, (si plan) tâches abouties.
- **Critères d'échec** : objectif manqué, contrainte enfreinte, risque critique,
  besoin de rollback.
- **Conditions de révocation** : critère d'échec constaté, changement de contexte,
  veto de gouvernance, révocation humaine explicite.

## 5. Manifeste décisionnel

Le manifeste agrège l'option retenue, les préconditions (validation), les critères de
succès/échec et les conditions d'abandon (révocation). Il porte
`execution_status = not_executed`, `requires_human_validation = true`,
`sovereign = false`. C'est le contrat que **Execution** (couche future) consommera —
jamais Decision.
