# Résumé Exécutif: Analyse des Patterns de Routage

**Date**: 2025-09-30
**Rapport complet**: [routage-patterns-analysis.md](./routage-patterns-analysis.md)

---

## Question Centrale

**"Le general agent choisit-il le bon sous-agent?"**

## Réponse Courte

**Majoritairement oui, avec amélioration post-restructuration, mais 3 blocages persistent:**

1. `junior-developer` pas adopté (1.3% usage en P4)
2. Biais vers généraliste quand hésitation
3. Agents fantômes jamais utilisés (`content-developer`: 0%, `project-framer`: <1%)

---

## Découvertes Clés

### ✓ Ce Qui Fonctionne Bien

**1. Pattern Git → git-workflow-manager** (P3: 153 calls)
- Pattern le plus clair et le plus fort
- Aucun mauvais routage détecté
- Collaboration bidirectionnelle `developer ↔ git-workflow-manager` (90 transitions)

**2. Amélioration P3 → P4**
- Mauvais routages: 13.9% → 3.6% (**-73%**)
- `refactoring-specialist`: 1.3% → 10.7% (**+8x**)
- Self-loops: 35.6% → 29.2% (meilleure collaboration)

**3. Émergence Quality Chain** (P4 uniquement)
- `architecture-reviewer → performance-optimizer → refactoring-specialist → senior-developer`
- Signe d'utilisation des safeguards scope creep

### ✗ Ce Qui Bloque le "Hands-Off"

**1. junior-developer Pas Adopté**
- Disponible depuis 21 sept, mais seulement **4 calls (1.3%)** en P4
- **Impact**: Tâches simples vont vers senior-developer (gaspillage)
- **Cause probable**: Description peu claire, pas de trigger words

**2. Routage par Défaut Vers Généraliste**
- P3: `developer` explose à **40.1%** (344 calls)
  - 77.9% pour testing (légitime)
  - 13.1% implementation + 6.1% debugging (auraient dû aller vers spécialistes)
- P4: `senior-developer` 22.8% (amélioration mais persiste)
- **11 cas de mauvais routage** identifiés en P4 (3.6%)

**3. Agents Fantômes**
- `content-developer`: **0 calls** en P3 ET P4
- `project-framer`: <1% en P3-P4 (utilisé seulement en P2 pour setup initial)
- **Impact**: Complexité inutile si pas utilisés

### ≈ Overhead backlog-manager?

- Toujours dans le **top 3** (P2: 25.8%, P3: 10.0%, P4: 14.7%)
- Self-loop élevé: 22-26 dans toutes périodes
- **Question**: Légitime (décomposition planning) ou overhead?

---

## Analyse Période 3: Pourquoi developer Explose?

**344 calls (40.1%)** — breakdown:

| Catégorie | Volume | % | Légitime? |
|-----------|--------|---|-----------|
| Testing | 268 | 77.9% | ✓ Oui (pas de spécialiste testing) |
| Implementation | 45 | 13.1% | ≈ Mixte (certains auraient dû aller vers spécialistes) |
| Debugging | 21 | 6.1% | ≈ Mixte |
| Documentation | 4 | 1.2% | ✗ Non (content-developer existe) |
| Refactoring | 2 | 0.6% | ✗ Non (refactoring-specialist existe) |

**Conclusion**: L'explosion est majoritairement due à TDD (testing légitime), mais ~15-20% sont des mauvais routages.

---

## Actions Prioritaires

### 1. Clarifier junior-developer (URGENT)

**Problème**: 4 calls seulement, tâches simples vont vers senior.

**Actions**:
- Ajouter exemples explicites dans description: "fix typos, simple refactoring, basic implementations"
- Ajouter trigger words: "simple", "straightforward", "quick fix", "basic"
- Dans general agent: "Always consider if junior-developer can handle this before routing to senior-developer"

**Métrique**: Passer de 1.3% à >5% usage.

### 2. Réduire biais généraliste

**Problème**: Hésitation → routage vers developer/senior-developer.

**Actions**:
- Améliorer descriptions agents (plus explicites sur domaines)
- Ajouter exemples concrets de tâches dans chaque description
- Créer guide de routage pour general agent
- Créer rubrique "Task Complexity Assessment"

**Métrique**: Maintenir mauvais routages <5% (actuellement 3.6%).

### 3. Agents fantômes: Clarifier ou supprimer

**Problème**: `content-developer` (0%) et `project-framer` (<1%) jamais utilisés.

**Actions**:
- **Option A**: Supprimer agents inutilisés
- **Option B**: Clarifier use cases + communiquer à utilisateur
- **Option C**: Analyser pourquoi pas de tâches correspondantes

### 4. Documenter patterns réussis

**À préserver**:
- `developer ↔ git-workflow-manager` (séparation dev/git)
- Architecture → solution-architect
- Refactoring → refactoring-specialist (amélioration P3→P4)

**À valider**:
- Quality chain P4: Efficace ou overhead?
- Pattern conception→planification (P2): Perdu, à restaurer?

### 5. Investiguer backlog-manager overhead

**Question**: 14.7% usage + self-loop 22 — est-ce normal?

**Action**: Analyser ce que fait backlog-manager dans ces self-loops.

---

## Métriques de Succès

| Métrique | P4 Actuel | Cible |
|----------|-----------|-------|
| Adoption junior-developer | 1.3% | >5% |
| Mauvais routages | 3.6% | <5% (maintenir) |
| Self-loops | 29.2% | <20% |
| Usage content-developer | 0% | >2% OU supprimer |
| Usage project-framer | 0.7% | >3% OU supprimer |

---

## Patterns de Transitions (Nouveauté P4)

**Évolution des self-loops** (agents qui se rappellent eux-mêmes):
- P2: 58% (dominé par project-framer, backlog-manager)
- P3: 35.6% (dominé par developer explosion: 191)
- P4: 29.2% (senior-developer: 38, backlog-manager: 22)

**Tendance positive**: Réduction continue → meilleure collaboration inter-agents.

**Pattern émergent P4**: Quality chain
- `architecture-reviewer → performance-optimizer → refactoring-specialist`
- 8+6+5 = 19 transitions
- **À valider**: Efficace ou trop complexe?

---

## Limites Méthodologiques

**Détection automatique de mauvais routage**:
- Basée sur mots-clés dans prompts/descriptions
- **Faux négatifs possibles**: Mauvais routages sans mots-clés évidents
- **Faux positifs possibles**: Certains cas flaggés peuvent être légitimes

**Context partiel**:
- Analyse basée sur prompt/description, sans historique complet de session
- Bon routage ≠ succès garanti (dépend de l'exécution de l'agent)

---

## Conclusion

**Le système de routage fonctionne globalement bien** et s'améliore (P3→P4: -73% mauvais routages).

**Les 3 blocages "hands-off" identifiés sont actionnables**:
1. junior-developer: Problème de description/documentation
2. Biais généraliste: Problème de guidance du general agent
3. Agents fantômes: Décision de design (garder ou supprimer?)

**L'amélioration la plus impactante**: Clarifier junior-developer pour décharger senior-developer.

---

**Pour plus de détails**: Voir [routage-patterns-analysis.md](./routage-patterns-analysis.md) (656 lignes, exemples concrets, analyse période par période).