# Rétrospective Délégation - Scratchpad

## Exploration Initiale

### Statistiques du Corpus
- 236 conversations (3 derniers mois)
- 482M de données totales
- 1446 appels d'agents au total

### Répartition des Agents (Top)
1. developer: 371 appels (25.6%)
2. git-workflow-manager: 167 appels (11.5%)
3. backlog-manager: 167 appels (11.5%)
4. solution-architect: 109 appels (7.5%)
5. architecture-reviewer: 82 appels (5.7%)

Total top 5: 896/1446 (62%)

### Questions à Explorer
- Comment l'agent principal choisit-il quel agent déléguer?
- Quelle est la structure des prompts efficaces vs problématiques?
- Y a-t-il des patterns de délégation en chaîne?
- Comment l'usage a-t-il évolué dans le temps?

### Hypothèses de Travail
- Les prompts courts manquent de contexte
- Certains agents sont mal utilisés pour certaines tâches
- Il y a une évolution dans la sophistication des délégations
- Les échecs sont souvent dus à des prompts ambigus

## Format des Données Source
Fichiers JSONL avec structure:
```json
{
  "type": "assistant",
  "message": {
    "role": "assistant",
    "content": "[{\"type\":\"tool_use\",\"name\":\"Task\",\"input\":{\"subagent_type\":\"developer\",...}}]"
  },
  "timestamp": "2025-09-15T21:41:31.866Z",
  "sessionId": "...",
  "cwd": "/path/to/project"
}
```

## Stratégie d'Extraction
1. Identifier tous les messages avec tool_use Task
2. Extraire le contexte (3 messages utilisateur précédents)
3. Capturer la délégation complète
4. Suivre la conversation post-délégation (feedback, corrections)

## Notes de Développement
- Utiliser jq pour parsing JSON
- grep pour identifier les délégations
- Timestamps pour analyse chronologique
- sessionId pour regrouper les conversations