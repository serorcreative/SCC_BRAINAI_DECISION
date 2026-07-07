# Gouvernance & sûreté de la décision

> **Principes cardinaux : aucune auto-modification ; aucune décision appliquée
> automatiquement ; aucune décision souveraine sans validation humaine.**

## 1. La décision reste candidate

Toute décision produite est au statut **`proposed`**. Le moteur ne peut pas produire
une décision « validée » ni déclencher son application.

## 2. Aucune application ici

La décision porte un **manifeste décisionnel** destiné à **Execution**, mais Decision
**n'applique jamais** : `execution_status = not_executed`, `sovereign = false`,
`requires_human_validation = true`. L'exécution éventuelle relèvera d'Execution, après
validation humaine, hors de cette couche.

## 3. Validation humaine obligatoire

Seule une **action humaine explicite** change le statut, via `HumanValidationPolicy` :

| Action | Transition | Exigence |
|--------|-----------|----------|
| `validate` | proposed → validated | approbateur **requis** |
| `reject` | proposed → rejected | approbateur requis |
| `revoke` | validated → revoked | approbateur requis |

Sans approbateur → refus. Transition illégale → refus. Chaque décision est tracée
(action, approbateur, motif, horodatage). Une décision structurante validée relève du
processus **ADR** (SCC-DOC-0009).

## 4. Aucune capacité d'auto-modification

Le `DecisionEngine` **n'importe aucune API d'écriture** d'une autre couche. Il lit
(interfaces publiques) et n'écrit que dans son registre (`data/decisions.jsonl`). Il
est donc **structurellement incapable** de modifier Reasoning, Planning, Learning,
Memory, Kernel, le graphe, une doctrine ou du code.

## 5. Audit

`audit()` vérifie, pour chaque décision :
- **intégrité** : empreinte de chaque option = son contenu ;
- **traçabilité** : chaque option cite une source ; l'option retenue existe ;
- **sûreté** : toute décision non-proposée porte un **approbateur humain** ; le
  manifeste n'est pas exécuté ; la décision n'est pas marquée souveraine.

## 6. Alignement doctrinal

- **Traçabilité complète** ([[SCC-DOC-0016]]) : options et décision tracées.
- **Gouvernance avant extension** ([[SCC-DOC-0015]]) : rien n'est validé/appliqué sans humain.
- **ADR obligatoire** ([[SCC-DOC-0009]]) : une décision structurante validée passe par un ADR.
- **Garde-fou humain T3** : les décisions **critiques** (irréversibles/impactantes)
  exigent une validation humaine renforcée — inscrit dans les conditions de validation.
- **Intelligence lourde optionnelle et branchable** ([[SCC-DOC-0029]]) : le LLM est
  une capacité optionnelle, jamais un prérequis.
