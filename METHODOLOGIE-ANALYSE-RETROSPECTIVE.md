# Méthodologie Analyse Rétrospective - Framework Pur

**Version**: 2.0 (Framework neutre, ré-analyse complète chaque fois)
**Date**: 2025-09-30
**Principe**: Découverte neutre sans biais conclusions précédentes

---

## Framework VACE

### **V - Validate Foundations**
Valider bases AVANT analyser. Git + Data + Assumptions.

### **A - Analyze Parallel**
LLM agents (sémantique) + Scripts (objectif) + Git (qualité) **en parallèle**.

### **C - Cross-check Findings**
Résoudre contradictions avec données primaires.

### **E - Evolve with Feedback**
User corrections + versioning + questions ouvertes.

---

## Séquence Analyse

### **Phase 0: FOUNDATIONS** (1-2 jours) ⚠️ BLOQUANT

**Objectif**: Valider bases avant analyser. Erreur ici = conclusions invalides.

#### 1. Git Archaeology (30min - 1h) - CRITIQUE

**Configurations timeline** (À FAIRE CHAQUE analyse):
```bash
# Agent configurations
cd ~/.claude-memories
git log --all --format="%ai | %s" --since="YYYY-MM-01" --until="YYYY-MM-31" \
  | grep -iE "(agent|Agent)"

# Découvrir: Quand agents ajoutés? Modifications système? Restructurations?
```

**Repos actifs** (contexte développement):
```bash
find ~/dev -name ".git" -type d 2>/dev/null | while read gitdir; do
    repo=$(dirname "$gitdir")
    cd "$repo"
    commits=$(git log --all --since="YYYY-MM-01" --until="YYYY-MM-31" \
      --oneline 2>/dev/null | wc -l)
    if [ "$commits" -gt 0 ]; then
        echo "$repo: $commits commits"
    fi
done
```

**Pourquoi CHAQUE fois**:
- Timeline système évolue (agents ajoutés/retirés/modifiés)
- Pas d'assumptions sur configurations
- Découverte neutre de l'état système période analysée

**Livrables**:
- Timeline configurations validée (dates ajouts/modifications agents)
- Repos actifs identifiés (contexte développement)
- Document: `AGENT-TIMELINE-VALIDATED.md`

#### 2. Data Inventory (15-30min)

**Data Consolidation** (first-time setup):
```bash
# Consolidate snapshots + current data (run once, then incremental)
python3 scripts/consolidate_all_data.py --dry-run  # Preview
python3 scripts/consolidate_all_data.py            # Execute

# For incremental updates only (add recent sessions)
python3 scripts/copy_conversations.py --dry-run   # Preview
python3 scripts/copy_conversations.py             # Execute
```

**Inventory Check**:
```bash
ls -lh data/conversations/
# Volumes par période, gaps identifiés
```

**Flag anomalies** (investigation triggers):
- Volume spikes/drops
- Missing data (évaluer criticité)
- Data quality (truncation, null values)

#### 3. Assumptions Validation (15min sync user)

**Checklist**: `TEMPLATES/assumptions-checklist.md`
- [ ] Timeline système vérifiée avec git
- [ ] Baseline période identifiée (pré-changements config)
- [ ] Data gaps documentés (criticité)
- [ ] Context external (développement ongoing?)

**Méthode**: List assumptions → Sync user 15min → Validate with git/data

---

### **Phase 1: EXTRACTION** (1-2 jours)

#### 1. Enriched Data Extraction

**Principe**: Full context + coûts tokens

```python
delegation = {
    "user_context_before": extract_user_message_text(prev_msg),
    "result_full": str(res.get("content", "")),  # Not truncated
    "sequence_number": idx + 1,
    "previous_agent": delegations[idx-1]["agent_type"] if idx > 0 else None,
    "next_agent": delegations[idx+1]["agent_type"] if idx+1 < len(delegations) else None,

    # NOUVEAUX CHAMPS CRITIQUES (ROI)
    "input_tokens": delegation.get("input_tokens"),
    "output_tokens": delegation.get("output_tokens"),
    "model_used": delegation.get("model")
}
```

**Validation**: Check 3-5 sessions manuellement (context complet? tokens présents?).

**Note**: Si tokens pas disponibles dans logs, estimer via:
```python
estimated_input_tokens = len(prompt_text) / 4  # ~4 chars per token
```

