# Exemples Concrets de Routage: Bons et Mauvais

**Source**: Analyse septembre 2025, données enrichies des 154 sessions
**But**: Guide pratique avec exemples réels pour améliorer le routage

---

## ✓ BONS ROUTAGES - Patterns à Préserver

### 1. Git Operations → git-workflow-manager

**Pattern le plus clair** (153 exemples en P3)

#### Exemple 1: Tagging et push
```
Tâche: Complete git tagging and push
Agent choisi: git-workflow-manager ✓

Prompt: "I need to complete the hotfix deployment process:
1. We just made a commit aa4eb49 with message 'fix(auth): remove 
   password hashing duplication in seeding'..."

Pourquoi c'est bon: Version control operations → git specialist
```

#### Exemple 2: Create release
```
Tâche: Create major version tag and release
Agent choisi: git-workflow-manager ✓

Prompt: "Create version tags for this major milestone in the 
Espace Naturo project. We just completed a major deployment..."

Pourquoi c'est bon: Git workflow → git specialist
```

**Trigger words efficaces**: git, commit, branch, merge, push, tag, release, PR

---

### 2. Architecture/Design → solution-architect

**Pattern fort et consistant** (55 exemples en P3)

#### Exemple 1: Design system
```
Tâche: Analyze URL detection at startup
Agent choisi: solution-architect ✓

Prompt: "The user wants to show the complete URL in the server 
startup message instead of just 'serving on port 5000'. There's 
an existing `getBaseUrlFromRequest` helper..."

Pourquoi c'est bon: Design decision → architecture specialist
```

#### Exemple 2: Structure analysis
```
Tâche: Analyze project structure for deployment
Agent choisi: solution-architect ✓

Prompt: "I need you to analyze the current project structure for 
'espace_naturo' to understand:
1. What type of application this is (frontend, backend, full-stack)
2. Current deployment architecture..."

Pourquoi c'est bon: System architecture → architect
```

**Trigger words efficaces**: architecture, design, structure, approach, strategy, analyze system

---

### 3. Refactoring → refactoring-specialist

**Amélioration P3→P4** (1.3% → 10.7%)

#### Exemple 1: Remove deprecated code
```
Tâche: Remove deprecated IStorageValidator
Agent choisi: refactoring-specialist ✓

Prompt: "I need you to fix a critical seeding bug in the worktree 
`/Users/guillaume/dev/client/espace_naturo_seeding_fix` on branch 
`fix/seeding-postgres-schema...`"

Pourquoi c'est bon: Code cleanup → refactoring specialist
```

#### Exemple 2: DRY violations
```
Tâche: Refactor SESSION DRY violations
Agent choisi: refactoring-specialist ✓

Prompt: "Tu travailles dans le worktree `espace_naturo-session` 
sur la branche `fix/session-404`. Le code-quality-analyst a 
identifié des DRY violations..."

Pourquoi c'est bon: Quality improvement → refactoring
```

**Trigger words efficaces**: refactor, restructure, clean up, DRY, code quality

---

### 4. Task Management → backlog-manager

**Consistant dans toutes périodes** (top 3 toujours)

#### Exemple 1: Add to backlog
```
Tâche: Add upload failure to backlog
Agent choisi: backlog-manager ✓

Prompt: "I need to add a critical production bug to the backlog:
**Bug Report:**
- **Title**: Production Upload Failure - 500 Access Denied..."

Pourquoi c'est bon: Planning/tracking → backlog manager
```

#### Exemple 2: Update status
```
Tâche: Update backlog with current status
Agent choisi: backlog-manager ✓

Prompt: "The user has requested an update to the backlog. Based 
on the recent work completed, CONS1.8 document editing 
functionality has been investigated..."

Pourquoi c'est bon: Task coordination → backlog
```

**Trigger words efficaces**: backlog, task, plan, track, organize, todo, status

---

### 5. Performance → performance-optimizer

**Specialist bien utilisé** (9 exemples en P4)

#### Exemple
```
Tâche: Analyze test performance patterns
Agent choisi: performance-optimizer ✓

Prompt: "Analyze the performance characteristics of the 
document-editing.test.ts integration test to identify 
potential optimizations..."

Pourquoi c'est bon: Performance analysis → optimizer
```

**Trigger words efficaces**: performance, optimize, slow, speed, bottleneck

---

## ✗ MAUVAIS ROUTAGES - Erreurs à Éviter

### 1. Refactoring → developer (au lieu de refactoring-specialist)

**Pattern d'erreur commun** (P2, P3, P4)

#### Exemple 1: Quality improvements
```
Tâche: Continue quality improvements
Agent choisi: developer ✗
Devrait être: refactoring-specialist

Prompt: "Continue the code quality improvement work that was 
started. The critical route duplication in server/routes.ts 
has been partially addressed..."

Pourquoi c'est mauvais: Refactoring specialist existe depuis P3
```

#### Exemple 2: Restructure database
```
Tâche: Refactor db.ts for lazy initialization
Agent choisi: developer ✗
Devrait être: solution-architect (design) ou refactoring-specialist

Prompt: "The user wants to refactor server/db.ts to use lazy 
initialization instead of connecting to the database at 
import time..."

Pourquoi c'est mauvais: Design decision + refactoring
```

---

### 2. Simple Tasks → senior-developer (au lieu de junior-developer)

**Pattern P4 uniquement** (junior-developer introduit 21 sept)

