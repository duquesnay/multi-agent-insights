# Analyse Rétrospective Système Multi-Agents - Méthodologie

## Objectif

Comprendre l'**évolution du système de délégation multi-agents** pendant septembre 2025 pour identifier ce qui empêche les sessions "hands-off" et mesurer l'impact des optimisations architecturales.

**Focus**: Le système lui-même ET ses transformations temporelles.

---

## ⚠️ CRITICAL: Infrastructure-First Principle

**Before writing ANY custom extraction/analysis code:**

1. **Check existing tools first**: `python -m tools.pipeline.run_analysis_pipeline --help`
2. **Try pipeline with filters**: Use `--project`, `--start-date`, `--end-date`
3. **Only if pipeline cannot handle**: Then consider custom scripts

### Common Mistake

❌ **WRONG**: Writing `/tmp/analyze_*.py` without checking if pipeline supports your use case

✅ **RIGHT**: Using existing pipeline with runtime configuration

### Scratch Scripts for One-Off Analysis

If you **must** write a temporary exploration script (after checking pipeline cannot handle it):

**Use the `scratch/` directory** (git-ignored, organized, discoverable):
```bash
# Create temporary script in scratch/
cat > scratch/explore_cold_chamber_oct8.py << 'EOF'
import sys
sys.path.insert(0, '.')
from tools.common.data_repository import load_sessions

sessions = load_sessions()
# ... your exploration code ...
EOF

python scratch/explore_cold_chamber_oct8.py
```

**NOT in `/tmp`** (hard to find, lost across sessions, no context)

See `scratch/README.md` for naming conventions and guidelines.

### Decision Workflow

```
Need data?
  → Check --help
    → Pipeline supports it?
      → Use pipeline ✅
    → Pipeline doesn't support?
      → Write custom script (document why pipeline couldn't handle it)
```

### Examples

**✅ RIGHT WAY** (Recent data from specific project):
```bash
python -m tools.pipeline.run_analysis_pipeline \
  --project "cold-chamber" \
  --start-date 2025-10-08 \
  --end-date 2025-10-08 \
  --all
```

**❌ WRONG WAY** (Custom script without checking):
```python
# DON'T do this without checking pipeline first:
cat > /tmp/analyze_recent.py << 'EOF'
import json
from pathlib import Path
# ... reinventing pipeline functionality ...
EOF
```

**Why this matters**: The pipeline handles project filtering, date ranges, caching, data schema, and error handling. Custom scripts bypass all this infrastructure and create maintenance debt.

**See**: "Running Analyses" section below for detailed pipeline usage.

---

## Découverte Méthodologique Critique

**Le système a évolué pendant la période d'observation.**

Septembre 2025 contient **7 modifications architecturales majeures**:
- 03 sept: +solution-architect, +project-framer
- 12 sept: Politique délégation obligatoire
- 15 sept: +content-developer
- 20 sept: +refactoring-specialist
- **21 sept 16h24**: **developer → senior-developer + junior-developer** (restructuration majeure)
- 21-22 sept: Safeguards scope creep
- 22 sept: +parallel-worktree-framework

**Implication**: Les 1250 délégations ne décrivent pas **un** système mais **plusieurs versions successives**. Une analyse qui traite les données comme homogènes produit des conclusions **invalides**.

## Approche Méthodologique

### Analyse Temporellement Segmentée

**3 périodes analysables**:

**P2 - "Conception Added" (3-11 sept)**
- Configuration: +solution-architect, +project-framer
- Volume: ~15-20 sessions
- Valeur: Baseline avec capacités de planification

**P3 - "Délégation Obligatoire" (12-20 sept)**
- Configuration: Politique obligatoire, +content-developer, +refactoring-specialist
- Volume: ~75-85 sessions
- Valeur: Système sous contrainte (contient 8/10 sessions marathon)

**P4 - "Post-Restructuration" (21-30 sept)**
- Configuration: senior-developer + junior-developer, safeguards actifs
- Volume: 33 sessions
- Valeur: Système optimisé actuel
- **Amélioration mesurée**: -33% marathons, -27% délégations/session vs P3

### Framework ORID Temporel

Pour chaque période:
1. **Observations (O)**: Faits mesurables spécifiques à cette configuration
2. **Réactions (R)**: Interprétations dans le contexte de cette période
3. **Insights (I)**: Causes racines valides pour cette configuration
4. ~~**Décision (D)**~~: Non inclus - appartient à l'utilisateur

