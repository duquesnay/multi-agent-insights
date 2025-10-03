# Livrable: Analyse des Patterns de Routage Agent→Sous-Agent

**Date**: 2025-09-30
**Agent**: Routage Investigator
**Données sources**: 154 sessions, 1315 délégations (sept 2025)

---

## 📦 Livrables Produits

### Documents Markdown (4 fichiers)

1. **[README-ROUTAGE.md](./README-ROUTAGE.md)** (6.4 KB)
   - Point d'entrée pour toute l'analyse
   - Vue d'ensemble des documents disponibles
   - Métriques clés et évolution temporelle

2. **[ROUTAGE-EXECUTIVE-SUMMARY.md](./ROUTAGE-EXECUTIVE-SUMMARY.md)** (6.4 KB)
   - **Lecture recommandée en premier** (5 min)
   - Réponse courte à "Le general agent choisit-il le bon sous-agent?"
   - Actions prioritaires avec métriques
   - Conclusion actionnable

3. **[routage-patterns-analysis.md](./routage-patterns-analysis.md)** (24 KB, 656 lignes)
   - **Rapport complet d'analyse** (30-45 min)
   - Analyse période par période (P2, P3, P4)
   - Bons et mauvais routages avec exemples concrets
   - Synthèse cross-période et insights actionnables
   - Annexe: Patterns de transitions agent→agent

4. **[ROUTAGE-EXAMPLES.md](./ROUTAGE-EXAMPLES.md)** (11 KB)
   - **Guide pratique** (15-20 min)
   - Exemples réels de bons et mauvais routages
   - Patterns de collaboration (transitions)
   - Guide rapide: tableau de référence
   - Actions concrètes pour améliorer

### Données JSON (3 fichiers)

5. **data/routing_patterns_by_period.json** (2.1 MB)
   - Patterns de routage par période (P2, P3, P4)
   - Toutes les délégations avec contexte complet
   - Transitions agent→agent
   - Échantillons de tâches par agent

6. **data/routing_quality_analysis.json** (21 KB)
   - Mauvais routages identifiés (heuristique)
   - Catégorisation par type d'erreur
   - Exemples concrets avec prompts
   - Agents sous-utilisés par période
   - Breakdown explosion developer (P3)

7. **data/good_routing_patterns.json** (45 KB)
   - Bons routages identifiés
   - Patterns de succès par agent
   - Exemples avec contexte
   - Volume par pattern

### Scripts Python (4 fichiers)

8. **extract_routing_patterns.py** (6.3 KB)
   - Extraction patterns de routage depuis données enrichies
   - Segmentation temporelle (P2, P3, P4)
   - Comptage agents et transitions

9. **analyze_routing_quality.py** (10 KB)
   - Détection heuristique de mauvais routages
   - Analyse explosion developer (P3)
   - Identification agents sous-utilisés

10. **analyze_good_routing.py** (7.1 KB)
    - Identification patterns de bon routage
    - Groupement par type de pattern
    - Extraction exemples concrets

11. **generate_routing_report.py** (16 KB)
    - Génération rapport markdown complet
    - Synthèse cross-période
    - Insights actionnables

---

## 🎯 Réponse à la Question Centrale

### Question
**"Le general agent choisit-il le bon sous-agent?"**

### Réponse
**Oui majoritairement (96.4% en P4), avec amélioration significative post-restructuration (P3→P4: -73% mauvais routages).**

**MAIS 3 blocages persistent:**

1. **junior-developer pas adopté** (1.3% usage vs cible >5%)
2. **Biais vers généraliste** quand hésitation (senior-developer 22.8%)
3. **Agents fantômes** jamais utilisés (content-developer: 0%, project-framer: <1%)

---

## 🔍 Découvertes Majeures

### ✓ Succès (à préserver)

**1. Pattern Git → git-workflow-manager**
- 153 calls en P3 (17.9%)
- Pattern le plus clair et le plus fort
- Collaboration bidirectionnelle: `developer ↔ git-workflow-manager` (90 transitions)
- **Aucun mauvais routage détecté**

**2. Amélioration spectaculaire P3 → P4**
- Mauvais routages: 13.9% → 3.6% (**-73%**)
- `refactoring-specialist`: 1.3% → 10.7% (**+8x**)
- Self-loops: 35.6% → 29.2% (-18%)
- developer explosion (40.1%) → senior-developer (22.8%)

**3. Émergence Quality Chain (P4)**
- `architecture-reviewer → performance-optimizer → refactoring-specialist → senior-developer`
- 19 transitions identifiées
- Signe d'utilisation des safeguards scope creep

