# Routing Patterns Analysis - Septembre 2025

**Objectif**: Comprendre comment le general agent choisit les sous-agents et identifier les patterns de routage optimaux et sous-optimaux.

**Méthodologie**: Analyse sémantique des prompts et descriptions de tâches avec segmentation temporelle stricte (P2, P3, P4).

---

## Période 2 (3-11 sept): Conception Added

**Configuration**: +solution-architect, +project-framer

**Volume**: 151 délégations

**Distribution agents**:
- backlog-manager: 39 (25.8%)
- project-framer: 38 (25.2%)
- solution-architect: 21 (13.9%)
- developer: 18 (11.9%)
- general-purpose: 16 (10.6%)

### ✓ Bons Routages

**81 exemples identifiés** de routage approprié.

#### Task management → backlog-manager

**Volume**: 39 délégations

**Exemples**:

1. **Tâche**: Add storage migration to backlog
   - **Prompt**: "Add the following strategic initiative to the backlog system:

**Initiative**: Migration du stockage objet vers Scaleway avec architecture injectable
..."
   - **Raison**: Task planning and tracking correctly routed to backlog manager

2. **Tâche**: Coordinate code quality improvements
   - **Prompt**: "I need you to coordinate the code quality improvement work based on the quality analysis results. The quality check identified critical issues that ne..."
   - **Raison**: Task planning and tracking correctly routed to backlog manager

#### Project setup → project-framer

**Volume**: 21 délégations

**Exemples**:

1. **Tâche**: Review project framing
   - **Prompt**: "Please analyze this NaturoSecure project and establish proper AAA Inception framing. This appears to be a secure document sharing platform for naturop..."
   - **Raison**: Project structure and organization correctly routed to framer

2. **Tâche**: Frame evolution toward Melanie's vision
   - **Prompt**: "Please establish AAA Inception framing for this project with the correct context:

**Current Situation:**
- NaturoSecure is the FIRST small release - ..."
   - **Raison**: Project structure and organization correctly routed to framer

#### Architecture → solution-architect

**Volume**: 16 délégations

**Exemples**:

1. **Tâche**: Analyze project structure for deployment
   - **Prompt**: "I need you to analyze the current project structure for "espace_naturo" to understand:

1. What type of application this is (frontend, backend, full-s..."
   - **Raison**: Complex design and architecture decisions correctly routed to specialist

2. **Tâche**: Analyser architecture Scaleway vs actuelle
   - **Prompt**: "Analysez l'architecture actuelle de l'application Espace Naturo et recommandez l'approche optimale pour le déploiement sur Scaleway.

**Contexte techn..."
   - **Raison**: Complex design and architecture decisions correctly routed to specialist

### ✗ Mauvais Routages

**10 cas identifiés** de routage sous-optimal.

#### Refactoring tasks should go to refactoring-specialist (available from P3)

**Volume**: 5 cas

**Exemples**:

1. **Agent choisi**: developer → **Devrait être**: refactoring-specialist
   - **Tâche**: Continue quality improvements
   - **Prompt**: "Continue the code quality improvement work that was started. The critical route duplication in server/routes.ts has been partially addressed (one dupl..."

2. **Agent choisi**: developer → **Devrait être**: refactoring-specialist
   - **Tâche**: Fix TypeScript errors
   - **Prompt**: "The application has 13 TypeScript errors preventing local testing. Fix these systematically:

**Critical Issues to Address:**

1. **Missing Client typ..."

---

## Période 3 (12-20 sept): Mandatory Delegation

**Configuration**: Politique obligatoire, +content-developer, +refactoring-specialist

**Volume**: 857 délégations

**Distribution agents**:
- developer: 344 (40.1%)
- git-workflow-manager: 153 (17.9%)
- backlog-manager: 86 (10.0%)
- architecture-reviewer: 64 (7.5%)
- solution-architect: 63 (7.4%)

### ✓ Bons Routages

**357 exemples identifiés** de routage approprié.

#### Git operations → git-workflow-manager

**Volume**: 153 délégations

**Exemples**:

1. **Tâche**: Complete git tagging and push
   - **Prompt**: "I need to complete the hotfix deployment process:

1. We just made a commit aa4eb49 with message "fix(auth): remove password hashing duplication in se..."
   - **Raison**: Version control operations correctly routed to git specialist

2. **Tâche**: Create major version tag and release
   - **Prompt**: "Create version tags for this major milestone in the Espace Naturo project.

CONTEXT:
We just completed a major deployment milestone with critical prod..."
   - **Raison**: Version control operations correctly routed to git specialist

#### Task management → backlog-manager

**Volume**: 86 délégations

**Exemples**:

1. **Tâche**: Add upload failure to backlog
   - **Prompt**: "I need to add a critical production bug to the backlog for Espace Naturo:

**Bug Report:**
- **Title**: Production Upload Failure - 500 Access Denied
..."
   - **Raison**: Task planning and tracking correctly routed to backlog manager

2. **Tâche**: Update backlog after deployment fixes
   - **Prompt**: "Update the project backlog based on the recent deployment work and fixes completed for Espace Naturo.

CONTEXT:
We just successfully completed a major..."
   - **Raison**: Task planning and tracking correctly routed to backlog manager

#### Architecture → solution-architect

**Volume**: 55 délégations

**Exemples**:

1. **Tâche**: Analyze URL detection at startup
   - **Prompt**: "The user wants to show the complete URL in the server startup message instead of just "serving on port 5000". There's an existing `getBaseUrlFromReque..."
   - **Raison**: Complex design and architecture decisions correctly routed to specialist

2. **Tâche**: Analyze URL detection at startup
   - **Prompt**: "The user wants to show the complete URL in the server startup message instead of just "serving on port 5000". There's an existing `getBaseUrlFromReque..."
   - **Raison**: Complex design and architecture decisions correctly routed to specialist

### ✗ Mauvais Routages

**119 cas identifiés** de routage sous-optimal.

#### Refactoring tasks should go to refactoring-specialist (available from P3)

**Volume**: 3 cas

**Exemples**:

1. **Agent choisi**: developer → **Devrait être**: refactoring-specialist
   - **Tâche**: Test self-request for URL detection
   - **Prompt**: "Let's test a pragmatic hotfix approach: making a self-request at startup to determine the complete URL.

Context: This is hotfix code that can be "dég..."

2. **Agent choisi**: developer → **Devrait être**: refactoring-specialist
   - **Tâche**: Refactor db.ts for lazy initialization
   - **Prompt**: "The user wants to refactor server/db.ts to use lazy initialization instead of connecting to the database at import time. Currently, the database conne..."

#### Architecture/design questions should go to solution-architect

**Volume**: 2 cas

**Exemples**:

1. **Agent choisi**: developer → **Devrait être**: solution-architect
   - **Tâche**: Query dev database for naturopath
   - **Prompt**: "The user wants to find the naturopath user in the development database. 

Looking at the codebase, this appears to be an Espace Naturo project with Po..."

2. **Agent choisi**: developer → **Devrait être**: solution-architect
   - **Tâche**: Refactor db.ts for lazy initialization
   - **Prompt**: "The user wants to refactor server/db.ts to use lazy initialization instead of connecting to the database at import time. Currently, the database conne..."

### ≈ Analyse: Explosion de `developer` (344 calls)

**Breakdown par catégorie**:

- **Testing**: 268 (77.9%)
- **Implementation**: 45 (13.1%)
- **Debugging**: 21 (6.1%)
- **Documentation**: 4 (1.2%)
- **Other**: 4 (1.2%)
- **Refactoring**: 2 (0.6%)

**Observation**: 77.9% des appels à `developer` sont pour des tâches de testing. Cela suggère:
1. Testing est légitimement une tâche de developer
2. Pas de spécialiste testing disponible → routage vers généraliste
3. Le volume élevé reflète l'adoption de TDD pendant cette période

**Mauvais routage**: Les 13.1% d'implémentation et 6.1% debugging incluent probablement des cas qui auraient dû aller vers:
- `refactoring-specialist` (pour refactoring)
- `solution-architect` (pour questions d'architecture)

### ? Agents Sous-Utilisés

- **project-framer**: 4 calls (0.5%)
- **content-developer**: 0 calls (0.0%)
- **refactoring-specialist**: 11 calls (1.3%)

**Analyse `content-developer`**: **0 calls** en Période 3 (12-20 sept).

**Hypothèses**:
1. **Pas de tâches de contenu pur** pendant cette période
2. **Routage vers developer**: Tâches de documentation/contenu vont vers developer générique
3. **Description ambiguë**: Le general agent ne distingue pas contenu vs code documentation

---

## Période 4 (21-30 sept): Post-Restructuration

**Configuration**: senior-developer + junior-developer split, safeguards scope creep

**Volume**: 307 délégations

**Distribution agents**:
- senior-developer: 70 (22.8%)
- backlog-manager: 49 (16.0%)
- refactoring-specialist: 33 (10.7%)
- solution-architect: 33 (10.7%)
- code-quality-analyst: 31 (10.1%)

### ✓ Bons Routages

**144 exemples identifiés** de routage approprié.

#### Task management → backlog-manager

**Volume**: 45 délégations

**Exemples**:

1. **Tâche**: Update backlog status
   - **Prompt**: "Update the backlog to accurately reflect the current state of CONS1.8 (document editing).

CURRENT SITUATION:
- CONS1.8: "Editer conseils client" is m..."
   - **Raison**: Task planning and tracking correctly routed to backlog manager

2. **Tâche**: Update backlog with current status
   - **Prompt**: "The user has requested an update to the backlog. Based on the recent work completed:

CONTEXT:
- CONS1.8 document editing functionality has been inves..."
   - **Raison**: Task planning and tracking correctly routed to backlog manager

#### Refactoring → refactoring-specialist

**Volume**: 28 délégations

**Exemples**:

1. **Tâche**: Remove deprecated IStorageValidator
   - **Prompt**: "I need you to fix a critical seeding bug in the worktree `/Users/guillaume/dev/client/espace_naturo_seeding_fix` on branch `fix/seeding-postgres-schem..."
   - **Raison**: Code quality improvements correctly routed to refactoring specialist

2. **Tâche**: Refactor SESSION DRY violations
   - **Prompt**: "**CONTEXTE**: Tu travailles dans le worktree `/Users/guillaume/dev/client/espace_naturo-session` sur la branche `fix/session-404`. Le code-quality-ana..."
   - **Raison**: Code quality improvements correctly routed to refactoring specialist

#### Architecture → solution-architect

**Volume**: 26 délégations

**Exemples**:

1. **Tâche**: Analyze seeding bugs group
   - **Prompt**: "**CONTEXTE**: Tu travailles sur le projet Espace Naturo (plateforme échange documents médicaux pour naturopathes) dans un worktree dédié `/Users/guill..."
   - **Raison**: Complex design and architecture decisions correctly routed to specialist

2. **Tâche**: Extract Docker scripts
   - **Prompt**: "Analyze the current Docker build and run workflow in the Espace Naturo project and design a plan to separate the build and run operations.

Currently,..."
   - **Raison**: Complex design and architecture decisions correctly routed to specialist

### ✗ Mauvais Routages

**11 cas identifiés** de routage sous-optimal.

#### Simple tasks should be delegated to junior-developer

**Volume**: 3 cas

**Exemples**:

1. **Agent choisi**: senior-developer → **Devrait être**: junior-developer
   - **Tâche**: Implement SEEDING fixes
   - **Prompt**: "**CONTEXTE**: Tu travailles sur le projet Espace Naturo dans le worktree `/Users/guillaume/dev/client/espace_naturo-seeding` sur la branche `fix/seedi..."

2. **Agent choisi**: senior-developer → **Devrait être**: junior-developer
   - **Tâche**: Implement SESSION fix
   - **Prompt**: "**CONTEXTE**: Tu travailles sur le projet Espace Naturo dans le worktree `/Users/guillaume/dev/client/espace_naturo-session` sur la branche `fix/sessi..."

#### Refactoring tasks should go to refactoring-specialist (available from P3)

**Volume**: 2 cas

**Exemples**:

1. **Agent choisi**: developer → **Devrait être**: refactoring-specialist
   - **Tâche**: TDD clickable links implementation
   - **Prompt**: "Implement clickable links in notes and descriptions using TDD approach.

Context:
- Working in: /Users/guillaume/dev/client/espace_naturo-clickable-li..."

2. **Agent choisi**: developer → **Devrait être**: refactoring-specialist
   - **Tâche**: Simplify password script with inquirer
   - **Prompt**: "Refactor `/Users/guillaume/dev/client/espace_naturo/scripts/update-password.ts` to use `@inquirer/prompts` instead of custom readline implementation.
..."

### ? Agents Sous-Utilisés

- **project-framer**: 2 calls (0.7%)
- **content-developer**: 0 calls (0.0%)
- **junior-developer**: 4 calls (1.3%)

**Analyse `junior-developer`**: Disponible depuis restructuration 21 sept, mais seulement 4 calls (1.3%).

**Hypothèses**:
1. **Description peu claire**: Le general agent ne comprend pas quand utiliser junior vs senior
2. **Prompts pas adaptés**: Les prompts utilisateur ne signalent pas "tâche simple"
3. **Biais vers senior**: Par défaut, routage vers senior-developer par sécurité

**Validation**: 2 des 11 cas de mauvais routage en P4 sont senior-developer → junior-developer.

**Analyse `content-developer`**: **0 calls** en Période 4 (21-30 sept).

**Hypothèses**:
1. **Pas de tâches de contenu pur** pendant cette période
2. **Routage vers developer**: Tâches de documentation/contenu vont vers developer générique
3. **Description ambiguë**: Le general agent ne distingue pas contenu vs code documentation

---

## Synthèse Cross-Période

### Améliorations Mesurées (P3 → P4)

**1. Réduction des mauvais routages**:
- P3: 119 cas (13.9%)
- P4: 11 cas (3.6%)

**2. Meilleure utilisation des spécialistes**:
- `refactoring-specialist`: P3 11 (1.3%) → P4 33 (10.7%)

**3. Introduction hiérarchie developer**:
- `senior-developer` adopté (70 calls, 22.8% en P4)
- `junior-developer` sous-utilisé (4 calls, 1.3% en P4)

### Blocages Persistants

**1. Routage par défaut vers généraliste**:
- P2: `developer` 11.9%
- P3: `developer` 40.1% (explosion)
- P4: `senior-developer` 22.8%

**Cause**: Lorsque le general agent hésite, il route vers le developer généraliste plutôt que vers un spécialiste.

**2. Spécialistes jamais utilisés**:
- `content-developer`: 0 calls en P3 ET P4
- `project-framer`: <1% en P3 et P4 (utilisé seulement en P2)

**Cause**: Descriptions d'agents pas assez claires OU tâches correspondantes absentes.

**3. Overhead `backlog-manager`**:
- P2: 25.8% (2e position)
- P3: 10.0% (3e position)
- P4: 14.7% (2e position)

**Question**: Est-ce légitime ou overhead? Backlog-manager toujours dans le top 3.

### Patterns de Routage Réussis à Préserver

**1. Git → git-workflow-manager** (153 calls en P3):
- Pattern le plus fort et le plus clair
- Aucun cas de mauvais routage détecté

**2. Architecture → solution-architect** (présent dans toutes périodes):
- P2: 13.9%, P3: 7.4%, P4: 10.1%
- Routage approprié pour questions de design/architecture

**3. Refactoring → refactoring-specialist** (P3-P4):
- Adoption progressive: P3 1.3% → P4 10.7%
- Amélioration claire post-restructuration

---

## Ce Qui Bloque le "Hands-Off" Aujourd'hui (P4)

### 1. junior-developer Pas Adopté

**Impact**: Tâches simples vont vers senior-developer, gaspillage de ressources.

**Exemples concrets** (P4):
1. **Implement SEEDING fixes**
   - Routé vers: senior-developer
   - Devrait être: junior-developer
   - Prompt: "**CONTEXTE**: Tu travailles sur le projet Espace Naturo dans le worktree `/Users/guillaume/dev/client/espace_naturo-seeding` sur la branche `fix/seedi..."

2. **Implement SESSION fix**
   - Routé vers: senior-developer
   - Devrait être: junior-developer
   - Prompt: "**CONTEXTE**: Tu travailles sur le projet Espace Naturo dans le worktree `/Users/guillaume/dev/client/espace_naturo-session` sur la branche `fix/sessi..."

**Actions**:
1. Clarifier description de `junior-developer` (quelles tâches?)
2. Ajouter exemples explicites de tâches junior vs senior
3. Encourager utilisateur à signaler "tâche simple" dans prompts

### 2. Routage par Défaut Vers Généraliste

**Impact**: Spécialistes sous-utilisés, surcharge des généralistes.

**P4**: 11 cas de mauvais routage identifiés (3.6% des délégations)

**Actions**:
1. Améliorer descriptions d'agents (plus explicites sur leurs domaines)
2. Ajouter exemples de tâches dans descriptions
3. Créer guide de routage pour le general agent

### 3. Agents Fantômes (content-developer, project-framer)

**Impact**: Agents présents mais jamais utilisés → complexité inutile.

**Actions**:
1. **Option A**: Supprimer agents inutilisés
2. **Option B**: Clarifier leurs use cases + communiquer à utilisateur
3. **Option C**: Analyser pourquoi pas de tâches correspondantes

---

## Notes Méthodologiques

### Détection de Mauvais Routage

**Heuristiques utilisées**:
- Mots-clés dans prompt/description vs agent choisi
- Architecture/design → solution-architect
- Refactoring → refactoring-specialist
- Git operations → git-workflow-manager
- Simple tasks → junior-developer
- Performance → performance-optimizer

**Limites**:
1. **Faux négatifs**: Mauvais routages sans mots-clés évidents non détectés
2. **Faux positifs**: Certains cas flaggés peuvent être légitimes (ex: developer pour implémenter après architecture)
3. **Context partiel**: Analyse basée sur prompt/description, sans historique complet de session

### Détection de Bon Routage

**Critères**:
- Alignement mots-clés tâche ↔ spécialité agent
- Utilisation cohérente de spécialistes pour leurs domaines

**Limite**: Bon routage ne garantit pas succès de la tâche (dépend de la qualité d'exécution de l'agent).