Puis **synthèse cross-période**:
- **→ Améliorations**: Problèmes résolus par modifications
- **↔ Persistants**: Problèmes présents dans toutes les périodes
- **← Régressions**: Nouveaux problèmes post-modifications

### Structure ✓✗≈? par Période

Pour chaque dimension analysée (routage, autonomie, coordination, efficacité):

- **✓ Positif**: Ce qui fonctionne bien dans cette configuration
- **✗ Négatif**: Ce qui dysfonctionne clairement
- **≈ Ambivalent**: Situations complexes sans jugement simple
- **? Mystères**: Phénomènes inexpliqués nécessitant investigation

### 5 Whys Évolutifs

Pour chaque dysfonctionnement:
1-3. Causes spécifiques à la période
4. Cause structurelle (potentiellement cross-période)
5. Cause racine systémique

**Validation**: Si cause racine présente en P3 ET P4 → blocage persistant.

## Ce Que Je Veux Découvrir

### Par Période
- Patterns de succès et d'échec spécifiques à chaque configuration
- Impact mesurable de chaque modification architecturale
- Contradictions révélant la complexité du système

### Cross-Période
- **Blocages persistants**: Dysfonctionnements présents dans toutes les configurations
- **Améliorations validées**: Problèmes résolus par la restructuration
- **Régressions**: Nouveaux problèmes introduits

### Focus P4 (Système Actuel)
- Ce qui empêche encore le "hands-off" malgré les optimisations
- Pourquoi 2 marathons persistent post-restructuration
- Adoption réelle de junior-developer

## Anti-Patterns à Éviter

### Erreurs Méthodologiques
- ❌ Traiter les données comme homogènes (mélanger P2, P3, P4)
- ❌ Comparer métriques sans segmentation temporelle
- ❌ Ignorer les biais d'apprentissage utilisateur
- ❌ Conclusions causales sans validation cross-période

### Erreurs d'Analyse
- ❌ Tableaux de métriques sans contexte temporel
- ❌ Conclusions hâtives sans validation statistique
- ❌ Généralités sans exemples concrets situés temporellement
- ❌ Ignorer les limites méthodologiques (volume P2 faible, confounding variables P3)

## Format de Sortie

### Documents Livrables

**1. temporal-segmentation-report.md**
- Découpage temporel détaillé
- Volume de données par période
- Métriques de base comparatives

**2. observations-comparative-v6.0.md**
Structure:
```
Avertissement Méthodologique
├── Période 2 (P2): Conception Added
│   ├── 1. Routage ✓✗≈?
│   ├── 2. Autonomie ✓✗≈?
│   └── [...]
├── Période 3 (P3): Délégation Obligatoire
│   └── [...]
├── Période 4 (P4): Post-Restructuration
│   └── [...]
├── Synthèse Évolutive
│   ├── Améliorations Mesurées (P3 → P4)
│   ├── Blocages Persistants (Cross-Période)
│   └── Régressions Introduites
├── 5 Whys: Blocages Persistants
└── Ce Qui Bloque le "Hands-Off" Aujourd'hui (P4)
```

**3. systemic-insights-v6.0.md**
- Causes racines validées cross-période
- Impact mesuré de la restructuration
- Blocages actuels et questions ouvertes

### Principes de Rédaction

**Chaque observation doit être**:
- **Située temporellement**: Valide pour quelle période?
- **Contextualisée architecturalement**: Quelle configuration?
- **Mesurée avec données complètes**: Segmentation appliquée
- **Validée cross-période**: Persiste après changements?
- **Reliée à l'objectif**: Quel blocage "hands-off" révèle-t-elle?

**Raconter des histoires avec les données**, mais:
- Histoires situées dans le temps (P2, P3, ou P4)
- Patterns validés par comparaison inter-périodes
- Surprises documentées avec leur contexte temporel
- Interrogations formulées comme hypothèses testables

## Biais et Limites Documentés

### Biais Reconnus
- **Apprentissage utilisateur**: Amélioration peut être due à l'expérience
- **Nouveauté**: Nouveaux agents sous-utilisés initialement
- **Complexité variable**: Tâches de septembre peuvent différer en difficulté

### Limites Statistiques
- **Volume P2 faible**: ~15-20 sessions (inférences limitées)
- **Confounding P3**: Multiples changements simultanés
- **Pas de contrôle**: Pas de groupe témoin sans modifications

### Limites d'Observation
- **Qualité code**: Non mesurée (nécessite git diff)
- **Satisfaction**: Données subjectives absentes
- **Coût opportunité**: Ce qui n'a pas été fait non quantifiable

## Learnings from Previous Analyses