### ✗ Blocages (à adresser)

**1. junior-developer Sous-Utilisé**
- **4 calls seulement (1.3%)** depuis introduction (21 sept)
- Tâches simples vont vers senior-developer
- **Root cause**: Description peu claire, pas de trigger words
- **Impact**: Gaspillage ressources senior

**2. Explosion developer en P3**
- **344 calls (40.1%)** — pic historique
- Breakdown:
  - 77.9% testing (légitime — pas de spécialiste)
  - 13.1% implementation + 6.1% debugging (auraient dû aller vers spécialistes)
- **Root cause**: Routage par défaut vers généraliste quand hésitation

**3. Agents Fantômes**
- `content-developer`: **0 calls** en P3 ET P4
- `project-framer`: <1% en P3-P4 (utilisé seulement en P2 pour setup)
- **Impact**: Complexité inutile si jamais utilisés

### ≈ Ambiguïté

**backlog-manager Overhead?**
- Toujours dans le **top 3** (P2: 25.8%, P3: 10.0%, P4: 14.7%)
- Self-loop élevé: 22-26 dans toutes périodes
- **Question**: Légitime (décomposition planning) ou overhead?

---

## 📊 Métriques Clés par Période

| Métrique | P2 (3-11 sept) | P3 (12-20 sept) | P4 (21-30 sept) | Évolution |
|----------|----------------|-----------------|-----------------|-----------|
| **Volume délégations** | 151 | 857 | 307 | -64% P3→P4 |
| **Mauvais routages** | 10 (6.6%) | 119 (13.9%) | 11 (3.6%) | **-73%** ✓ |
| **Top agent** | backlog-manager (25.8%) | developer (40.1%) | senior-developer (22.8%) | Normalisé |
| **Self-loops** | 58% | 35.6% | 29.2% | **-47%** ✓ |
| **refactoring-specialist** | N/A | 11 (1.3%) | 33 (10.7%) | **+8x** ✓ |
| **junior-developer** | N/A | N/A | 4 (1.3%) | ✗ Pas adopté |

---

## 🚀 Actions Prioritaires (Ordre d'Impact)

### 1. URGENT: Clarifier junior-developer

**Problème**: 4 calls (1.3%) vs cible >5%
**Impact**: Tâches simples → senior-developer (gaspillage)

**Actions concrètes**:
```
Dans description junior-developer, ajouter:

HANDLES:
- Fix typos, basic syntax errors
- Simple refactoring following existing patterns
- Basic implementations with clear guidance
- Straightforward bug fixes
- Quick fixes, simple updates

DOES NOT HANDLE:
- Complex architecture decisions
- New design patterns
- Critical production bugs
- Performance optimization
- System design questions

TRIGGER WORDS: simple, basic, straightforward, quick fix, trivial
```

**Dans general agent, ajouter**:
```
Before routing to senior-developer, ask:
- Is this task simple and straightforward?
- Does it follow existing patterns?
- No architectural decisions needed?
→ YES? Route to junior-developer
→ NO? Route to senior-developer
```

**Métrique de succès**: 1.3% → >5% dans les 2 prochaines semaines

---

### 2. Réduire Biais Généraliste

**Problème**: Hésitation → routage vers developer/senior-developer

**Actions**:
1. **Améliorer descriptions agents**:
   - Ajouter section "HANDLES" / "DOES NOT HANDLE"
   - Lister trigger words explicites
   - Donner 3-5 exemples concrets par agent

2. **Créer guide de routage pour general agent**:
   ```
   ROUTING DECISION TREE:
   1. Identify task domain (git/architecture/refactoring/etc.)
   2. Check if specialist exists for this domain
   3. Assess complexity (simple/medium/complex)
   4. Route to specialist if available
   5. Only use generalist if no specialist matches
   ```

3. **Ajouter Task Complexity Assessment** dans general agent:
   ```
   Assess before routing:
   - Domain: What specialty?
   - Complexity: Simple/Medium/Complex?
   - Criticality: Low/Medium/High?
   ```

**Métrique de succès**: Maintenir mauvais routages <5% (actuellement 3.6%)

---

### 3. Décision Agents Fantômes

**Problème**: content-developer (0%), project-framer (<1%) jamais utilisés

**Options**:
- **Option A - Supprimer**: Si pas utilisés après 2 mois → retirer du système
- **Option B - Clarifier**: Définir use cases précis + communiquer à utilisateur
- **Option C - Analyser**: Comprendre pourquoi pas de tâches correspondantes

