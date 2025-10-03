# TodoList Actions - Système Multi-Agents
**Date**: 2025-09-30
**Source**: Synthèse des 4 analyses agents (Routage, Autonomie, Coordination, Qualité)
**Statut**: Draft v1 (à valider/ajuster)

---

## 🔴 P0 - Bloquants Critiques (Immédiat)

### 1. Circuit-Breaker Anti-Marathon [BLOQUANT]
**Problème**: 90% des marathons = cascades auto-délégations sans arrêt
**Cause racine**: Pas de limite après échecs répétés
**Action**:
```
IF same_agent fails 3 consecutive times:
    STOP delegation cascade
    ESCALATE to user with:
        "Agent X failed 3x on task Y"
        "Recommend: reframe task or manual intervention"
```
**Validation**: Tester règle sur les 12 marathons historiques
**Métrique succès**: 0 marathons avec 3+ échecs consécutifs sans escalation

---

### 2. Limiter Auto-Délégations Senior-Developer [BLOQUANT]
**Problème**: `senior-developer → senior-developer` (10× en P4) crée monopole
**Cause racine**: Prompts ne limitent pas self-delegation
**Action**:
```
Prompt senior-developer:
"BEFORE self-delegating, check:
  - Can junior-developer handle? (routine <10min)
  - Need specialist? (domain expertise)
  RULE: Max 2 consecutive self-delegations, then MUST delegate out"
```
**Validation**: Mesurer ratio self-delegation avant/après
**Métrique succès**: Self-loops senior <5% (actuellement ~10%)

---

### 3. Git Diff Validation Over-Engineering [CRITIQUE]
**Problème**: Agent 4 détecte over-engineering +54% en P4, hypothèse safeguards réfutée
**Besoin**: Valider sur code réel (pas juste textes)
**Action**:
- Identifier projets git des 5 marathons extrêmes
- Analyser diff: LOC, complexité, refactorings
- Confirmer/infirmer signaux "over-engineering" textuels
**Validation**: Corrélation signaux textuels vs métriques git
**Métrique succès**: Taux corrélation >70% (signaux textuels = indicateurs fiables)

---

## 🟠 P1 - Importants (Sous 1 semaine)

### 4. Règles Explicites Délégation Junior [ADOPTION]
**Problème**: junior-developer utilisé 1.3% vs cible >5%
**Cause racine**: Prompts général-agent + senior-developer ne routent pas vers junior
**Action**:
```
Senior-developer MUST delegate to junior-developer if:
  - Unit tests writing/fixing
  - Documentation updates
  - Code formatting/linting
  - Simple refactoring (<20 lines)
  - Bug fixes in well-known patterns

General-agent routing guide:
  - Trigger words: "simple", "straightforward", "quick fix", "basic"
  - ALWAYS consider junior before senior
```
**Validation**: Tracker usage junior-developer sur 2 semaines
**Métrique succès**: Junior adoption >5% des délégations

---

### 5. Clarifier Description Junior-Developer [ADOPTION]
**Problème**: Description actuelle floue ("junior" connoté négatif?)
**Action**:
- Renommer? "lightweight-developer" ou "routine-developer"
- Ajouter exemples concrets de tâches appropriées
- Documenter explicitement quand NE PAS utiliser (complex architecture, new patterns)
**Validation**: A/B test adoption avant/après clarification
**Métrique succès**: +3% adoption vs baseline

---

### 6. Investiguer Safeguards Inefficaces [QUALITÉ]
**Problème**: P4 = pire over-engineering (+54%) malgré safeguards scope creep
**Action**:
- Analyse qualitative 20 cas "scope creep" P4
- Identifier pourquoi safeguards contournés/inefficaces
- Patterns: "URGENT" bypass? Complexité mal estimée?
**Validation**: Patterns identifiés
**Métrique succès**: Propositions concrètes amélioration safeguards

---

### 7. Améliorer Mesure Échecs [MÉTRIQUE]
**Problème**: 97% échecs = `[interrupted by user]` (ambiguïté)
**Action**:
- Capturer timing interruption (rapide = timeout, long = supervision)
- Capturer contexte: dernière action agent avant interruption
- Capturer intention utilisateur (feedback post-interruption)
**Validation**: Classification échecs sur 50 cas tests
**Métrique succès**: Taxonomie claire avec <10% "ambigus"

