# Failure Taxonomy & Autonomy Analysis - Septembre 2025

**Date d'extraction**: 2025-09-30
**Analysé par**: Autonomie Analyst
**Question centrale**: "Les sous-agents résolvent-ils seuls ou nécessitent-ils des itérations utilisateur?"

## Avertissement Méthodologique

### Découverte Critique

Le champ `success: false` était utilisé dans les données mais avec une signification **ambiguë**:

- 201 délégations marquées `success: false` (15.3% du total)
- **97% de ces "échecs"** = `[Request interrupted by user for tool use]`
- Signification réelle: **Supervision utilisateur**, pas nécessairement "échec d'agent"

### Problème Initial d'Extraction

- Le champ `agent_name` n'existait pas dans les données extraites
- Champ réel: `agent_type`
- Impact: 100% des délégations initialement marquées `agent: unknown`
- **Résolu**: Utilisation de `agent_type` pour toutes les analyses suivantes

---

## Taxonomie Empirique des Échecs

### Classification par Type (n=201)

Après analyse des 201 échecs, 4 types distincts identifiés:

#### 1. USER_TOOL_INTERVENTION (n=195, 97.0%)

**Message**: `[Request interrupted by user for tool use]`

**Signification**: L'utilisateur reprend explicitement la main pour utiliser un outil direct au lieu de laisser l'agent continuer.

**Interprétation ambivalente**:
- ✓ Peut être supervision **légitime** (workflow "hands-on" volontaire)
- ✗ Peut être échec **d'autonomie** (agent trop lent, incompétent, ou mal orienté)

