#!/usr/bin/env python3
"""
Generate comprehensive routing patterns analysis report.
"""

import json
from common.config import ROUTING_PATTERNS_FILE, ROUTING_QUALITY_FILE, GOOD_ROUTING_FILE, PROJECT_ROOT

def load_all_data():
    """Load all analysis data."""
    with open(ROUTING_PATTERNS_FILE, 'r') as f:
        routing = json.load(f)

    with open(ROUTING_QUALITY_FILE, 'r') as f:
        quality = json.load(f)

    with open(GOOD_ROUTING_FILE, 'r') as f:
        good = json.load(f)

    return routing, quality, good

def generate_report():
    """Generate comprehensive routing analysis report."""
    
    routing, quality, good = load_all_data()
    
    report = []
    
    # Header
    report.append("# Routing Patterns Analysis - Septembre 2025")
    report.append("")
    report.append("**Objectif**: Comprendre comment le general agent choisit les sous-agents et identifier les patterns de routage optimaux et sous-optimaux.")
    report.append("")
    report.append("**Méthodologie**: Analyse sémantique des prompts et descriptions de tâches avec segmentation temporelle stricte (P2, P3, P4).")
    report.append("")
    report.append("---")
    report.append("")
    
    # Periods analysis
    periods = {
        'P2': ('Période 2 (3-11 sept)', 'Conception Added', '+solution-architect, +project-framer'),
        'P3': ('Période 3 (12-20 sept)', 'Mandatory Delegation', 'Politique obligatoire, +content-developer, +refactoring-specialist'),
        'P4': ('Période 4 (21-30 sept)', 'Post-Restructuration', 'senior-developer + junior-developer split, safeguards scope creep')
    }
    
    for period_key, (title, name, config) in periods.items():
        report.append(f"## {title}: {name}")
        report.append("")
        report.append(f"**Configuration**: {config}")
        report.append("")
        
        # Get data for this period
        period_routing = routing['periods'][period_key]
        period_quality = quality['periods'][period_key]
        period_good = good['periods'][period_key]
        
        # Overview stats
        total = period_quality['total_delegations']
        misrouted = period_quality['misrouted_count']
        good_count = period_good['good_routing_count']
        
        report.append(f"**Volume**: {total} délégations")
        report.append("")
        report.append(f"**Distribution agents**:")
        for agent, count in period_routing['analysis']['top_agents']:
            pct = (count / total) * 100
            report.append(f"- {agent}: {count} ({pct:.1f}%)")
        report.append("")
        
        # Good routing patterns
        report.append("### ✓ Bons Routages")
        report.append("")
        report.append(f"**{good_count} exemples identifiés** de routage approprié.")
        report.append("")
        
        # Top 3 good patterns
        sorted_patterns = sorted(period_good['patterns'].items(), key=lambda x: x[1]['count'], reverse=True)
        for pattern, data in sorted_patterns[:3]:
            report.append(f"#### {pattern}")
            report.append("")
            report.append(f"**Volume**: {data['count']} délégations")
            report.append("")
            report.append(f"**Exemples**:")
            report.append("")
            for i, ex in enumerate(data['examples'][:2], 1):
                report.append(f"{i}. **Tâche**: {ex['task_description']}")
                report.append(f"   - **Prompt**: \"{ex['prompt_preview'][:150]}...\"")
                report.append(f"   - **Raison**: {ex['reason']}")
                report.append("")
        
        # Bad routing patterns
        report.append("### ✗ Mauvais Routages")
        report.append("")
        report.append(f"**{misrouted} cas identifiés** de routage sous-optimal.")
        report.append("")
        
        if misrouted > 0:
            # Group misrouted by type
            misrouted_by_type = {}
            for ex in period_quality['misrouted_examples']:
                issue = ex['reason']
                if issue not in misrouted_by_type:
                    misrouted_by_type[issue] = []
                misrouted_by_type[issue].append(ex)
            
            for issue, examples in sorted(misrouted_by_type.items(), key=lambda x: len(x[1]), reverse=True):
                report.append(f"#### {issue}")
                report.append("")
                report.append(f"**Volume**: {len([e for e in period_quality['misrouted_examples'] if e['reason'] == issue])} cas")
                report.append("")
                report.append("**Exemples**:")
                report.append("")
                for i, ex in enumerate(examples[:2], 1):
                    report.append(f"{i}. **Agent choisi**: {ex['agent_chosen']} → **Devrait être**: {ex['agent_should_be']}")
                    report.append(f"   - **Tâche**: {ex['task_description']}")
                    report.append(f"   - **Prompt**: \"{ex['prompt_preview'][:150]}...\"")
                    report.append("")
        
        # Special analysis for P3 developer explosion
        if period_key == 'P3':
            report.append("### ≈ Analyse: Explosion de `developer` (344 calls)")
            report.append("")
            report.append("**Breakdown par catégorie**:")
            report.append("")
            for cat, count in sorted(period_quality['developer_explosion'].items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    pct = (count / 344) * 100
                    report.append(f"- **{cat.title()}**: {count} ({pct:.1f}%)")
            report.append("")
            report.append("**Observation**: 77.9% des appels à `developer` sont pour des tâches de testing. Cela suggère:")
            report.append("1. Testing est légitimement une tâche de developer")
            report.append("2. Pas de spécialiste testing disponible → routage vers généraliste")
            report.append("3. Le volume élevé reflète l'adoption de TDD pendant cette période")
            report.append("")
            report.append("**Mauvais routage**: Les 13.1% d'implémentation et 6.1% debugging incluent probablement des cas qui auraient dû aller vers:")
            report.append("- `refactoring-specialist` (pour refactoring)")
            report.append("- `solution-architect` (pour questions d'architecture)")
            report.append("")
        
        # Underutilized agents
        if period_quality.get('underutilized_agents'):
            report.append("### ? Agents Sous-Utilisés")
            report.append("")
            for agent_info in period_quality['underutilized_agents']:
                agent = agent_info['agent']
                count = agent_info['count']
                pct = agent_info['percentage']
                report.append(f"- **{agent}**: {count} calls ({pct:.1f}%)")
            report.append("")
            
            # Special analysis for junior-developer in P4
            if period_key == 'P4' and any(a['agent'] == 'junior-developer' for a in period_quality['underutilized_agents']):
                report.append("**Analyse `junior-developer`**: Disponible depuis restructuration 21 sept, mais seulement 4 calls (1.3%).")
                report.append("")
                report.append("**Hypothèses**:")
                report.append("1. **Description peu claire**: Le general agent ne comprend pas quand utiliser junior vs senior")
                report.append("2. **Prompts pas adaptés**: Les prompts utilisateur ne signalent pas \"tâche simple\"")
                report.append("3. **Biais vers senior**: Par défaut, routage vers senior-developer par sécurité")
                report.append("")
                report.append("**Validation**: 2 des 11 cas de mauvais routage en P4 sont senior-developer → junior-developer.")
                report.append("")
            
            # content-developer never used
            if any(a['agent'] == 'content-developer' and a['count'] == 0 for a in period_quality['underutilized_agents']):
                report.append(f"**Analyse `content-developer`**: **0 calls** en {title}.")
                report.append("")
                report.append("**Hypothèses**:")
                report.append("1. **Pas de tâches de contenu pur** pendant cette période")
                report.append("2. **Routage vers developer**: Tâches de documentation/contenu vont vers developer générique")
                report.append("3. **Description ambiguë**: Le general agent ne distingue pas contenu vs code documentation")
                report.append("")
        
        report.append("---")
        report.append("")
    
    # Cross-period synthesis
    report.append("## Synthèse Cross-Période")
    report.append("")
    
    report.append("### Améliorations Mesurées (P3 → P4)")
    report.append("")
    report.append("**1. Réduction des mauvais routages**:")
    report.append(f"- P3: {quality['periods']['P3']['misrouted_count']} cas ({quality['periods']['P3']['misrouted_count']/quality['periods']['P3']['total_delegations']*100:.1f}%)")
    report.append(f"- P4: {quality['periods']['P4']['misrouted_count']} cas ({quality['periods']['P4']['misrouted_count']/quality['periods']['P4']['total_delegations']*100:.1f}%)")
    report.append("")
    report.append("**2. Meilleure utilisation des spécialistes**:")
    p3_refactor = routing['periods']['P3']['analysis']['agent_distribution'].get('refactoring-specialist', 0)
    p4_refactor = routing['periods']['P4']['analysis']['agent_distribution'].get('refactoring-specialist', 0)
    p3_total = quality['periods']['P3']['total_delegations']
    p4_total = quality['periods']['P4']['total_delegations']
    report.append(f"- `refactoring-specialist`: P3 {p3_refactor} ({p3_refactor/p3_total*100:.1f}%) → P4 {p4_refactor} ({p4_refactor/p4_total*100:.1f}%)")
    report.append("")
    report.append("**3. Introduction hiérarchie developer**:")
    report.append("- `senior-developer` adopté (70 calls, 22.8% en P4)")
    report.append("- `junior-developer` sous-utilisé (4 calls, 1.3% en P4)")
    report.append("")
    
    report.append("### Blocages Persistants")
    report.append("")
    report.append("**1. Routage par défaut vers généraliste**:")
    report.append("- P2: `developer` 11.9%")
    report.append("- P3: `developer` 40.1% (explosion)")
    report.append("- P4: `senior-developer` 22.8%")
    report.append("")
    report.append("**Cause**: Lorsque le general agent hésite, il route vers le developer généraliste plutôt que vers un spécialiste.")
    report.append("")
    report.append("**2. Spécialistes jamais utilisés**:")
    report.append("- `content-developer`: 0 calls en P3 ET P4")
    report.append("- `project-framer`: <1% en P3 et P4 (utilisé seulement en P2)")
    report.append("")
    report.append("**Cause**: Descriptions d'agents pas assez claires OU tâches correspondantes absentes.")
    report.append("")
    report.append("**3. Overhead `backlog-manager`**:")
    report.append("- P2: 25.8% (2e position)")
    report.append("- P3: 10.0% (3e position)")
    report.append("- P4: 14.7% (2e position)")
    report.append("")
    report.append("**Question**: Est-ce légitime ou overhead? Backlog-manager toujours dans le top 3.")
    report.append("")
    
    report.append("### Patterns de Routage Réussis à Préserver")
    report.append("")
    report.append("**1. Git → git-workflow-manager** (153 calls en P3):")
    report.append("- Pattern le plus fort et le plus clair")
    report.append("- Aucun cas de mauvais routage détecté")
    report.append("")
    report.append("**2. Architecture → solution-architect** (présent dans toutes périodes):")
    report.append("- P2: 13.9%, P3: 7.4%, P4: 10.1%")
    report.append("- Routage approprié pour questions de design/architecture")
    report.append("")
    report.append("**3. Refactoring → refactoring-specialist** (P3-P4):")
    report.append("- Adoption progressive: P3 1.3% → P4 10.7%")
    report.append("- Amélioration claire post-restructuration")
    report.append("")
    
    report.append("---")
    report.append("")
    
    # Current blockers
    report.append("## Ce Qui Bloque le \"Hands-Off\" Aujourd'hui (P4)")
    report.append("")
    report.append("### 1. junior-developer Pas Adopté")
    report.append("")
    report.append("**Impact**: Tâches simples vont vers senior-developer, gaspillage de ressources.")
    report.append("")
    report.append("**Exemples concrets** (P4):")
    for i, ex in enumerate(quality['periods']['P4']['misrouted_examples'][:2], 1):
        if ex['agent_should_be'] == 'junior-developer':
            report.append(f"{i}. **{ex['task_description']}**")
            report.append(f"   - Routé vers: {ex['agent_chosen']}")
            report.append(f"   - Devrait être: junior-developer")
            report.append(f"   - Prompt: \"{ex['prompt_preview'][:150]}...\"")
            report.append("")
    
    report.append("**Actions**:")
    report.append("1. Clarifier description de `junior-developer` (quelles tâches?)")
    report.append("2. Ajouter exemples explicites de tâches junior vs senior")
    report.append("3. Encourager utilisateur à signaler \"tâche simple\" dans prompts")
    report.append("")
    
    report.append("### 2. Routage par Défaut Vers Généraliste")
    report.append("")
    report.append("**Impact**: Spécialistes sous-utilisés, surcharge des généralistes.")
    report.append("")
    report.append(f"**P4**: 11 cas de mauvais routage identifiés ({quality['periods']['P4']['misrouted_count']/quality['periods']['P4']['total_delegations']*100:.1f}% des délégations)")
    report.append("")
    report.append("**Actions**:")
    report.append("1. Améliorer descriptions d'agents (plus explicites sur leurs domaines)")
    report.append("2. Ajouter exemples de tâches dans descriptions")
    report.append("3. Créer guide de routage pour le general agent")
    report.append("")
    
    report.append("### 3. Agents Fantômes (content-developer, project-framer)")
    report.append("")
    report.append("**Impact**: Agents présents mais jamais utilisés → complexité inutile.")
    report.append("")
    report.append("**Actions**:")
    report.append("1. **Option A**: Supprimer agents inutilisés")
    report.append("2. **Option B**: Clarifier leurs use cases + communiquer à utilisateur")
    report.append("3. **Option C**: Analyser pourquoi pas de tâches correspondantes")
    report.append("")
    
    report.append("---")
    report.append("")
    
    # Methodology notes
    report.append("## Notes Méthodologiques")
    report.append("")
    report.append("### Détection de Mauvais Routage")
    report.append("")
    report.append("**Heuristiques utilisées**:")
    report.append("- Mots-clés dans prompt/description vs agent choisi")
    report.append("- Architecture/design → solution-architect")
    report.append("- Refactoring → refactoring-specialist")
    report.append("- Git operations → git-workflow-manager")
    report.append("- Simple tasks → junior-developer")
    report.append("- Performance → performance-optimizer")
    report.append("")
    report.append("**Limites**:")
    report.append("1. **Faux négatifs**: Mauvais routages sans mots-clés évidents non détectés")
    report.append("2. **Faux positifs**: Certains cas flaggés peuvent être légitimes (ex: developer pour implémenter après architecture)")
    report.append("3. **Context partiel**: Analyse basée sur prompt/description, sans historique complet de session")
    report.append("")
    report.append("### Détection de Bon Routage")
    report.append("")
    report.append("**Critères**:")
    report.append("- Alignement mots-clés tâche ↔ spécialité agent")
    report.append("- Utilisation cohérente de spécialistes pour leurs domaines")
    report.append("")
    report.append("**Limite**: Bon routage ne garantit pas succès de la tâche (dépend de la qualité d'exécution de l'agent).")
    report.append("")
    
    return "\n".join(report)

def main():
    report_content = generate_report()
    
    output_path = PROJECT_ROOT / 'routage-patterns-analysis.md'
    with open(output_path, 'w') as f:
        f.write(report_content)
    
    print(f"Report generated: {output_path}")
    print(f"Total length: {len(report_content)} characters")

if __name__ == '__main__':
    main()