---

## 🟡 P2 - Optimisations (Sous 2 semaines)

### 8. Décider Sort Agents Fantômes [MAINTENANCE]
**Problème**:
- content-developer: 0% usage en P4
- project-framer: <1% usage en P4
**Action**:
- content-developer: Supprimer OU définir use cases précis
- project-framer: Évaluer si "one-time use" (seulement P2)
**Validation**: Usage sur période test 2 semaines
**Métrique succès**: Usage >2% OU suppression validée

---

### 9. Tester Architecture-Reviewer AVANT Developer [QUALITÉ]
**Problème**: Pattern actuel = developer code → architecture-reviewer rejette → rework
**Hypothèse**: Reviewer AVANT pourrait réduire rework
**Action**:
- Expérimenter sur 10 tâches: architecture-reviewer → developer
- Mesurer rework ratio vs baseline
**Validation**: Rework réduit de >20%?
**Métrique succès**: Rework ratio <10% (actuellement 17.9% P4)

---

### 10. Analyser ROI Backlog-Manager [OVERHEAD?]
**Problème**: backlog-manager top 2-3 dans toutes périodes (overhead ou légitime?)
**Action**:
- Self-loops élevés (22-26): décomposition légitime ou problème?
- Comparer sessions avec/sans backlog-manager: efficacité différente?
**Validation**: Analyse 30 sessions représentatives
**Métrique succès**: Justification claire utilisation OU réduction usage

---

## 📊 Métriques de Suivi Globales

| Métrique | Baseline P4 | Cible Court-Terme | Cible Long-Terme |
|----------|-------------|-------------------|------------------|
| Marathons (>20 délég) | 5.6% sessions | <3% | 0% |
| Auto-délégations senior | ~10% | <5% | <2% |
| Junior-dev adoption | 1.3% | >5% | >10% |
| Over-engineering signals | 2.63/délég | <2.0 | <1.5 |
| Rework chains | 17.9% | <10% | <5% |
| Mauvais routages | 3.6% | <3% | <2% |
| Taux autonomie (hybride) | ~89% | >92% | >95% |

---

## 🔄 Processus de Validation

### Phase 1: Git Validation (Semaine 1)
- Valider hypothèses qualité Agent 4 avec code réel
- Confirmer/infirmer over-engineering P4
- Prioriser actions selon résultats

### Phase 2: Implémentation P0 (Semaine 1-2)
- Circuit-breaker (dev 1-2j)
- Limites auto-délégations (prompts 1j)
- Tester sur 20 sessions

### Phase 3: Implémentation P1 (Semaine 2-3)
- Règles junior-developer
- Amélioration mesure échecs
- Safeguards investigation

### Phase 4: Mesure Impact (Semaine 4)
- Comparer métriques avant/après
- Ajuster actions selon résultats
- Itération v2 todolist

---

## 📝 Notes Méthodologiques

**Sources**:
- Agent 1 (Routage): routage-patterns-analysis.md
- Agent 2 (Autonomie): failure-taxonomy-analysis.md
- Agent 3 (Coordination): coordination-marathons-analysis.md
- Agent 4 (Qualité): quality-assessment-analysis.md

**Limitations reconnues**:
- Pas encore validé avec git diff (P0-3 prioritaire)
- Timeline septembre uniquement (extension juin-sept en cours)
- Corrélation ≠ causalité

**Versioning**:
- v1.0: Synthèse initiale des 4 agents (30 sept)
- v2.0: Post-git validation (à venir)
- v3.0: Post-timeline étendue juin-sept (à venir)

---

## ✅ Statut Actions

- [ ] P0-1: Circuit-breaker
- [ ] P0-2: Limites auto-délégations
- [ ] P0-3: Git validation marathons
- [ ] P1-4: Règles junior-developer
- [ ] P1-5: Clarifier description junior
- [ ] P1-6: Investiguer safeguards
- [ ] P1-7: Améliorer mesure échecs
- [ ] P2-8: Agents fantômes
- [ ] P2-9: Architecture-reviewer AVANT
- [ ] P2-10: ROI backlog-manager