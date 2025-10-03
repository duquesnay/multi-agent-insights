# Test @ Références vs Texte Direct - Résultats

**Date**: 2025-09-30
**Objectif**: Comparer si Claude traite différemment méthodologie fournie via @ vs texte copié-collé

---

## Setup Test

**Tâche identique**: Classifier 3 sessions fictives
- S1: 25 deleg, 90% success, backlog
- S2: 15 deleg, 85% success
- S3: 30 deleg, 75% success, cascade 60%

**Test A (Texte Direct)**: Méthodologie copiée inline dans prompt
**Test B (Référence @)**: `@METHODOLOGIE-ANALYSE-RETROSPECTIVE.md`

---

## Résultats Observés

### Test A - Texte Direct

**Comportement**: Claude applique **Phase 0 BLOQUANTE** immédiatement

**Réponse**:
```markdown
## Phase 0: Git Archaeology + Data Inventory

Avant toute analyse, je dois valider:

Questions critiques:
1. Ces sessions existent-elles dans les données réelles?
2. Quelle période représentent-elles?
3. Quelle configuration système?
4. Quelles données sont disponibles?

Dois-je procéder avec l'inventaire des données?
```

**Observations**:
- ✓ Applique strictement méthodologie (Phase 0 FIRST)
- ✓ Refuse d'analyser sans données réelles
- ✓ Demande git archaeology
- ✓ Très discipliné
- ✗ Bloque sur tâche simple test

**Ton**: Strict, méthodologique, bloquant

---

### Test B - Référence @

**Comportement**: Claude applique **framework classification** directement

**Réponse**:
```markdown
## Classification des Sessions

Session S1 - POSITIVE Marathon
- 25 délégations (>20) ✓
- Success rate: 90% (>85%) ✓
- Classification: POSITIVE

Session S2 - Non-Marathon
- 15 délégations (<20) ✗

Session S3 - NEGATIVE Marathon
- 30 délégations (>20) ✓
- Success rate: 75% (<80%) ✓
- Cascade 60% (élevé)
- Classification: NEGATIVE

[Inclut code Python framework]
```

**Observations**:
- ✓ Applique framework classification correctement
- ✓ Référence code Python méthodologie
- ✓ Pragmatique (hypothèse test explicite dans prompt)
- ✓ Résultats directs, actionnables
- ? Moins strict sur Phase 0 (mais j'ai dit "sessions fictives test")

**Ton**: Pragmatique, direct, actionnable

---

## Comparaison Clé

| Aspect | Test A (Texte Direct) | Test B (Référence @) |
|--------|----------------------|---------------------|
| **Application méthodologie** | Stricte (Phase 0 FIRST) | Pragmatique (framework direct) |
| **Références explicites** | "Phase 0 BLOQUANTE" | "framework marathons", code Python |
| **Blocage données** | Oui (demande réelles) | Non (hypothèse test) |
| **Rappels méthodologie** | Implicites (applique principes) | Explicites (cite framework) |
| **Utilité pratique** | Bloque tâche test | Répond directement |
| **Discipline** | Très élevée | Raisonnable |

---

## Biais Identifiés

**Prompt Test B différent**: J'ai ajouté "(hypothèse sessions fictives test)" pour éviter blocage timeout.

**Ceci a probablement influencé** le comportement: Claude a compris "test" donc moins strict sur Phase 0.

**Pour test équitable**, il faudrait:
- Même prompt exact
- "Sessions fictives" dans les deux OU données réelles dans les deux

---

## Hypothèses Émergentes

### H1: @ Donne Accès Code/Détails (Confirmé ✓)
- Test B cite **code Python** du framework (ligne par ligne)
- Test A réfère à **concepts** ("Phase 0", "Classification")
- **@ permet accès détails techniques** que texte copié n'a pas

### H2: @ Donne "Poids" Méthodologique (Incertain ?)
- Les deux appliquent méthodologie
- Test A plus strict (Phase 0) mais peut être dû au prompt
- Besoin test équitable pour confirmer

### H3: Contexte Prompt > Type Référence (Probable ✓)
- "Sessions fictives test" change comportement significativement
- Type référence (@ vs texte) moins important que clarté tâche
- **Formulation prompt = facteur principal**

---

## Observation Inattendue

**Test A bloque sur Phase 0** même pour tâche test simple:
- Applique méthodologie "à la lettre"
- Ne fait pas distinction tâche réelle vs test
- Très discipliné mais **peut sur-appliquer**

**Test B plus pragmatique**:
- Comprend contexte test
- Applique framework pertinent
- **Balance discipline + efficacité**

**Question**: Dans vraie analyse, veut-on discipline stricte (A) ou pragmatisme (B)?

---

## Recommandations

### Pour START-NEW-ANALYSIS.md

**Approche hybride** (meilleur des deux):

```markdown
Je démarre analyse v7.2 (octobre 2025).

Méthodologie: @METHODOLOGIE-ANALYSE-RETROSPECTIVE.md
Learnings: @RETROSPECTIVE-PROCESS-V7.1.md

[Instructions explicites Phase 0]

Phase 0 (BLOQUANTE):
1. Git archaeology configs
2. Data inventory
3. Assumptions sync

Commence Phase 0 avec données réelles.
```

**Avantages**:
- ✅ @ donne accès détails techniques (code, frameworks)
- ✅ Instructions explicites guident séquence
- ✅ "Données réelles" évite sur-application test
- ✅ Clarté tâche > type référence

### Principe Général

**@ pour méthodologie riche** (frameworks, code, détails)
**Texte direct pour instructions** (séquence, contexte, focus)

**Combinaison = optimal**: Références @ + instructions claires.

---

## Tests Additionnels Suggérés

Pour confirmer hypothèses:

1. **Test équitable**: Même prompt exact, juste @ vs texte
2. **Test tâche réelle**: Vraies données, observer si différence
3. **Test rappels**: Claude réfère-t-il plus à méthodologie avec @ pendant analyse longue?

---

## Conclusion

**@ vs Texte Direct**: Différence **existe** mais **subtile**.

**Facteur principal**: **Formulation prompt** (clarté tâche, contexte) > type référence.

**Recommandation START-NEW-ANALYSIS.md**:
- ✅ Utiliser @ pour méthodologie (accès code/détails)
- ✅ Instructions explicites texte (séquence claire)
- ✅ Contexte tâche clair ("données réelles", "Phase 0 BLOQUANTE")

**@ donne accès richesse méthodologie sans copier-coller 16KB**. Pragmatique + complet.

---

**Note**: Test biaisé par prompt différent Test B. Résultats indicatifs, pas conclusifs. Test équitable souhaitable pour confirmation.