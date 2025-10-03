# Plan Méthodologique - Analyse du Système Multi-Agents

## Objectif de l'Analyse

Comprendre le **système de délégation multi-agents** de Claude Code pour identifier ce qui empêche les sessions "hands-off" (sans intervention humaine) et améliorer l'efficacité globale du système.

**Focus**: Le système lui-même, pas le comportement utilisateur.

## Méthodologie d'Analyse

### Framework ORID (Arrêt avant Décision)

L'analyse suit le framework ORID mais s'arrête avant la phase de décision:

1. **Observations (O)**: Faits mesurables et patterns observés dans les données
2. **Réactions (R)**: Interprétations, tensions, surprises
3. **Insights (I)**: Compréhension profonde, causes racines (5 Whys)
4. ~~**Décision (D)**~~: Non inclus - les décisions appartiennent à l'utilisateur

### Structure de Restitution

Chaque dimension du système (routage, autonomie, coordination, efficacité) sera analysée selon:

- **✓ Positif**: Ce qui fonctionne bien
- **✗ Négatif**: Ce qui dysfonctionne clairement
- **≈ Ambivalent/Ambigu**: Situations complexes sans jugement simple
- **? Mystères**: Phénomènes inexpliqués nécessitant investigation

### Méthode des 5 Whys

Pour chaque dysfonctionnement majeur, application systématique:

1. **Pourquoi 1**: Symptôme observable
2. **Pourquoi 2**: Cause immédiate
3. **Pourquoi 3**: Cause intermédiaire
4. **Pourquoi 4**: Cause structurelle
5. **Pourquoi 5**: Cause racine systémique

## Dimensions d'Analyse

### 1. Routage Agent → Sous-Agent

**Questions**:
- Le general agent choisit-il le bon sous-agent?
- Quels sont les mauvais routages fréquents?
- Y a-t-il des sous-agents sous-utilisés/sur-utilisés?

**Métriques**:
- Distribution des appels par agent
- Taux de succès par agent (révèle les erreurs de routage)
- Patterns de "mauvais choix" dans les échecs

### 2. Autonomie des Sous-Agents

**Questions**:
- Les sous-agents résolvent-ils seuls ou nécessitent des itérations?
- Quels agents sont les plus autonomes?
- Qu'est-ce qui déclenche les échecs?

**Métriques**:
- Taux de succès global: 82.6%
- Taux de succès par agent
- Types d'échecs par agent

### 3. Coordination Multi-Agents

**Questions**:
- Comment les agents se coordonnent-ils sur des tâches complexes?
- Y a-t-il des patterns de délégations successives?
- Quels sont les coûts de coordination?

**Métriques**:
- Sessions "heavy" (>20 délégations)
- Séquences de délégations agent → agent
- Temps entre délégations

### 4. Efficacité Token et Temps

**Questions**:
- Quel est le coût réel en tokens par type de tâche?
- Y a-t-il du gaspillage?
- Quels agents sont les plus efficaces?

**Métriques**:
- Total: 491,929 tokens
- Coût moyen par agent
- Ratio tokens/valeur produite

### 5. Effets Long-Terme

**Nouveau focus** sur la qualité dans le temps:

**Questions**:
- Les délégations à l'agent developer conduisent-elles à:
  - Du code de qualité?
  - De l'over-engineering?
  - Des bugs découverts plus tard?
  - Du travail inachevé?
- Les refactorings suggérés par architecture-reviewer sont-ils suivis?
- Y a-t-il une "dette de coordination" qui s'accumule?

**Méthode**:
- Analyse temporelle: suivre les sessions sur plusieurs jours/semaines
- Identifier les corrections post-délégation
- Mesurer le "rework" (re-faire ce qui a été délégué)
- Patterns de qualité vs quantité

## Contexte Temporel Critique

### Évolution des Agents en Septembre 2025

**IMPORTANT**: L'écosystème des agents a évolué significativement pendant la période analysée. Cette évolution peut expliquer certains patterns observés.

**Timeline des changements majeurs**:

- **03 sept**: Ajout `solution-architect` et `project-framer` (nouveaux agents de conception)
- **12 sept**: Politique de délégation obligatoire (changement comportemental)
- **15 sept**: Ajout `content-developer` (nouveau domaine: copywriting)
- **20 sept**: Ajout `refactoring-specialist` (spécialisation du developer)
- **21 sept 16h24**: **RESTRUCTURATION MAJEURE**
  - `developer` renommé en `senior-developer`
  - Création `junior-developer` (Haiku, tâches simples)
  - Nouveau workflow "speed-first"
- **22 sept**: Safeguards anti-scope-creep pour `integration-specialist`

**Implication pour l'analyse**:
- Les données pré-21 septembre utilisent `developer` (agent générique)
- Les données post-21 septembre utilisent `senior-developer` + `junior-developer` (spécialisés)
- Les métriques de "developer" mélangent deux configurations différentes du système

**Hypothèse à valider**:
- Les sessions marathon pré-21 sept pourraient être causées par l'absence de `junior-developer`
- Les interruptions fréquentes pourraient diminuer post-restructuration
- Le taux de succès "developer" pourrait être artificiellement bas (mixing deux agents différents)

## Ce Qui a Déjà été Extrait

### Données Disponibles

- **142 sessions** avec délégations (période: septembre 2025)
- **1250 délégations** au total
- Token costs complets (input, output, cache_read)
- Success/failure pour 97.9% des délégations
- **ATTENTION**: Données couvrent une période de changements architecturaux majeurs

### Métriques Système Calculées

**Autonomie**:
- 82.6% succès
- 15.4% échecs
- 2.1% inconnus (limites techniques d'extraction)

**Par Agent** (top 5 par volume):
1. developer: 371 calls, 81.5% success, 154,914 tokens
2. backlog-manager: 167 calls, 81.0% success, 62,501 tokens
3. git-workflow-manager: 167 calls, 91.0% success, 53,552 tokens
4. solution-architect: 109 calls, 84.4% success, 39,225 tokens
5. architecture-reviewer: 82 calls, 90.1% success, 31,604 tokens

**Friction Points**:
- 192 échecs documentés
- 12 sessions "marathons" (>20 délégations)
- Exemples d'échecs typiques extraits

## Prochaines Étapes

1. **Analyse des 5 Whys** sur les échecs les plus fréquents
2. **Pattern mining** dans les sessions heavy
3. **Analyse long-terme**: suivre des sessions multi-jours
4. **Production observations-vN.md** avec structure ORID

## Principe Directeur

> "On ne se contente pas de données partielles, on réfléchit en profondeur."

Chaque observation doit être:
- Mesurée avec données complètes
- Contextualisée (pourquoi, dans quelles conditions)
- Analysée pour causes racines
- Reliée à l'objectif "hands-off"