#### 2. Classification AVANT Agrégation

**Marathons** (`TEMPLATES/classification-framework.py`):
```python
def classify_marathon(session):
    if deleg_count <= 20: return None

    success_rate = (successes / total * 100)
    cascade_rate = (consecutive_same_agent / (total-1) * 100)

    if success_rate >= 85: return "POSITIVE"  # Productive work
    elif success_rate < 80: return "NEGATIVE"  # Pathological
    else: return "AMBIGUOUS"  # Needs review
```

**Failures** (taxonomy, pas juste count):
- USER_TOOL_INTERVENTION (ambiguous)
- AGENT_NOT_FOUND (config issue)
- TIMEOUT, EXECUTION_ERROR, etc.

#### 3. Segmentation Temporelle

**Basée sur git timeline** (Phase 0):
```python
def classify_period(date_str, config_changes):
    # Use git-validated config change dates
    # No hardcoded assumptions about periods
    for change in config_changes:
        if date_str < change["date"]:
            return change["period_before"]
    return "CURRENT"
```

---

### **Phase 2: ANALYSIS** (3-5 jours)

#### Approche Parallèle (MAXIMISER CONCURRENCE)

**Lancer TOUT en parallèle** (1 message, multiple tool calls):

```
# Agents LLM (4 simultanés)
Task(subagent_type="agent-1", description="Routage patterns")
Task(subagent_type="agent-2", description="Failure taxonomy")
Task(subagent_type="agent-3", description="Coordination & marathons")
Task(subagent_type="agent-4", description="Quality assessment")

# Scripts Python (pendant agents tournent)
python metrics_calculation.py
python cascade_analysis.py
python tokens_roi_analysis.py

# Git validation (après claims qualité émis)
```

**Git Forensics** (investigation hypothèses):

Agents LLM peuvent investiguer plus profondément via git:

```bash
# Retrouver description agent à l'époque
cd ~/.claude-memories
git log --all --format="%ai %h" --since="YYYY-MM-DD" --until="YYYY-MM-DD" \
  | grep -iE "(agent-name)"
git show <commit>:.claude/agents/agent-name.md  # Description d'époque

# Explorer causalité dans projets
cd ~/dev/projet
git log --all --since="YYYY-MM-DD" --until="YYYY-MM-DD" --oneline
git diff <commit>^..<commit>  # Comprendre changements
```

**Quand utiliser**:
- Agent pattern inexpliqué → Voir description agent d'époque
- Hypothèse causalité (ex: "junior ignoré car projets complexes") → Fouiller git projets
- Claims sur "over-engineering" → Valider diffs réels

**Cross-check findings** quotidiennement:
- Agent claims vs Scripts metrics
- Quality assertions vs Git diffs
- Contradictions → Return to primary data (+ git forensics si nécessaire)

**Livrables**:
- 4 analyses agents (`agent-analyses/*.md`)
- Métriques objectives (`metrics-report.json`)
- Git validation (`git-validation-sessions.md`)
- Cross-validation (`contradictions-resolved.md`)

---

### **Phase 3: SYNTHESIS** (2-3 jours)

1. **Draft conclusions v1.0**
   - Framework ✓✗≈? par période
   - Synthèse cross-période
   - 5 Whys blocages
   - Recommendations P0/P1/P2

2. **User feedback** (30min sync)
   - Présenter findings majeurs
   - Corrections user
   - Context manquant

3. **Re-analyze si assumptions invalides**
   - Re-segment data
   - Re-compute métriques
   - Version document (vX.Y → vX.Y+1)

4. **Final synthesis + learnings**
   - Documenter processus
   - Learnings méthodologiques (pour humain, pas prochaine analyse)

---

## Principes Clés

### 1. Git = Source of Truth + Investigation Tool
- **Timeline** (Phase 0): Config history (agents added when? modified?)
- **Quality** (Phase 2): Diffs (+LOC/-LOC, commit types, complexity)
- **Context** (Phase 0): Active repos, development ongoing
- **Forensics** (Phase 2): Descriptions agents d'époque, causalités projets