### v7.1 (Septembre 2025) - Meta-Learnings

**Découvertes critiques**:
- **Git archaeology FIRST**: Timeline configs critique (août 4 launch découvert, pas juin)
- **Classification before aggregation**: Marathons 10/12 positifs (pas tous problèmes)
- **Agents LLM = hypothesis generators**: Valider avec git (Agent 4 faux positif over-engineering)
- **Data gaps = investigation triggers**: Août missing = période adoption critique
- **User corrections early > late revisions**: Sync assumptions Phase 0 saved 2 semaines rework

**Framework VACE** (Validate, Analyze, Cross-check, Evolve):
- Phase 0 BLOQUANTE: Git archaeology + data inventory + assumptions sync (15min user)
- Cross-validation formalisée: LLM vs Scripts vs Git (résoudre contradictions)
- Structure versionnée prospective: Créer répertoire analyse au début processus

**Nature modifications**: 80% application méthodologie existante + 20% additions tactiques.

**Référence complète**: See `METHODOLOGIE-ANALYSE-RETROSPECTIVE.md` + `RETROSPECTIVE-PROCESS-V7.1.md`

---

## Running Analyses

### Infrastructure-First Principle

**Before writing custom extraction/analysis code**: Check if the existing pipeline handles your use case.

The pipeline supports runtime configuration for different projects and time periods:

```bash
# Project-specific analysis with custom date range
python -m tools.pipeline.run_analysis_pipeline \
  --project "project-name" \
  --start-date 2025-10-01 \
  --end-date 2025-10-07 \
  --discover-periods \
  --all

# Use existing pipeline infrastructure - it's configurable
# Only create custom scripts if the pipeline cannot handle your use case
```

### Full Pipeline

```bash
# Run complete analysis pipeline (includes backup stage)
# Pipeline: backup → extraction → enrichment → segmentation → analysis → reporting
python -m tools.pipeline.run_analysis_pipeline --all

# Skip backup if using existing data or live source
python -m tools.pipeline.run_analysis_pipeline --all --skip-backup --source-live

# List available stages
python -m tools.pipeline.run_analysis_pipeline --list-stages

# Run specific stages
python -m tools.pipeline.run_analysis_pipeline --stage segmentation --stage analysis

# Resume from specific stage
python -m tools.pipeline.run_analysis_pipeline --from analysis

# Dry-run (preview without executing - shows planned stages upfront)
python -m tools.pipeline.run_analysis_pipeline --all --dry-run
```

**Note**: `--all` includes the backup stage which archives conversations from `~/.claude/projects/` to `data/conversations/`. Use `--skip-backup` to work with existing data or `--source-live` to read directly from live source.

### Individual Analyses

```bash
# List available analyses
python -m tools.pipeline.analysis_runner --list

# Run specific analysis
python -m tools.pipeline.analysis_runner --metrics
python -m tools.pipeline.analysis_runner --marathons

# Run all analyses
python -m tools.pipeline.analysis_runner --all
```

### Testing

```bash
# Run all tests (required before committing changes)
./run_tests.sh all

# Run specific test categories
./run_tests.sh unit
./run_tests.sh integration

# Generate coverage report
./run_tests.sh coverage
```

**Test requirement**: GREEN LINE - all tests must pass.

### Key Documentation

- `REFACTORING-COMPLETE.md` - What was done, why, and results
- `docs/PIPELINE.md` - Pipeline stages and execution order
- `DOMAIN-MODEL.md` - Data structures and typed models
- `TESTING.md` - Test suite guide

---

## Project Learnings

### 2025-10-03 - GitHub publication with private/public separation

**Methodological:**
- `.gitignore` patterns can be too broad - captured CHANGELOG.md initially. Test with `git status` after each pattern added rather than all at once.
- Local organization != Git organization. Users keep their local archives organized even if git doesn't see them. Separate "structure for me" from "structure for GitHub".

**Technical:**
- `git mv` preserves history but git-ignored files can be moved with regular `mv` without impacting the repo. Clarify this distinction to avoid confusion.

**Decision Anchors:**
- **Private archive structure**: For projects with dual public/private nature, use `analyses/{findings,methodology}/` + `reports/{implementation,performance}/`
- **Root cleanup threshold**: If >10 non-code files at root, trigger docs/ reorganization

---

## Principe Directeur

> **"On analyse l'évolution d'un système vivant, pas un système statique."**

La rigueur méthodologique prime sur les conclusions définitives. Documenter les incertitudes est plus important que forcer des certitudes.
- ALWAYS use english to create things: commands, docs, comments, git messages, etc.