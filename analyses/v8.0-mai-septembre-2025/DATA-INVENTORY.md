# Data Inventory - Phase 0

**Analysis Version**: v8.0
**Date**: 2025-09-30
**Period**: Mai-Septembre 2025 (focus Septembre)
**Analyst**: Claude Code (Sonnet 4.5)

---

## Primary Data Sources

### 1. Claude Projects (Live Data - PRIMARY SOURCE)

**Location**: `~/.claude/projects/`

**Volume**:
- 272 JSONL files across all projects
- ~98,583 total message lines
- Distribution par mois:
  - **Août 2025**: 139 messages
  - **Septembre 2025**: 97,025 messages

**Structure**:
```
~/.claude/projects/
├── [project-name]/
│   └── *.jsonl  # Chronological conversation logs per session
```

**Status**: ✅ Accessible, complet

---

### 2. Historical Extractions (Pre-Launch Baseline)

**Location**: `data/historical/`

**Périodes pré-agents** (avant 4 août 2025):
- **Mai 2025**: 10 sessions, 17 délégations
- **Juin 2025**: 31 sessions, 72 délégations
- **Juillet 2025**: 16 sessions, 24 délégations

**Total baseline**: 57 sessions, 113 délégations (ère mono-agent)

**Status**: ✅ Pre-processed, validé (v7.1)

---

### 3. Agent Calls Metadata

**Location**: `data/raw/agent_calls_metadata.csv`

**Volume**: 1,247 agent call records

**Champs**:
- timestamp, session_id, project_path
- agent_type, prompt_length, description

**Période**: Principalement septembre 2025

**Status**: ✅ Disponible, structuré

---

## Volume Analysis by Period

### Mai-Juillet 2025 (Pré-Agents)
- **Source**: data/historical/
- **Volume**: 57 sessions, 113 délégations
- **Configuration**: Mono-agent (pas d'agents spécialisés)
- **Usage**: Baseline pour comparaison

### Août 2025 (Launch + Vacances)
- **Source**: ~/.claude/projects/*.jsonl
- **Volume**: 139 messages (~5-10 sessions estimées)
- **Configuration**: Launch 4 août (8 agents), puis vacances 4-23 août
- **Contexte**: **Utilisateur en vacances** → faible utilisation normale
- **Usage**: Période transition (données limitées mais utilisables)

### Septembre 2025 (Premier Mois Complet)
- **Source**: ~/.claude/projects/*.jsonl
- **Volume**: 97,025 messages (~140-150 sessions estimées)
- **Configuration**: Évolutions multiples (voir git archaeology)
- **Usage**: **Focus principal de l'analyse**

---

## Data Quality Assessment

### ✓ Strengths

- **Logs complets** dans ~/.claude/projects/
- **Git-validated timeline** pour évolution système
- **Agent metadata** structurée (septembre)
- **Baseline historique** solide (mai-juillet)
- **Contexte external** documenté (vacances août)

### ⚠️ Limitations

- **Août faible volume** (vacances) → adoption initiale peu documentée
- **DB timestamps corrompus** (__store.db dates 1970) → ignorer DB
- **Snapshots conversations/** incohérents → utiliser JSONL direct

### ✓ Mitigation Strategy

1. **Primary**: Extract fresh from ~/.claude/projects/*.jsonl
2. **Historical baseline**: Use data/historical/ as-is
3. **Metadata**: agent_calls_metadata.csv pour septembre
4. **Ignore**: Snapshots conversations/, processed analyses v6.0-v7.1

---

## Segmentation Timeline (Git-Based)

### P0: Mai-Juillet 2025 (Baseline)
- **Config**: Mono-agent, no specialization
- **Data**: data/historical/ (57 sessions, 113 délégations)

### P1: Août 2025 (Launch + Vacances)
- **4 août**: Launch 8 agents (git: 795b476e)
- **4-23 août**: Vacances utilisateur
- **24-31 août**: Reprise utilisation
- **Data**: ~/.claude/projects/ (139 messages)
- **Note**: Faible volume attendu (contexte)

### P2: Sept 1-11 (Conception Added)
- **3 sept**: +solution-architect, +project-framer
- **Data**: À extraire de JSONL

### P3: Sept 12-20 (Délégation Obligatoire)
- **12 sept**: Politique délégation mandatory
- **15 sept**: +content-developer
- **20 sept**: +refactoring-specialist
- **Data**: ~75-85 sessions (ref v7.1)
- **Note**: Contient 8/10 marathons

### P4: Sept 21-30 (Post-Restructuration)
- **21 sept 16h24**: **senior-developer + junior-developer split**
- **21-22 sept**: Safeguards scope creep
- **22 sept**: +parallel-worktree-framework
- **Data**: 33 sessions (ref v7.1)
- **Amélioration mesurée**: -33% marathons vs P3

---

## Extraction Requirements (Phase 1)

### Target Dataset

**Période complète**: Mai-Septembre 2025

**Champs requis** par délégation:
```json
{
  "session_id": "...",
  "timestamp": "2025-09-XX...",
  "agent_type": "developer|solution-architect|...",
  "user_context_before": "message utilisateur",
  "result_full": "résultat complet agent (non tronqué)",
  "input_tokens": 1234,
  "output_tokens": 5678,
  "model_used": "claude-sonnet-4-5",
  "sequence_number": 1,
  "previous_agent": "...",
  "next_agent": "..."
}
```

### Extraction Script

**Utiliser**: `extract_enriched_data.py` (déjà existant)

**Modifications requises**:
- ✓ Inclure tokens data (input/output)
- ✓ Inclure model_used
- ✓ Segmentation temporelle (git-based dates)

### Validation Checklist

- [ ] Sample 3-5 sessions manuellement
- [ ] Vérifier token data présent
- [ ] Vérifier ordre chronologique
- [ ] Vérifier full context (pas truncation)
- [ ] Vérifier classification périodes correcte

---

## Next Steps

### Phase 1: Extraction (1-2 jours)

1. **Adapter extract_enriched_data.py**:
   - Ajouter tokens/model fields
   - Implémenter segmentation git-based

2. **Extraire données complètes**:
   - Mai-juillet: Historical data
   - Août-septembre: Fresh extraction JSONL

3. **Classifier avant agréger**:
   - Marathons: positive/negative/ambiguous
   - Failures: taxonomy (pas juste count)
   - Segmentation temporelle appliquée

4. **Valider extraction**:
   - Sample manual 3-5 sessions
   - Document dans EXTRACTION-REPORT.md

---

## Data Gaps & Anomalies

### ✓ Août "Faible Volume" - RÉSOLU

**État**: Pas un gap, contexte normal
- Vacances utilisateur 4-23 août
- 139 messages utilisables (24-31 août)
- Impact: Adoption initiale peu documentée (acceptable)

### ⚠️ Septembre Début (1-2 Sept)

**Snapshot 2 septembre**: 11 projects
**Snapshot 30 septembre**: 21 projects

**Question**: Données complètes 1-2 sept dans JSONL?
**Validation**: À vérifier lors extraction

---

**Completed**: 2025-09-30
**Ready for**: Assumptions Checklist (Phase 0 next step)