**Recommandation**: **Option B pour content-developer, Option A pour project-framer**
- `content-developer`: Clarifier (documentation/guides ≠ code comments)
- `project-framer`: Supprimer (utilisé seulement setup initial P2)

**Métrique de succès**:
- content-developer: >2% usage OU suppression
- project-framer: Suppression documentée

---

### 4. Valider Quality Chain (P4)

**Observation**: Nouveau pattern émergent
`architecture-reviewer → performance-optimizer → refactoring-specialist → senior-developer`

**Question**: Efficace ou overhead?

**Actions**:
1. Mesurer impact qualité code des tâches passant par cette chaîne
2. Comparer avec tâches directes (sans chaîne)
3. Analyser durée totale vs qualité finale

**Métrique de succès**: Décision data-driven (garder/simplifier/supprimer)

---

### 5. Investiguer backlog-manager

**Observation**: Toujours top 3, self-loop élevé (22)

**Actions**:
1. Analyser 20 exemples de `backlog-manager → backlog-manager`
2. Identifier si décomposition légitime ou mauvaise délégation
3. Mesurer value ajoutée vs overhead

**Métrique de succès**: Clarification légitime vs overhead

---

## 📈 Patterns de Collaboration Identifiés

### Pattern Réussi: developer ↔ git-workflow-manager
- **P3**: 90 transitions bidirectionnelles (47 + 43)
- **Séparation claire**: Développement / Version control
- **À préserver**: Pattern le plus fort

### Pattern Émergent: Quality Chain (P4)
- `architecture-reviewer → performance-optimizer → refactoring-specialist`
- **Nouveau post-restructuration**
- **À valider**: Efficacité vs overhead

### Pattern Perdu: Conception → Planification (P2)
- `solution-architect → project-framer → backlog-manager`
- **Disparu en P3-P4**
- **À investiguer**: Pourquoi perdu? À restaurer?

### Anti-Pattern: Self-Loops Excessifs
- **P3**: developer → developer (191 fois)
- **Problème**: Agent ne délègue pas
- **Amélioration P4**: Réduit à 38 (senior-developer)

---

## 🎓 Insights Méthodologiques

### Découverte Critique
Le système a **évolué pendant l'observation** (7 modifications majeures en sept).
→ Nécessité de **segmentation temporelle stricte** (P2, P3, P4)

### Détection de Mauvais Routage
**Heuristique**: Mots-clés prompt/description vs agent choisi

**Limites**:
- Faux négatifs: Mauvais routages sans keywords évidents
- Faux positifs: Certains flaggés peuvent être légitimes
- Context partiel: Pas d'historique session complet

### Volume Analysé
- **154 sessions** (3-30 sept 2025)
- **1315 délégations** (P2: 151, P3: 857, P4: 307)
- **140 mauvais routages identifiés** (10.6% total)

---

## 📚 Comment Utiliser Ces Livrables?

### Pour Décideurs (5-10 min)
1. Lire [ROUTAGE-EXECUTIVE-SUMMARY.md](./ROUTAGE-EXECUTIVE-SUMMARY.md)
2. Consulter section "Actions Prioritaires" ci-dessus
3. Décider quelles actions implémenter

### Pour Amélioration Système (30-45 min)
1. Lire [routage-patterns-analysis.md](./routage-patterns-analysis.md) complet
2. Étudier [ROUTAGE-EXAMPLES.md](./ROUTAGE-EXAMPLES.md) pour patterns concrets
3. Implémenter actions prioritaires
4. Mesurer métriques de succès

### Pour Analyse Approfondie (2-3h)
1. Explorer fichiers JSON dans `data/`
2. Exécuter scripts Python pour analyses custom
3. Valider hypothèses avec données brutes

---

## ✅ Mission Accomplie

### Objectif Initial
**"Comprendre comment le general agent choisit les sous-agents et identifier les patterns de routage optimaux et sous-optimaux."**

### Livré
✓ Analyse complète avec segmentation temporelle
✓ Identification de 3 blocages actionnables
✓ 5 actions prioritaires avec métriques
✓ Patterns de succès documentés
✓ Exemples concrets (bons et mauvais)
✓ Guide pratique d'amélioration
✓ Données et scripts pour analyses futures

### Réponse Courte
**Le routage fonctionne bien (96.4% en P4) et s'améliore, mais 3 optimisations claires émergent: clarifier junior-developer, réduire biais généraliste, décider du sort des agents fantômes.**

---

**Analyse terminée**: 2025-09-30
**Agent**: Routage Investigator
**Version**: 1.0
**Prochaine étape**: Implémenter actions prioritaires et mesurer impact