**Règle Phase 0**: Git archaeology CHAQUE analyse (pas d'assumptions timeline).

**Règle Phase 2**: Agents LLM peuvent investiguer git pour valider hypothèses:
- `~/.claude-memories`: Source de vérité descriptions agents historiques
- `~/dev/projets`: Explorer causalités (ex: projets complexes → junior ignoré?)

### 2. Classification > Agrégation
Comprendre nature AVANT quantifier:
- Marathons: success_rate + cascade_rate → positive/negative/ambiguous
- Failures: taxonomy (not just true/false)
- Coûts: tokens par type agent, par type tâche

**Règle**: Classifier D'ABORD, agréger ensuite.

### 3. Assumptions = Hypothèses à Tester
Ne jamais assumer:
- Timeline système (git verify)
- Nature patterns (classify verify)
- Baseline période (user + git confirm)

**Règle**: List → Validate → Proceed.

### 4. Agents LLM = Générateurs Hypothèses
Riches analyses sémantiques MAIS:
- Peuvent produire faux positifs
- Doivent être cross-checked (scripts, git)
- Pas source vérité absolue

**Règle**: Agent claims → Validate with data/git.

### 5. Data Gaps = Investigation Triggers
Anomalie volume/qualité → Stop, investigate:
- Pourquoi gap?
- Impact sur conclusions?
- Contournable ou bloquant?

**Règle**: Document gaps + criticité (Phase 0).

### 6. User Knows Context
Sync points critiques:
- **Phase 0** (15min): Assumptions validation
- **Phase 3** (30min): Findings feedback

**Règle**: Corrections early > revisions late.

### 7. Parallélisation Maximum
**Performance > Séquentialité**:
- Bash: Multiple commands → 1 message, multiple Bash calls
- Agents: 4 agents → 1 message, 4 Task calls
- Scripts + Git + LLM concurrent

**Règle**: Si indépendant, paralléliser.

---

## Metrics Tokens & ROI

### Metrics Obligatoires (Extraction Phase 1)

**Par délégation**:
- `input_tokens`: Tokens prompt envoyé
- `output_tokens`: Tokens réponse générée
- `model_used`: Model (contexte)

**Agrégations**:
- Tokens total par session
- Tokens moyen par type agent
- Tokens par type tâche (simple/complexe)
- ROI marathons (tokens vs output quality git)

### Calculs ROI

```python
# Tokens par agent type
tokens_by_agent = df.groupby('agent_type')[['input_tokens', 'output_tokens']].sum()
tokens_by_agent['total'] = tokens_by_agent.sum(axis=1)

# ROI junior vs senior
junior_tokens = tokens_by_agent.loc['junior-developer', 'total']
senior_tokens = tokens_by_agent.loc['senior-developer', 'total']
# Compare: tasks done, quality (git), tokens

# ROI marathons
marathon_tokens = marathons[['input_tokens', 'output_tokens']].sum().sum()
marathon_output = git_validate_marathons()  # LOC net, features
roi = marathon_output / marathon_tokens  # Output per token

# Overhead système
baseline_tokens = baseline_sessions[['input_tokens', 'output_tokens']].sum(axis=1).mean()
current_tokens = current_sessions[['input_tokens', 'output_tokens']].sum(axis=1).mean()
overhead_pct = ((current_tokens - baseline_tokens) / baseline_tokens) * 100
```

### Analyse ROI Questions

- **Junior adoption**: Économie tokens réelle vs overhead routing?
- **Marathons**: Tokens justifiés par output qualité?
- **Cascades**: Gaspillage tokens auto-délégations?
- **Complexité tâches**: Simple fixes vs features (tokens/task)?
- **Overhead système**: +X% tokens = quels gains mesurables?

**Tokens = unité ROI** (pas temps estimé, pas dollars).

---

## Anti-Patterns

### ❌ 1. Assumptions Non Validées
**Erreur**: Commencer sans git archaeology.
**Impact**: Timeline/conclusions fausses.
**Solution**: Git archaeology Phase 0 (bloquant).

### ❌ 2. Stats Avant Comprendre
**Erreur**: Scripts métriques avant sémantique.
**Impact**: Contexte perdu, patterns manqués.
**Solution**: LLM agents D'ABORD, scripts après.

### ❌ 3. Classification Tardive
**Erreur**: Agréger puis essayer classifier.
**Impact**: Nature patterns incomprise.
**Solution**: Classify AVANT aggregate.

### ❌ 4. Data Gaps Ignorés
**Erreur**: Continuer malgré anomalie volume.
**Impact**: Conclusions biaisées/invalides.
**Solution**: Flag Phase 0, document impact.

### ❌ 5. Agent Claims Non Validés
**Erreur**: Accepter conclusions qualité sans git.
**Impact**: Faux positifs (textual signals ≠ code reality).
**Solution**: Cross-check ALWAYS (agents vs git).

### ❌ 6. Travail Séquentiel
**Erreur**: 1 tâche à la fois, bash avec &&.
**Impact**: Session 3× plus longue.
**Solution**: Paralléliser (multiple tool calls).

### ❌ 7. Biais Conclusions Précédentes
**Erreur**: Chercher patterns découverts avant.
**Impact**: Confirmation bias, nouveaux patterns manqués.
**Solution**: Ré-analyse NEUTRE chaque fois.

---

## Structure Versionnée (Prospective)

**Chaque analyse** = nouveau répertoire:

```bash
# Début analyse
mkdir analyses/vX.X-mois-2025
cd analyses/vX.X-mois-2025

# Tous fichiers générés ICI pendant analyse
# Templates copiés si besoin

# Fin analyse: Archive, continue suivante
```

**Avantages**:
- Évolution claire versions
- Contexte préservé par période
- Référençable ("voir v7.0 validation git")

---

## Checklist Complète

### AVANT Commencer (Phase 0 - Bloquant):
- [ ] Git archaeology configs (`~/.claude-memories`)
- [ ] Git active repos (development context)
- [ ] Data inventory (volumes, gaps, anomalies)
- [ ] Assumptions list → Sync user 15min
- [ ] Gaps documentés (criticité)
- [ ] Version directory créé

### PENDANT Extraction (Phase 1):
- [ ] Enriched data (full context + **tokens**)
- [ ] Classification frameworks applied
- [ ] Sample validation (3-5 sessions)
- [ ] Segmentation git-based (no assumptions)

### PENDANT Analyse (Phase 2):
- [ ] Agents + Scripts + Git **PARALLEL**
- [ ] Cross-check findings daily
- [ ] Git validation quality claims
- [ ] Contradictions flagged + resolved

### APRÈS Conclusions (Phase 3):
- [ ] User feedback sync (30min)
- [ ] Contradictions resolved with data
- [ ] Synthesis versioned (document changes)
- [ ] Learnings captured (méthodologique)

---

## Templates Disponibles

`TEMPLATES/`:
1. `assumptions-checklist.md` - Phase 0 validation
2. `timeline-reconstruction.sh` - Git archaeology automatisé
3. `classification-framework.py` - Classifier marathons/failures
4. `cross-validation-report.md` - Résolution contradictions
5. `version-README-template.md` - README futures versions

**Note**: Script extraction (Phase 1) à refaire pour inclure tokens data.

---

## Parallélisation Patterns

### Bash Commands (Multiple Indépendants)
```bash
# ✓ GOOD: 1 message, multiple Bash tool calls
Bash(command="git status")
Bash(command="git diff")
Bash(command="git log")

# ✗ BAD: Chaîné avec &&
Bash(command="git status && git diff && git log")
```

### Agent Analyses (4 Simultanés)
```bash
# ✓ GOOD: 1 message, 4 Task tool calls
Task(agent-1, routage)
Task(agent-2, failures)
Task(agent-3, coordination)
Task(agent-4, quality)

# ✗ BAD: 4 messages séquentiels
```

### Analyses Mixtes (Concurrent)
```bash
# ✓ GOOD: Tout parallèle quand possible
# - Agents LLM lancés (long)
# - Pendant: Scripts Python (rapide)
# - Puis: Git validation claims
```

---

## Principe Directeur

> **"Chaque analyse = découverte complète et neutre."**

**Pas d'assumptions**:
- Timeline système (git archaeology CHAQUE fois)
- Nature patterns (classify AVANT aggregate)
- Baseline période (user + git validate)

**Pas de biais**:
- Conclusions précédentes
- Patterns attendus
- Hypothèses non testées

**Ré-analyse COMPLÈTE** pour découvrir ce qui EST, pas confirmer ce qui ÉTAIT.

---

**Version**: 2.0 - Framework pur sans biais
**Date**: 2025-09-30