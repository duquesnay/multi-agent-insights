# Assumptions Checklist - Phase 0

**Analysis Version**: v8.0
**Date**: 2025-09-30
**Analyst**: Claude Code (Sonnet 4.5)

---

## Critical Assumptions to Validate

### 1. System Timeline

- [x] When was multi-agent system launched? **4 août 2025** (commit 795b476e)
- [x] What agents existed during analysis period? **8 agents initial**, puis ajouts progressifs
- [x] Were there major configuration changes? **OUI - 7 modifications septembre**
- [x] Baseline period identified? **Mai-Juillet 2025** (pré-agents)

**Git command executed**:
```bash
cd ~/.claude-memories
git log --all --format="%ai | %s" --since="2025-05-01" --until="2025-09-30" \
  | grep -E "(agent|Agent)"
```

**Validation**:
- [x] Timeline verified with git
- [ ] User confirmed timeline accuracy (PENDING)

**Notes**:
```
Timeline découverte (git archaeology):

4 août 2025 (795b476e): Launch multi-agent system (8 agents)
- developer, backlog-manager, git-workflow, documentation-writer, etc.

3 sept (d776ce28, 4b5f58f5): +solution-architect, +project-framer
11 sept (6449c2c7): eXtreme Estimates methodology integration
12 sept (059fcd8f): MANDATORY agent delegation policy
12 sept (d32c8b73): Enhanced agent descriptions
15 sept (1d7bb35c): +content-developer
20 sept (6c65b3f4): +refactoring-specialist
21 sept 16h24 (51622746): RESTRUCTURE - senior-developer + junior-developer split
21 sept (9e40e5d8, 6915b7b6): Scope-aware protocols, over-engineering prevention
22 sept (10955a90): Safeguards integration-specialist
22 sept (a6c42141): +parallel-worktrees framework
30 sept (ff95e8e2): Modernize architecture for Sonnet 4.5

CONTEXTE UTILISATEUR:
- 4-23 août: Vacances → faible utilisation post-launch
- 24 août: Reprise utilisation (139 messages août total)
- Septembre: Premier mois complet utilisation intensive
```

---

### 2. Data Availability

- [x] What snapshots/data available for period? **Live JSONL + Historical extractions**
- [x] Volumes per period checked? **OUI - voir tableau**
- [x] Missing data identified? **Août faible volume (vacances) - PAS un gap**
- [x] Data quality validated? **JSONL complets, DB timestamps corrompus (ignorés)**

**Inventory executed**:
```bash
# Primary source
find ~/.claude/projects -name "*.jsonl" | wc -l  # 272 files
# Messages par mois (timestamps JSONL)
Août 2025: 139 messages
Septembre 2025: 97,025 messages
```

**Validation**:
- [x] Volumes make sense - septembre spike attendu (premier mois complet)
- [x] Août faible volume expliqué (vacances 4-23, normal)
- [x] Data sources validés (JSONL fiables, DB ignorée)

**Notes**:
```
Period              | Source            | Volume        | Notes
--------------------|-------------------|---------------|---------------------------
Mai 2025            | historical/       | 10 sess, 17 d | Baseline
Juin 2025           | historical/       | 31 sess, 72 d | Baseline
Juillet 2025        | historical/       | 16 sess, 24 d | Baseline
Août 2025 (4-23)    | JSONL             | ~139 msgs     | Vacances user - faible volume NORMAL
Août 2025 (24-31)   | JSONL             | (inclus)      | Reprise utilisation
Septembre 2025      | JSONL             | 97,025 msgs   | Premier mois complet (~140-150 sessions)

DATA QUALITY:
✓ JSONL files: Complete, chronological, 272 files
✗ __store.db: Timestamps corrupted (1970) - IGNORED
✓ agent_calls_metadata.csv: 1,247 records (septembre)
✓ Historical extractions: Pre-validated (v7.1)
```

---

### 3. External Context

- [ ] Active development projects during period? **À identifier (git repos)**
- [x] Major features/migrations ongoing? **Système lui-même en évolution**
- [x] User learning curve factors? **Vacances août = pause apprentissage**
- [x] System changes outside agent configs? **7 modifications config septembre**

**Git repos check** (À FAIRE avec user):
```bash
find ~/dev -name ".git" -type d 2>/dev/null | while read gitdir; do
    repo=$(dirname "$gitdir")
    cd "$repo"
    commits=$(git log --all --since="2025-05-01" --until="2025-09-30" \
      --oneline 2>/dev/null | wc -l)
    if [ "$commits" -gt 10 ]; then
        echo "$repo: $commits commits"
    fi
done
```