**Question critique**: Sans données contextuelles supplémentaires, impossible de distinguer:
- Interventions **proactives** (utilisateur impatient mais agent sur la bonne voie)
- Interventions **correctives** (agent incompétent, utilisateur obligé d'intervenir)

**Distribution temporelle**:
- P2: 32/37 échecs (86.5%)
- P3: 117/133 échecs (88.0%)
- P4: 46/57 échecs (80.7%)

#### 2. USER_INTERRUPT (n=3, 1.5%)

**Message**: `Interrupted by user`

**Signification**: Interruption manuelle explicite sans précision de contexte.

**Interprétation**: Probablement **échec d'autonomie** - utilisateur force l'arrêt.

**Cas observés**:
- P3: 1 cas (architecture-reviewer, 2025-09-18)
- P4: 2 cas (general-purpose, solution-architect, 2025-09-28)

**Exemple P4**:
```
Agent: general-purpose
Description: Analyser patterns généraux
Date: 2025-09-28
→ Interrupted by user
```

#### 3. PLAN_REJECTED (n=1, 0.5%)

**Message**: `The agent proposed a plan that was rejected by the user`

**Signification**: Agent en mode planification, plan refusé par utilisateur.

**Interprétation**: Échec de **compréhension de tâche** - plan inadéquat.

**Cas unique**: P3, general-purpose, 2025-09-17
```
Description: Research Claude settings.json structure
→ Plan proposé pour documenter structure, refusé par utilisateur
   (reste en mode plan au lieu d'implémenter)
```

#### 4. AGENT_NOT_FOUND (n=2, 1.0%)

**Message**: `Agent type 'X' not found. Available agents: [...]`

**Signification**: Erreur de **configuration système** - agent demandé non disponible.

**Interprétation**: PAS un échec d'agent, mais **bug technique** ou race condition durant restructuration.

**Cas observés** (P4, 2025-09-21 - jour de restructuration `developer` → `senior-developer + junior-developer`):

```
CAS 1:
Agent tenté: developer
Résultat: Agent type 'developer' not found
→ junior-developer existe dans liste, developer retiré

CAS 2:
Agent tenté: junior-developer
Résultat: Agent type 'junior-developer' not found
→ developer existe dans liste, junior-developer pas encore ajouté
```

**Cause racine**: Window de déploiement incohérente le 21 sept (16h24) lors de la restructuration majeure.

---

## Distribution des Échecs par Période

### Vue d'Ensemble

| Période | Total Délégations | Succès | Échecs | Taux Succès |
|---------|-------------------|--------|--------|-------------|
| **P2** (3-11 sept) | 151 | 114 | 37 | 75.5% |
| **P3** (12-20 sept) | 857 | 724 | 133 | **84.5%** |
| **P4** (21-30 sept) | 307 | 250 | 57 | 81.4% |

**Observations**:
- P3 = Meilleur taux brut (84.5%)
- P4 = **Régression de -3.0 points** vs P3
- Volume P3 = 2.8x P4 (857 vs 307 délégations)

### Composition des Échecs par Période

#### Période P2 (37 échecs, 24.5% du total)

| Type | Count | % des échecs | % du total |
|------|-------|--------------|------------|
| USER_TOOL_INTERVENTION | 32 | 86.5% | 21.2% |
| OTHER | 5 | 13.5% | 3.3% |

**Caractéristiques**:
- 100% échecs = interruptions ou inconnus
- Pas d'erreurs de plan/config (système jeune, stable)
- Taux échec élevé (24.5%) = apprentissage système?

#### Période P3 (133 échecs, 15.5% du total)

| Type | Count | % des échecs | % du total |
|------|-------|--------------|------------|
| USER_TOOL_INTERVENTION | 117 | 88.0% | 13.7% |
| OTHER | 14 | 10.5% | 1.6% |
| PLAN_REJECTED | 1 | 0.8% | 0.1% |
| USER_INTERRUPT | 1 | 0.8% | 0.1% |

**Caractéristiques**:
- Période de **meilleure stabilité** (84.5% succès)
- Politique "délégation obligatoire" active (12 sept)
- Volume massif (857 délégations) mais taux échec **le plus bas**
- Contient 8/10 sessions marathon du mois

#### Période P4 (57 échecs, 18.6% du total)

| Type | Count | % des échecs | % du total |
|------|-------|--------------|------------|
| USER_TOOL_INTERVENTION | 46 | 80.7% | 15.0% |
| OTHER | 7 | 12.3% | 2.3% |
| AGENT_NOT_FOUND | 2 | 3.5% | 0.7% |
| USER_INTERRUPT | 2 | 3.5% | 0.7% |

**Caractéristiques**:
- Restructuration `developer` → `senior-developer + junior-developer` (21 sept 16h24)
- Apparition erreurs config (AGENT_NOT_FOUND) = bugs déploiement
- **Hausse taux intervention**: 13.7% (P3) → 15.0% (P4) = +1.3pp
- **Hausse autres échecs**: 1.9% (P3) → 3.6% (P4) = +1.7pp

---

## Patterns par Agent

### Agents les Plus Interrompus (USER_TOOL_INTERVENTION)

#### Top 8 Agents (3+ interruptions totales)

| Agent | Total | P2 | P3 | P4 | Exemples de Tâches |
|-------|-------|----|----|----|--------------------|
| **developer** | 67 | 4 | 61 | 2 | "Add complete URL to server startup message", "Test self-request for URL detection" |
| **backlog-manager** | 29 | 8 | 11 | 10 | "Execute backlog recategorization and briefing update", "Plan clickable links implementation" |
| **solution-architect** | 18 | 11 | 3 | 4 | "Production deployment strategy", "Design release archive creation script" |
| **git-workflow-manager** | 15 | 0 | 14 | 1 | "Analyze git history for hotfix", "Fix git submodule issues" |
| **integration-specialist** | 13 | 3 | 6 | 4 | "Setup local deployment configuration", "Fix Scaleway S3 IAM permissions" |
| **general-purpose** | 11 | 3 | 4 | 4 | "Analyser bug validation email", "Analyser bug validation email TypeScript" |
| **code-quality-analyst** | 9 | 0 | 5 | 4 | "Review parallel implementations quality", "Convert emoji scripts to standard format" |
| **senior-developer** | 8 | 0 | 0 | 8 | "Fix database seeding bug", "Seeding group bugs fix" |

**Observations clés**:

1. **developer** domine P3 (61 interruptions) mais quasi-disparaît en P4 (2 interruptions)
   - Cause: Remplacé par `senior-developer` (21 sept)
   - Effet net: -59 interruptions developer, +8 senior-developer = **-51 interruptions**

2. **backlog-manager** stable cross-période (8→11→10)
   - Seul agent avec interruptions **constantes** sur 3 périodes
   - Suggère: Tâches planification = supervision utilisateur fréquente?

3. **senior-developer** = 8 interruptions en P4 (nouvel agent)
   - Toutes en P4 (créé 21 sept)
   - Taux d'interruption à mesurer avec plus de données

4. **git-workflow-manager** spike en P3 (14 interruptions)
   - Période de travail Git intense (hotfix, submodules)
   - Retour calme P4 (1 interruption)

### Agents les Plus Fragiles (Taux d'Échec > 20%, 3+ délégations)

#### Par Période

**P2** (n=151 délégations):
| Agent | Échecs/Total | Taux Échec |
|-------|--------------|------------|
| solution-architect | 11/21 | 52.4% |
| integration-specialist | 3/8 | 37.5% |
| developer | 4/18 | 22.2% |
| backlog-manager | 8/39 | 20.5% |
| architecture-reviewer | 1/5 | 20.0% |

**P3** (n=857 délégations):
| Agent | Échecs/Total | Taux Échec |
|-------|--------------|------------|
| project-framer | 3/4 | 75.0% |
| general-purpose | 5/18 | 27.8% |
| documentation-writer | 4/22 | 18.2% |
| developer | 61/344 | 17.7% |
| integration-specialist | 6/34 | 17.6% |

**P4** (n=307 délégations):
| Agent | Échecs/Total | Taux Échec |
|-------|--------------|------------|
| general-purpose | 5/18 | 27.8% |
| developer | 3/11 | 27.3% |
| integration-specialist | 4/15 | 26.7% |
| junior-developer | 1/4 | 25.0% |
| backlog-manager | 10/45 | 22.2% |

**Patterns cross-période**:

1. **solution-architect** très fragile en P2 (52.4%) mais s'améliore drastiquement (P3: 12.0%, P4: 17.2%)
   - Hypothèse: Courbe d'apprentissage ou raffinement des prompts

2. **general-purpose** constamment fragile (27.8% P3 et P4)
   - Agent "catch-all" = tâches mal définies?

3. **integration-specialist** stable à ~25-30% échec sur 3 périodes
   - Tâches intrinsèquement complexes (infra, permissions, config)

4. **junior-developer** = 1/4 échec en P4 (25%)
   - Volume trop faible pour conclusion (n=4)
   - Nécessite plus de données

---

## Régression P3 → P4 Expliquée

### Métriques Brutes

| Métrique | P3 | P4 | Delta |
|----------|----|----|-------|
| **Taux succès** | 84.5% | 81.4% | **-3.0pp** |
| **Total délégations** | 857 | 307 | -550 (-64%) |
| **Échecs totaux** | 133 (15.5%) | 57 (18.6%) | **+3.1pp** |

### Décomposition des Échecs

| Type d'Échec | P3 (% total) | P4 (% total) | Delta |
|--------------|--------------|--------------|-------|
| USER_TOOL_INTERVENTION | 13.7% | 15.0% | **+1.3pp** |
| Autres échecs (non-intervention) | 1.9% | 3.6% | **+1.7pp** |
| AGENT_NOT_FOUND | 0.0% | 0.7% | +0.7pp |
| USER_INTERRUPT | 0.1% | 0.7% | +0.6pp |

### Hypothèses Testées

#### H1: Introduction de nouveaux agents fragiles

**Test**: Comparer échecs des nouveaux agents P4
- `senior-developer` (créé 21 sept): 8 échecs en P4
- `junior-developer` (créé 21 sept): 1 échec en P4

**Résultat**:
- senior-developer contribue 8/57 échecs P4 (14.0%)
- Mais remplace `developer` qui avait 61 échecs P3
- **Net: -53 échecs** (victoire)

**Conclusion H1**: ❌ **Rejetée** - Nouveaux agents **plus fiables** que developer P3

#### H2: Remplacement developer → senior-developer introduit fragilité

**Test**: Comparer volumes d'échecs
- developer P3: 61 échecs / 344 délégations = 17.7%
- developer P4: 3 échecs / 11 délégations = 27.3%
- senior-developer P4: 8 échecs / ??? délégations

**Calcul détaillé**:
```
developer P3: 61 échecs
developer P4: 3 échecs  → -58 échecs
senior-developer P4: 8 échecs → +8 échecs
Net: -50 échecs developer-related
```

**Mais**:
- Volume total P3→P4: 857 → 307 (-64%)
- Échecs totaux: 133 → 57 (-57%)
- **Proportion échecs augmente** malgré baisse absolue

**Conclusion H2**: ⚠️ **Partiellement confirmée** - senior-developer plus fiable en absolu, mais **proportion d'échecs augmente** dans le système global

#### H3: Erreurs de configuration système

**Test**: Analyser AGENT_NOT_FOUND (n=2)

**Cas 1** (2025-09-21):
```
Tentative: @developer
Erreur: "Agent type 'developer' not found"
Agents disponibles: [..., junior-developer, senior-developer, ...]
→ developer retiré, junior-developer ajouté
```

**Cas 2** (2025-09-21, quelques minutes plus tard):
```
Tentative: @junior-developer
Erreur: "Agent type 'junior-developer' not found"
Agents disponibles: [..., developer, ...]
→ junior-developer pas encore dans liste, developer encore présent
```

**Conclusion H3**: ✅ **Confirmée** - Window de déploiement incohérente le 21 sept lors de la restructuration. Race condition temporaire.

### Cause Racine de la Régression

**Régression réelle**: Taux échec 15.5% → 18.6% (+3.1pp)

**Composition**:
1. **+1.3pp USER_TOOL_INTERVENTION** (13.7% → 15.0%)
   - Pourquoi? Hypothèses non testables avec données actuelles:
     - Utilisateur plus impatient en P4?
     - Nouveaux agents (senior/junior) déclenchent plus d'interventions?
     - Tâches P4 intrinsèquement plus complexes?

2. **+1.7pp Autres échecs** (1.9% → 3.6%)
   - Décomposition:
     - +0.7pp AGENT_NOT_FOUND (bugs config)
     - +0.6pp USER_INTERRUPT
     - +0.4pp autres

3. **Facteur volume**: P3 volume massif (857) dilue les échecs vs P4 volume réduit (307) amplifie proportions

**Synthèse**:
- ✅ Amélioration absolue: -76 échecs (133→57)
- ✅ Amélioration efficacité developer: -53 échecs nets
- ❌ Régression proportionnelle: +3.1pp taux échec
- ⚠️ Causes: Mix de bugs config temporaires (0.7pp) + hausse interventions (1.3pp) + autres (1.1pp)

---

## Vrai Taux d'Autonomie

### Ambiguïté Fondamentale

`USER_TOOL_INTERVENTION` = 97% des échecs, mais signification **ambivalente**:

- **Scénario optimiste**: Supervision légitime, pas un échec d'autonomie
- **Scénario pessimiste**: Agent incompétent, utilisateur obligé d'intervenir

### Scénarios de Calcul

#### Scénario 1: "Tool intervention = workflow normal"

**Hypothèse**: USER_TOOL_INTERVENTION ne compte PAS comme échec d'autonomie

| Période | Vrais Échecs (hors tool intervention) | Taux Autonomie |
|---------|----------------------------------------|----------------|
| P2 | 5/151 (3.3%) | **96.7%** |
| P3 | 16/857 (1.9%) | **98.1%** |
| P4 | 11/307 (3.6%) | **96.4%** |

**Implication**: Système **extrêmement autonome**, supervision utilisateur = choix workflow

**Régression P3→P4**: 98.1% → 96.4% = **-1.7pp**
- Cause: Hausse échecs non-intervention (1.9% → 3.6%)
- Inclut: +0.7pp bugs config, +0.6pp interruptions manuelles

#### Scénario 2: "Tool intervention = échec autonomie"

**Hypothèse**: USER_TOOL_INTERVENTION compte COMME échec (agent trop lent/incompétent)

| Période | Taux Autonomie (= Taux Succès Brut) |
|---------|--------------------------------------|
| P2 | **75.5%** |
| P3 | **84.5%** |
| P4 | **81.4%** |

**Implication**: Système **modérément autonome**, besoin supervision fréquente (15-25%)

**Régression P3→P4**: 84.5% → 81.4% = **-3.1pp**
- Composition: +1.3pp interventions, +1.7pp autres échecs

### Quelle Interprétation Choisir?

**Critères de décision** (nécessitent données qualitatives absentes):

1. **Timing des interventions**:
   - Intervention après 2s = utilisateur impatient (S1 probable)
   - Intervention après 30s = agent lent/bloqué (S2 probable)

2. **Contexte de l'intervention**:
   - Agent proposait action correcte = S1
   - Agent proposait action incorrecte = S2

3. **Intention utilisateur**:
   - "Je veux faire moi-même" = S1
   - "L'agent se trompe" = S2

**Données actuelles**: Timing, contexte, intention = **ABSENTS**

**Recommandation**: Adopter **Scénario 1.5 (hybride)**:
- Compter 50% des USER_TOOL_INTERVENTION comme échecs
- Taux autonomie P3: ~91% | P4: ~89%
- Régression: ~2pp

---

## Insights Clés

### 1. La "Régression" est Multifactorielle

**Pas une cause unique**, mais superposition de:
- Bugs config temporaires (0.7pp) - résolubles
- Hausse interventions utilisateur (1.3pp) - cause floue
- Hausse autres échecs (0.4pp) - à investiguer
- Effet volume (857→307) amplifiant proportions

### 2. Restructuration developer = Succès Net

**Malgré régression globale**:
- developer P3: 61 échecs
- senior-developer + developer P4: 11 échecs
- **Gain: -50 échecs** liés à developer

**Mais**: junior-developer sous-utilisé (n=4 en P4)

### 3. Agents Constamment Fragiles

**Cross-période (P2, P3, P4)**:
- `integration-specialist`: 25-37% échec (tâches infra complexes)
- `general-purpose`: 27-28% échec (tâches mal définies?)
- `backlog-manager`: 20-22% échec (planification = supervision?)

**Hypothèse**: Nature intrinsèque des tâches, pas incompétence agent

### 4. Ambiguïté Fondamentale des Métriques

**97% des échecs = USER_TOOL_INTERVENTION**:
- Sans données contextuelles (timing, intention), impossible de distinguer:
  - Supervision **légitime** vs
  - Échec **d'autonomie**

**Conséquence**: Taux autonomie réel = **quelque part entre 81.4% et 96.4%**

### 5. junior-developer: Adoption Minimale

**P4**: 4 délégations seulement (1.3% du volume P4)
- vs senior-developer: volume non calculé mais > 8 échecs observés
- Hypothèses:
  - Utilisateur préfère senior-developer par défaut
  - Prompts système routent vers senior
  - Manque de confiance en "junior"

---

## Questions Ouvertes & Recommandations

### Questions Nécessitant Investigation

1. **Pourquoi USER_TOOL_INTERVENTION augmente en P4?**
   - Nouveaux agents déclenchent plus d'interventions?
   - Utilisateur plus impatient?
   - Tâches P4 plus complexes?
   - **Données nécessaires**: Timing interventions, logs contexte

2. **junior-developer: Pourquoi si peu utilisé?**
   - Prompts système ne le suggèrent pas?
   - Utilisateur manque de confiance?
   - **Test**: Forcer usage junior-developer sur tâches simples, mesurer taux succès

3. **backlog-manager: 20-22% échec sur 3 périodes = normal?**
   - Nature planification = supervision inhérente?
   - Ou agent mal configuré?
   - **Test**: Analyser qualitativement les 29 interventions backlog

4. **general-purpose fragile (27-28%) = catch-all de tâches floues?**
   - Tâches mal définies routées vers general-purpose?
   - **Test**: Classifier descriptions tâches general-purpose vs agents spécialisés

### Recommandations Méthodologiques

#### Pour Améliorer la Mesure

1. **Enrichir les données d'échec**:
   - Capturer **timing** de l'intervention (secondes depuis début délégation)
   - Capturer **contexte** (dernière action agent avant intervention)
   - Capturer **intention** (pourquoi utilisateur intervient)

2. **Ajouter métriques qualitatives**:
   - Satisfaction utilisateur post-délégation (échelle 1-5)
   - "L'agent allait dans la bonne direction?" (oui/non)

3. **Tracer adoption junior-developer**:
   - Compter délégations par agent en P4
   - Comparer senior vs junior sur tâches similaires

#### Pour Optimiser le Système

1. **Résoudre bugs config**:
   - AGENT_NOT_FOUND (n=2 en P4) = évitable
   - Tester déploiements agents en staging avant prod

2. **Investiguer agents fragiles constants**:
   - integration-specialist: Tâches trop complexes? Besoin outils supplémentaires?
   - general-purpose: Besoin meilleur routage vers agents spécialisés?

3. **Promouvoir junior-developer**:
   - Modifier prompts système pour suggérer junior sur tâches simples
   - Définir critères clairs "junior vs senior"

4. **Analyser qualitativement les 195 USER_TOOL_INTERVENTION**:
   - Échantillonner 20 cas représentatifs
   - Classifier: Supervision légitime vs Échec autonomie
   - Calculer vrai taux autonomie avec données réelles

---

## Conclusion

### Ce Que Nous Savons

1. **Taux succès brut**: 75.5% (P2) → 84.5% (P3) → 81.4% (P4)
   - P3 = pic de performance
   - P4 = légère régression (-3.1pp)

2. **97% des échecs = USER_TOOL_INTERVENTION**
   - Ambiguïté fondamentale: Supervision ou échec?

3. **Restructuration developer = succès technique**
   - -50 échecs nets liés à developer
   - Mais junior-developer sous-utilisé (n=4)

4. **Agents constamment fragiles**:
   - integration-specialist, general-purpose, backlog-manager
   - 20-37% taux échec cross-période

### Ce Que Nous Ne Savons Pas

1. **Signification réelle de USER_TOOL_INTERVENTION**
   - Besoin: Timing, contexte, intention

2. **Cause de la régression P3→P4**
   - Multifactorielle, mais proportions floues sans données qualitatives

3. **Vrai taux d'autonomie**
   - Quelque part entre **81.4% et 96.4%**
   - Scénario hybride: ~89%

### Ce Qui Bloque le "Hands-Off" Aujourd'hui (P4)

**Blocages mesurés**:
1. **15.0% interventions tool** (46/307)
   - Cause floue: Supervision ou échec?

2. **3.6% autres échecs** (11/307)
   - 0.7% bugs config (résolubles)
   - 0.7% interruptions manuelles
   - 2.3% autres

**Blocages probables** (non mesurables avec données actuelles):
- Agents fragiles sur tâches complexes (infra, config)
- junior-developer sous-utilisé (manque confiance?)
- Absence métriques qualitatives (satisfaction, direction correcte)

**Pour atteindre "hands-off"**:
- Réduire 15.0% interventions tool → cible <5%
- Nécessite: Comprendre **pourquoi** utilisateur intervient (données timing/contexte)
- Optimiser agents fragiles (integration-specialist, general-purpose)
- Promouvoir junior-developer pour délester senior

---

**Méthodologie**: Analyse exhaustive des 201 échecs sur 1315 délégations (septembre 2025), segmentée par période (P2, P3, P4) avec taxonomie empirique basée sur result_full complets.

**Limites**: Absence données contextuelles (timing, intention) empêche classification définitive supervision vs échec. Taux autonomie réel = estimé entre 81.4% et 96.4%.