#### Exemple 1: Simple fix
```
Tâche: Implement SEEDING fixes
Agent choisi: senior-developer ✗
Devrait être: junior-developer

Prompt: "Tu travailles sur le projet Espace Naturo dans le 
worktree `espace_naturo-seeding` sur la branche 
`fix/seeding-postgres-schema`..."

Pourquoi c'est mauvais: Tâche simple, pas de complexité 
architecturale → junior peut gérer
```

#### Exemple 2: Basic implementation
```
Tâche: Implement SESSION fix
Agent choisi: senior-developer ✗
Devrait être: junior-developer

Prompt: "Tu travailles dans le worktree `espace_naturo-session` 
sur la branche `fix/session-404`..."

Pourquoi c'est mauvais: Fix straightforward → junior-developer
```

**Problème root cause**: Description junior-developer pas claire

---

### 3. Architecture Questions → developer (au lieu de solution-architect)

#### Exemple
```
Tâche: Query dev database for naturopath
Agent choisi: developer ✗
Devrait être: solution-architect

Prompt: "The user wants to find the naturopath user in the 
development database. Looking at the codebase, this appears 
to be an Espace Naturo project with PostgreSQL..."

Pourquoi c'est mauvais: Architecture understanding nécessaire
```

---

### 4. Content Creation → developer (au lieu de content-developer)

**Note**: content-developer existe mais **0 calls** en P3 et P4

#### Pattern (hypothétique, content-developer jamais utilisé)
```
Tâche: Write guide or tutorial
Agent choisi: developer ✗
Devrait être: content-developer

Prompt: "Write a comprehensive guide for..."

Pourquoi c'est mauvais: Content creation, pas code
```

**Problème root cause**: Description content-developer ambiguë OU 
pas de tâches de contenu pur pendant septembre

---

## 🔄 TRANSITIONS - Patterns de Collaboration

### Pattern Réussi: developer ↔ git-workflow-manager

**P3**: 90 transitions bidirectionnelles (47 + 43)

```
Séquence typique:
1. developer: Implement feature
2. git-workflow-manager: Create commit, tag, push
3. developer: Continue with next feature
OU
1. git-workflow-manager: Create branch
2. developer: Implement on branch
3. git-workflow-manager: Merge, create PR
```

**Pourquoi c'est bon**: Séparation claire dev/version control

---

### Pattern Émergent P4: Quality Chain

**Nouveau en P4** (19 transitions)

```
Séquence typique:
1. architecture-reviewer: Analyze code structure
2. performance-optimizer: Identify bottlenecks
3. refactoring-specialist: Apply improvements
4. senior-developer: Implement changes

Exemple:
- architecture-reviewer: "Critical DRY violations detected"
- performance-optimizer: "Tests are slow due to X"
- refactoring-specialist: "Restructure to fix both"
- senior-developer: "Implement restructuring"
```

**Question ouverte**: Ce pattern est-il efficace ou overhead?

---

### Anti-Pattern: Self-Loops Excessifs

**developer → developer**: 191 en P3 (problème)

```
Pattern problématique:
1. developer: Start task
2. developer: Subtask 1
3. developer: Subtask 2
... (continues)
50. developer: Finally done

Pourquoi c'est problématique: Agent ne délègue pas aux 
spécialistes disponibles
```

**Amélioration P4**: senior-developer self-loop réduit à 38

---

## 📋 GUIDE RAPIDE: Quand Utiliser Quel Agent?

| Type de Tâche | Agent Correct | Trigger Words |
|---------------|---------------|---------------|
| **Git operations** | git-workflow-manager | git, commit, branch, merge, tag, push, PR |
| **Architecture/design** | solution-architect | architecture, design, structure, system, approach |
| **Refactoring** | refactoring-specialist | refactor, restructure, DRY, code quality, clean up |
| **Performance** | performance-optimizer | slow, performance, optimize, bottleneck, speed |
| **Code review** | code-quality-analyst | review, analyze, audit, quality check |
| **Planning** | backlog-manager | backlog, task, plan, organize, track, status |
| **Project setup** | project-framer | project structure, framing, organization |
| **Simple tasks** | junior-developer | simple, basic, straightforward, quick fix |
| **Complex features** | senior-developer | complex, architecture, new pattern, critical |
| **Documentation/content** | content-developer | write guide, tutorial, documentation (non-code) |

---

## 🎯 Actions pour Améliorer le Routage

### Pour le General Agent

1. **Ajouter Task Complexity Assessment**:
   ```
   Before routing, assess:
   - Complexity: Simple/Medium/Complex?
   - Domain: Architecture/Implementation/Git/Planning?
   - If simple → junior-developer
   - If complex → senior-developer
   - If specialized domain → specialist
   ```

2. **Préférence spécialistes**:
   ```
   When in doubt:
   - Check if specialist exists for this domain
   - Route to specialist rather than generalist
   - Only use generalist if no specialist matches
   ```

### Pour les Descriptions d'Agents

1. **junior-developer**: Ajouter exemples concrets
   ```
   Handles: fix typos, simple refactoring following existing 
   patterns, basic implementations, straightforward bug fixes
   
   Does NOT handle: complex architecture, new patterns, 
   critical production bugs
   ```

2. **content-developer**: Clarifier use case
   ```
   Handles: Writing guides, tutorials, documentation (non-code), 
   content creation, technical writing
   
   Does NOT handle: Code documentation (comments), API docs
   ```

3. **Tous agents**: Ajouter trigger words list dans description

---

**Date**: 2025-09-30
**Source**: Analyse de 1315 délégations (sept 2025)
**Taux de mauvais routage P4**: 3.6% (11/307)
**Objectif**: <5%