**Validation**:
- [ ] Active repos à identifier avec user (PENDING)
- [x] Development context compris: Système multi-agents en évolution
- [ ] User confirmation facteurs externes (PENDING)

**Notes**:
```
CONTEXTE CONNU:
- 4-23 août: Vacances user → pause développement + apprentissage système
- Septembre: Évolution rapide système (7 modifications config)
- Septembre: Premier mois complet utilisation intensive

QUESTIONS POUR USER:
1. Projets actifs mai-septembre? (MCP, applications clientes, autres?)
2. Migrations techniques majeures en cours?
3. Complexité/nature tâches comparable entre périodes?
4. Autres facteurs externes impactant utilisation?
```

---

### 4. Baseline & Comparisons

- [x] What period serves as baseline? **Mai-Juillet 2025 (pré-agents)**
- [x] Baseline configuration documented? **OUI - mono-agent, no specialization**
- [x] Comparison periods valid? **NON - septembre a 4 configs différentes**
- [x] Cross-period comparisons make sense? **Segmentation requise**

**Validation**:
- [x] Baseline = pré-4 août (before multi-agent launch)
- [x] Comparisons must segment by config changes (git-based)
- [x] Segmentation respects system evolution (7 modifications sept)

**Notes**:
```
Baseline: P0 (Mai-Juillet) - Mono-agent, no specialization
  Volume: 57 sessions, 113 délégations
  Config: Ère pré-agents spécialisés

Comparison periods (git-based segmentation):
  P1: Août (4-31) - 8 agents initial, vacances
  P2: Sept 1-11 - +solution-architect, +project-framer
  P3: Sept 12-20 - Mandatory delegation + specialists
  P4: Sept 21-30 - senior/junior split + safeguards

⚠️ CROSS-PERIOD COMPARISONS COMPLEXES:
- Configurations différentes → comparaisons directes invalides
- Vacances août → biais apprentissage vs septembre
- Évolution rapide sept → 4 sous-périodes nécessaires
- Méthodologie: Comparer évolution (P3→P4), pas absolu (P0 vs P4)
```

---

### 5. Key Metrics Definitions

- [x] What constitutes "failure"? **Taxonomy required (pas juste boolean)**
- [x] What constitutes "marathon"? **>20 délégations + classification**
- [x] Success rate calculation clear? **OUI - mais contexte par période**
- [x] Other metrics well-defined? **Tokens ROI à ajouter**

**Validation**:
- [x] Metrics definitions explicit (from v7.1 learnings)
- [x] Classification frameworks defined (apply BEFORE aggregation)
- [x] Edge cases documented

**Notes**:
```
Marathon definition (from methodology):
  Threshold: >20 delegations in session
  Classification: success_rate + cascade_rate
    - POSITIVE: success_rate ≥85% (productive work)
    - NEGATIVE: success_rate <80% (pathological)
    - AMBIGUOUS: 80-85% (needs review)

Failure taxonomy (not just count):
  - USER_TOOL_INTERVENTION: Ambiguous (intentional or stuck?)
  - AGENT_NOT_FOUND: Config issue
  - TIMEOUT: Resource/complexity
  - EXECUTION_ERROR: Code/environment issue
  - CASCADE_LOOP: Coordination failure

Tokens metrics (Phase 1 extraction):
  - input_tokens, output_tokens par délégation
  - Agrégations: par agent type, par type tâche
  - ROI: tokens vs output quality (git validation)

Success rate:
  - Par session: successes / total delegations
  - Contexte période (config influence expected)
```

---

## User Sync (15min)

**Date sync**: 2025-09-30 (MAINTENANT)
**Attendees**: Guillaume (utilisateur) + Claude Code

### Questions for User:

1. **Timeline agents launch correct?**
   - Git dit: 4 août 2025 launch multi-agents
   - Modifications septembre (7 commits)
   - ✓ Confirmed correct?

2. **Août "faible volume" - contexte validé?**
   - 139 messages août vs 97,025 septembre
   - Vacances 4-23 août expliquent le volume
   - ✓ Acceptable pour analyse?

3. **External context factors?**
   - Projets actifs mai-septembre? (Repos à identifier)
   - Migrations techniques majeures?
   - Complexité tâches comparable entre périodes?

4. **Baseline period makes sense?**
   - Mai-Juillet = baseline pré-agents
   - Août = transition (vacances)
   - Septembre = focus principal
   - ✓ Segmentation pertinente?

5. **Metrics definitions aligned with intent?**
   - Marathon >20 délégations + classification positive/negative/ambiguous
   - Failure taxonomy (pas juste count)
   - Tokens ROI à mesurer
   - ✓ Mesures attendues?

6. **Objectif analyse - clarification**
   - "Ce qui bloque hands-off" = ?
   - Focus septembre, mais baseline mai-septembre pour contexte
   - ✓ Intent correct?

### User Corrections:
```
Q1. Timeline correcte? → OUI (4 août launch validé, 7 modifs sept validées)
Q2. Août faible volume OK? → OUI (vacances contexte accepté)
Q3. Projets actifs mai-sept:
    - Mai-Août: obsidian-mcp, omnifocus-mcp (projets MCP dominants)
    - Septembre: nagturo (projet principal, nouveau contexte)
Q4. Baseline pertinente? → OK (mai-juillet pré-agents validé)
Q5. Metrics attendues → User demande recommandations
Q6. "Hands-off" défini:
    - Coder SANS intervention user (sauf feedbacks/avis explicitement demandés)
    - Tourner en autonomie et FINIR la tâche
    - Sans nécessité de corriger des choses qui auraient pu/dû être déjà sues

    Traduction metrics:
    - Interventions user non-demandées = blocage
    - Sessions incomplètes (pas fini tâche) = blocage
    - Erreurs répétées (context déjà connu) = blocage
```

### Revised Assumptions:
```
AJOUTS POST-SYNC:

External Context - PRÉCISÉ:
- Mai-Août: Développement MCP servers (obsidian-mcp, omnifocus-mcp)
  → Tâches: Architecture MCP, TypeScript, intégrations API
- Septembre: Nouveau projet nagturo (contexte différent)
  → Potentiel: Changement nature tâches = biais comparaison

"Hands-off" - DÉFINI CLAIREMENT:
3 types de blocages à mesurer:
1. USER_INTERVENTION_UNASKED: User doit intervenir sans avoir été sollicité
2. INCOMPLETE_TASK: Session ne finit pas la tâche demandée
3. REPEATED_ERROR: Erreurs sur context déjà connu (mémoire système)

Implications métriques:
- Mesurer taux "finition tâche" (task completion rate)
- Classifier interventions user (demandées vs forcées)
- Tracker erreurs context (même erreur >1 fois = problème)
```

---

## Validation Status

- [x] Critical assumptions documented (git archaeology done)
- [x] Data inventory complete (JSONL source validated)
- [x] Timeline git-validated (4 août launch + 7 modifs sept)
- [x] User confirmation timeline/context (✅ VALIDATED)
- [x] External context clarified (obsidian/omnifocus-mcp puis nagturo)
- [x] Baseline period user-approved (mai-juillet OK)
- [x] Metrics definitions aligned (✅ APPROVED 2025-09-30)
- [x] Objectif analysis confirmed ("hands-off" = autonomie + finition)

**Ready to proceed to Phase 1 (Extraction)**: ☑ YES

---

## Proposed Metrics (Q5 Answer)

Basé sur définition "hands-off", je propose ces metrics:

### Metrics Principales (Blocages Hands-Off)

1. **Task Completion Rate**
   - Sessions qui finissent la tâche demandée vs abandonnées
   - Indicateur: Taux <80% = problème autonomie

2. **User Intervention Classification**
   - ASKED: User sollicité (feedback, avis) = normal
   - UNASKED: User force intervention = **blocage**
   - Indicateur: Ratio unasked/total interventions

3. **Context Memory Failures**
   - Erreurs répétées sur même context/pattern
   - Indicateur: >1 occurrence même erreur = système n'apprend pas

4. **Marathon Quality Distribution**
   - POSITIVE: ≥85% success, productive
   - NEGATIVE: <80% success, stuck = **blocage**
   - Indicateur: Ratio negative/total marathons

### Metrics Secondaires (Efficience)

5. **Agent Routing Accuracy**
   - Bon agent dès premier coup vs cascades inutiles
   - Indicateur: Taux routing direct vs détours

6. **Tokens ROI**
   - Tokens investis vs output quality (git validation)
   - Indicateur: ROI par type agent, par période

7. **Session Duration vs Complexity**
   - Temps/délégations pour tâche simple vs complexe
   - Indicateur: Over-engineering detection

**Validation Needed**: Ces metrics répondent à ton besoin?

---

**Completed by**: Claude Code (Sonnet 4.5)
**Date**: 2025-09-30
**Approved by user**: ☑ Timeline/Context  ☑ Metrics  ☑ PHASE 0 COMPLETE