import json
import os
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def load_all_results(directory_path="results/"):
    """Load all results, separated into Round and Step"""
    results = {'Round': {}, 'Step': {}}

    for file in os.listdir(directory_path):
        if file.endswith('.json'):
            file_path = os.path.join(directory_path, file)
            scenario_name = file.replace('.json', '')

            if scenario_name.endswith('Round'):
                game_type = 'Round'
                base_name = scenario_name[:-5]
            elif scenario_name.endswith('Step'):
                game_type = 'Step'
                base_name = scenario_name[:-4]
            else:
                continue

            with open(file_path, 'r') as f:
                data = json.load(f)
                results[game_type][base_name] = data

    return results


def extract_agent_info(scenario_name):
    """
    Extract base agent type and gene version from scenario name
    Examples:
    - SCabSelfPlay -> ('SCab', None)
    - HCabVGHare1 -> ('HCab', None)
    - ECab99SelfPlay -> ('ECab', '99')
    - ECab199VGHare1 -> ('ECab', '199')
    - Allegtr -> ('Allegtr', None)
    """
    # Handle SCab and HCab (no gene versions)
    if scenario_name.startswith('SCab'):
        return 'SCab', None
    if scenario_name.startswith('HCab'):
        return 'HCab', None
    if scenario_name.startswith('Allegatr'):
        return 'Allegatr', None
    if scenario_name.startswith('Allegtr'):
        return 'Allegtr', None

    # Handle ECab with possible gene versions
    if scenario_name.startswith('ECab'):
        remainder = scenario_name[4:]  # Remove 'ECab'

        # Extract gene version (digits after ECab)
        gene_version = ''
        for char in remainder:
            if char.isdigit():
                gene_version += char
            else:
                break

        if gene_version:
            return 'ECab', gene_version
        return 'ECab', None

    print("The scenario name is as follows ", scenario_name)
    return 'Unknown', None


def get_agent_display_name(scenario_name):
    """Get clean display name including gene version"""
    agent_type, gene_version = extract_agent_info(scenario_name)
    if gene_version:
        return f"{agent_type}{gene_version}"
    return agent_type


def extract_agent_type(scenario_name):
    """Extract just the base agent type"""
    agent_type, _ = extract_agent_info(scenario_name)
    return agent_type


def extract_scenario_category(scenario_name):
    """Extract scenario category, handling gene versions correctly"""
    agent_type, gene_version = extract_agent_info(scenario_name)

    if agent_type == 'Unknown':
        return scenario_name

    # Calculate prefix length
    if gene_version:
        prefix = f"{agent_type}{gene_version}"
    else:
        prefix = agent_type

    return scenario_name[len(prefix):]


def get_all_agent_groups(results):
    """
    Get all unique agent groups from the results
    Returns sorted list of display names: ['ECab199', 'HCab', 'SCab']
    """
    agent_groups = set()
    for scenario_name in results.keys():
        agent_groups.add(get_agent_display_name(scenario_name))
    return sorted(agent_groups)


def filter_relevant_scores(scenario_name, score_per_player):
    """Filter scores to only include test agents (not background agents)"""
    category = extract_scenario_category(scenario_name)

    if not score_per_player or not isinstance(score_per_player[0], list):
        return score_per_player

    if 'SelfPlay' in category:
        return score_per_player  # Keep all 3
    elif any(x in category for x in ['VGHare1', 'VGStag1', 'Allegatr1', 'VAllegtr1']):
        return score_per_player[:2]  # Keep first 2 (test agents)
    elif any(x in category for x in ['VGHare2', 'VGStag2', 'Allegatr2', 'VAllegtr2']):
        return score_per_player[:1]  # Keep first 1 (test agent)
    return score_per_player


def get_agent_labels(scenario_name):
    """Get appropriate labels for agents in this scenario"""
    category = extract_scenario_category(scenario_name)
    agent_display = get_agent_display_name(scenario_name)

    if 'SelfPlay' in category:
        return [f'{agent_display}_1', f'{agent_display}_2', f'{agent_display}_3']
    elif 'VGHare1' in category:
        return [f'{agent_display}_1', f'{agent_display}_2', 'GHare']
    elif 'VGHare2' in category:
        return [f'{agent_display}_1', 'GHare']
    elif 'VGStag1' in category:
        return [f'{agent_display}_1', f'{agent_display}_2', 'GStag']
    elif 'VGStag2' in category:
        return [f'{agent_display}_1', 'GStag']
    elif any(x in category for x in ['VAllegtr1', 'Allegatr1']):
        return [f'{agent_display}_1', f'{agent_display}_2', 'Allegatr']
    elif any(x in category for x in ['VAllegtr2', 'Allegatr2']):
        return [f'{agent_display}_1', 'Allegatr']
    return ['Agent 1', 'Agent 2', 'Agent 3']


# ==================== OVERVIEW GRAPHS ====================
def create_overview_reward_distribution(results, game_type, save_dir="graphs/overview/"):
    """OVERVIEW FOLDER: Reward distribution graphs for each agent group"""
    save_dir_game = os.path.join(save_dir, game_type)
    os.makedirs(save_dir_game, exist_ok=True)

    agent_groups = get_all_agent_groups(results)
    colors = ['#e74c3c', '#f39c12', '#2ecc71']  # Red for Nothing, Orange for Hare, Green for Stag

    for agent_display in agent_groups:
        # Filter results for this specific agent group
        agent_results = {name: data for name, data in results.items()
                         if get_agent_display_name(name) == agent_display}

        if not agent_results:
            continue

        scenarios = []
        nothing_avgs = []
        hare_avgs = []
        stag_avgs = []

        for scenario_name, data in agent_results.items():
            category = extract_scenario_category(scenario_name)
            scores = data.get('score_per_player', [])

            if not scores or not isinstance(scores[0], list):
                continue

            filtered_scores = filter_relevant_scores(scenario_name, scores)

            scenarios.append(category)
            nothing_avgs.append(np.mean([player[0] for player in filtered_scores]))
            hare_avgs.append(np.mean([player[1] for player in filtered_scores]))
            stag_avgs.append(np.mean([player[2] for player in filtered_scores]))

        if not scenarios:
            continue

        # Create grouped bar chart with percentages
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

        x = np.arange(len(scenarios))
        width = 0.25

        bars1 = ax1.bar(x - width, nothing_avgs, width, label='Nothing (0 pts)', color=colors[0], alpha=0.8)
        bars2 = ax1.bar(x, hare_avgs, width, label='Hare (1 pt)', color=colors[1], alpha=0.8)
        bars3 = ax1.bar(x + width, stag_avgs, width, label='Stag (2 pts)', color=colors[2], alpha=0.8)

        ax1.set_xlabel('Scenario Type', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Average Score (Test Agents Only)', fontsize=12, fontweight='bold')
        ax1.set_title(f'{agent_display} - {game_type}: Reward Distribution', fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(scenarios, rotation=45, ha='right')
        ax1.legend(loc='upper right')
        ax1.grid(axis='y', alpha=0.3)

        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                if height > 0.01:
                    ax1.text(bar.get_x() + bar.get_width() / 2., height + 0.01,
                             f'{height:.3f}', ha='center', va='bottom', fontsize=8, rotation=90)

        # Stacked percentage
        totals = [n + h + s for n, h, s in zip(nothing_avgs, hare_avgs, stag_avgs)]
        nothing_pct = [n / t * 100 if t > 0 else 0 for n, t in zip(nothing_avgs, totals)]
        hare_pct = [h / t * 100 if t > 0 else 0 for h, t in zip(hare_avgs, totals)]
        stag_pct = [s / t * 100 if t > 0 else 0 for s, t in zip(stag_avgs, totals)]

        ax2.bar(scenarios, nothing_pct, label='Nothing', color=colors[0], alpha=0.8)
        ax2.bar(scenarios, hare_pct, bottom=nothing_pct, label='Hare', color=colors[1], alpha=0.8)
        ax2.bar(scenarios, stag_pct, bottom=[n + h for n, h in zip(nothing_pct, hare_pct)],
                label='Stag', color=colors[2], alpha=0.8)

        ax2.set_xlabel('Scenario Type', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Percentage of Actions', fontsize=12, fontweight='bold')
        ax2.set_title(f'{agent_display} - {game_type}: Action Distribution (%)', fontsize=14, fontweight='bold')
        ax2.set_xticks(range(len(scenarios)))
        ax2.set_xticklabels(scenarios, rotation=45, ha='right')
        ax2.legend(loc='upper right')
        ax2.grid(axis='y', alpha=0.3)
        ax2.set_ylim(0, 100)

        plt.suptitle(f'{agent_display} - {game_type} Games: Complete Analysis', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{save_dir_game}/{agent_display}_reward_distribution.png', dpi=150, bbox_inches='tight')
        plt.close()

        print(f"Created {agent_display} {game_type} overview graph")


# ==================== STAG HUNTING GRAPHS ====================
def create_stag_hunting_comparison(results, game_type, save_dir="graphs/stag_hunting/"):
    """STAG HUNTING FOLDER: Focus on cooperation success (Stag scores)"""
    save_dir_game = os.path.join(save_dir, game_type)
    os.makedirs(save_dir_game, exist_ok=True)

    agent_groups = get_all_agent_groups(results)
    all_scenarios = sorted(set(extract_scenario_category(name) for name in results.keys()))

    # Generate colors for however many agent groups we have
    agent_colors = plt.cm.tab10(np.linspace(0, 1, len(agent_groups)))

    # 1. Heatmap
    matrix = np.zeros((len(agent_groups), len(all_scenarios)))

    for i, agent_display in enumerate(agent_groups):
        for j, scenario in enumerate(all_scenarios):
            for scenario_name, data in results.items():
                if get_agent_display_name(scenario_name) == agent_display and \
                        extract_scenario_category(scenario_name) == scenario:
                    scores = data.get('score_per_player', [])
                    if scores and isinstance(scores[0], list):
                        filtered_scores = filter_relevant_scores(scenario_name, scores)
                        matrix[i, j] = np.mean([player[2] for player in filtered_scores])
                    break

    fig, ax = plt.subplots(figsize=(14, 8))
    im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto', vmin=0, vmax=1)

    for i in range(len(agent_groups)):
        for j in range(len(all_scenarios)):
            text_color = "white" if matrix[i, j] > 0.6 else "black"
            ax.text(j, i, f'{matrix[i, j]:.3f}', ha="center", va="center",
                    color=text_color, fontweight='bold', fontsize=12)

    ax.set_xticks(np.arange(len(all_scenarios)))
    ax.set_yticks(np.arange(len(agent_groups)))
    ax.set_xticklabels(all_scenarios, rotation=45, ha='right')
    ax.set_yticklabels(agent_groups)
    ax.set_xlabel('Scenario Type', fontsize=12, fontweight='bold')
    ax.set_ylabel('Agent Group', fontsize=12, fontweight='bold')
    ax.set_title(f'{game_type} Games: Stag Hunting Success Heatmap', fontsize=14, fontweight='bold')

    cbar = plt.colorbar(im)
    cbar.set_label('Average Stag Score (Test Agents)', rotation=270, labelpad=20)

    plt.tight_layout()
    plt.savefig(f'{save_dir_game}/stag_hunting_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()

    # 2. Direct comparison bar chart
    fig, ax = plt.subplots(figsize=(14, 7))
    x = np.arange(len(all_scenarios))
    width = 0.8 / len(agent_groups)

    for i, agent_display in enumerate(agent_groups):
        stag_scores = []
        for scenario in all_scenarios:
            score_found = 0
            for scenario_name, data in results.items():
                if get_agent_display_name(scenario_name) == agent_display and \
                        extract_scenario_category(scenario_name) == scenario:
                    scores = data.get('score_per_player', [])
                    if scores and isinstance(scores[0], list):
                        filtered_scores = filter_relevant_scores(scenario_name, scores)
                        score_found = np.mean([player[2] for player in filtered_scores])
                    break
            stag_scores.append(score_found)

        offset = (i - (len(agent_groups) - 1) / 2) * width
        bars = ax.bar(x + offset, stag_scores, width, label=agent_display,
                      color=agent_colors[i], alpha=0.8)

        for bar in bars:
            height = bar.get_height()
            if height > 0.01:
                ax.text(bar.get_x() + bar.get_width() / 2., height + 0.01,
                        f'{height:.3f}', ha='center', va='bottom', fontsize=8, rotation=90)

    ax.set_xlabel('Scenario Type', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Stag Score (Test Agents)', fontsize=12, fontweight='bold')
    ax.set_title(f'{game_type} Games: Stag Hunting Success Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(all_scenarios, rotation=45, ha='right')
    ax.legend(loc='upper right')
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(f'{save_dir_game}/stag_hunting_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()

    # 3. Top performers
    fig, ax = plt.subplots(figsize=(12, 6))

    combinations = []
    for scenario_name, data in results.items():
        scores = data.get('score_per_player', [])
        if scores and isinstance(scores[0], list):
            filtered_scores = filter_relevant_scores(scenario_name, scores)
            stag_avg = np.mean([player[2] for player in filtered_scores])
            combinations.append((scenario_name, stag_avg))

    combinations.sort(key=lambda x: x[1], reverse=True)
    top_n = min(5, len(combinations))
    top_combinations = combinations[:top_n]

    names = [f"{get_agent_display_name(name)}\n{extract_scenario_category(name)}"
             for name, _ in top_combinations]
    scores = [score for _, score in top_combinations]

    bars = ax.barh(names, scores, color='#2ecc71', alpha=0.8)
    for bar, score in zip(bars, scores):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                f'{score:.3f}', ha='left', va='center', fontsize=12, fontweight='bold')

    ax.set_xlabel('Average Stag Score', fontsize=12, fontweight='bold')
    ax.set_title(f'{game_type} Games: Top {top_n} Stag Hunters', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 1)
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{save_dir_game}/best_stag_hunters.png', dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Created {game_type} stag hunting graphs")


# ==================== POPULARITY GRAPHS ====================
def create_popularity_graphs(results, game_type, save_dir="graphs/popularity/"):
    """POPULARITY FOLDER: Show how often test agents win vs opponent agents"""
    save_dir_game = os.path.join(save_dir, game_type)
    os.makedirs(save_dir_game, exist_ok=True)

    agent_groups = get_all_agent_groups(results)

    for agent_display in agent_groups:
        agent_results = {name: data for name, data in results.items()
                         if get_agent_display_name(name) == agent_display}

        if not agent_results:
            continue

        # Collect valid data
        scenario_data = []

        for scenario_name, data in agent_results.items():
            category = extract_scenario_category(scenario_name)
            popularity = data.get('popularity_over_time', [])

            if not popularity or len(popularity) < 3:
                continue

            total = sum(popularity) if sum(popularity) > 0 else 1

            if 'SelfPlay' in category:
                test_pop = sum(popularity) / total * 100
                opp_pop = 0
            elif any(x in category for x in ['VGHare1', 'VGStag1', 'VAllegtr1', 'Allegatr1']):
                test_pop = (popularity[0] + popularity[1]) / total * 100
                opp_pop = popularity[2] / total * 100
            elif any(x in category for x in ['VGHare2', 'VGStag2', 'VAllegtr2', 'Allegatr2']):
                test_pop = popularity[0] / total * 100
                opp_pop = (popularity[1] + popularity[2]) / total * 100
            else:
                continue

            scenario_data.append({
                'category': category,
                'test_pop': test_pop,
                'opp_pop': opp_pop
            })

        if not scenario_data:
            continue

        scenarios = [d['category'] for d in scenario_data]
        test_vals = [d['test_pop'] for d in scenario_data]
        opp_vals = [d['opp_pop'] for d in scenario_data]

        fig, ax = plt.subplots(figsize=(14, 8))

        x = np.arange(len(scenarios))
        width = 0.35

        bars1 = ax.bar(x - width / 2, test_vals, width,
                       label=f'{agent_display} (Test Agents)',
                       color='#2ecc71', alpha=0.8, edgecolor='black')

        if any(v > 0 for v in opp_vals):
            bars2 = ax.bar(x + width / 2, opp_vals, width,
                           label='Opponent Agents',
                           color='#e74c3c', alpha=0.8, edgecolor='black')

        ax.set_xlabel('Scenario Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average Popularity (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'{agent_display} - {game_type}: Test Agents vs Opponents Popularity',
                     fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(scenarios, rotation=45, ha='right')
        ax.legend(loc='upper right')
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim(0, 105)

        for bar in bars1:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width() / 2., min(height + 2, 102),
                        f'{height:.1f}%', ha='center', va='bottom',
                        fontsize=9, fontweight='bold')

        if any(v > 0 for v in opp_vals):
            for bar in bars2:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width() / 2., min(height + 2, 102),
                            f'{height:.1f}%', ha='center', va='bottom',
                            fontsize=9, fontweight='bold')

        ax.axhline(y=50, color='black', linestyle='--', alpha=0.3, linewidth=1)

        plt.tight_layout()
        plt.savefig(f'{save_dir_game}/{agent_display}_popularity.png', dpi=150, bbox_inches='tight')
        plt.close()

        print(f"Created {agent_display} {game_type} popularity graph")


# ==================== HARE INTENT GRAPHS ====================
def create_hare_intent_graphs(results, game_type, save_dir="graphs/hare_intent/"):
    """HARE INTENT FOLDER: Show percentage of time agents attempt to hunt hares"""
    save_dir_game = os.path.join(save_dir, game_type)
    os.makedirs(save_dir_game, exist_ok=True)

    agent_groups = get_all_agent_groups(results)

    for agent_display in agent_groups:
        agent_results = {name: data for name, data in results.items()
                         if get_agent_display_name(name) == agent_display}

        if not agent_results:
            continue

        fig, ax = plt.subplots(figsize=(14, 8))

        scenarios = []
        hare_intent_values = []

        for scenario_name, data in agent_results.items():
            category = extract_scenario_category(scenario_name)
            hare_intent = data.get('hare_intent_percent_total', 0)

            scenarios.append(category)
            if hare_intent < 1:
                hare_intent_values.append(hare_intent * 100)
            else:
                hare_intent_values.append(hare_intent)

        colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(scenarios)))
        bars = ax.bar(scenarios, hare_intent_values, color=colors, alpha=0.8, edgecolor='black')

        ax.set_xlabel('Scenario Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Hare Intent (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'{agent_display} - {game_type}: Hare Hunting Intent Percentage',
                     fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(scenarios)))
        ax.set_xticklabels(scenarios, rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3)

        for bar, value in zip(bars, hare_intent_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height + 1,
                    f'{value:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax.axhline(y=50, color='black', linestyle='--', alpha=0.3, linewidth=1)
        ax.text(len(scenarios) - 0.5, 52, 'More hare hunting →', ha='right', fontsize=9, style='italic', alpha=0.7)
        ax.text(len(scenarios) - 0.5, 48, '← Less hare hunting', ha='right', fontsize=9, style='italic', alpha=0.7)

        plt.tight_layout()
        plt.savefig(f'{save_dir_game}/{agent_display}_hare_intent.png', dpi=150, bbox_inches='tight')
        plt.close()

        print(f"Created {agent_display} {game_type} hare intent graph")


# ==================== SCENARIO COMPARISON GRAPHS ====================
def create_scenario_reward_distribution(results, game_type, save_dir="graphs/scenario_comparison/reward_distribution/"):
    """
    For each scenario type, compare reward distribution across all agent groups
    """
    save_dir_game = os.path.join(save_dir, game_type)
    os.makedirs(save_dir_game, exist_ok=True)

    agent_groups = get_all_agent_groups(results)
    all_scenarios = sorted(set(extract_scenario_category(name) for name in results.keys()))

    colors = ['#e74c3c', '#f39c12', '#2ecc71']  # Nothing, Hare, Stag

    for scenario in all_scenarios:
        scenario_data = {}

        for scenario_name, data in results.items():
            if extract_scenario_category(scenario_name) == scenario:
                agent_display = get_agent_display_name(scenario_name)
                scores = data.get('score_per_player', [])

                if scores and isinstance(scores[0], list):
                    filtered_scores = filter_relevant_scores(scenario_name, scores)
                    scenario_data[agent_display] = {
                        'nothing': np.mean([player[0] for player in filtered_scores]),
                        'hare': np.mean([player[1] for player in filtered_scores]),
                        'stag': np.mean([player[2] for player in filtered_scores])
                    }

        if not scenario_data:
            continue

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

        agents_present = sorted(scenario_data.keys())
        x = np.arange(len(agents_present))
        width = 0.25

        nothing_vals = [scenario_data[agent]['nothing'] for agent in agents_present]
        hare_vals = [scenario_data[agent]['hare'] for agent in agents_present]
        stag_vals = [scenario_data[agent]['stag'] for agent in agents_present]

        # Left: Grouped bar chart
        bars1 = ax1.bar(x - width, nothing_vals, width, label='Nothing (0 pts)', color=colors[0], alpha=0.8)
        bars2 = ax1.bar(x, hare_vals, width, label='Hare (1 pt)', color=colors[1], alpha=0.8)
        bars3 = ax1.bar(x + width, stag_vals, width, label='Stag (2 pts)', color=colors[2], alpha=0.8)

        ax1.set_xlabel('Agent Type', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Average Score', fontsize=12, fontweight='bold')
        ax1.set_title(f'{scenario} - {game_type}: Reward Distribution', fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(agents_present, rotation=45, ha='right')
        ax1.legend(loc='upper right')
        ax1.grid(axis='y', alpha=0.3)

        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                if height > 0.01:
                    ax1.text(bar.get_x() + bar.get_width() / 2., height + 0.01,
                             f'{height:.3f}', ha='center', va='bottom', fontsize=8, rotation=90)

        # Right: Stacked percentage
        totals = [n + h + s for n, h, s in zip(nothing_vals, hare_vals, stag_vals)]
        nothing_pct = [n / t * 100 if t > 0 else 0 for n, t in zip(nothing_vals, totals)]
        hare_pct = [h / t * 100 if t > 0 else 0 for h, t in zip(hare_vals, totals)]
        stag_pct = [s / t * 100 if t > 0 else 0 for s, t in zip(stag_vals, totals)]

        ax2.bar(agents_present, nothing_pct, label='Nothing', color=colors[0], alpha=0.8)
        ax2.bar(agents_present, hare_pct, bottom=nothing_pct, label='Hare', color=colors[1], alpha=0.8)
        ax2.bar(agents_present, stag_pct, bottom=[n + h for n, h in zip(nothing_pct, hare_pct)],
                label='Stag', color=colors[2], alpha=0.8)

        ax2.set_xlabel('Agent Type', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Percentage of Actions', fontsize=12, fontweight='bold')
        ax2.set_title(f'{scenario} - {game_type}: Action Distribution (%)', fontsize=14, fontweight='bold')
        ax2.set_xticks(range(len(agents_present)))
        ax2.set_xticklabels(agents_present, rotation=45, ha='right')
        ax2.legend(loc='upper right')
        ax2.grid(axis='y', alpha=0.3)
        ax2.set_ylim(0, 100)

        plt.suptitle(f'{scenario} - {game_type} Games: Agent Comparison', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{save_dir_game}/{scenario}_reward_distribution.png', dpi=150, bbox_inches='tight')
        plt.close()

        print(f"Created {scenario} {game_type} reward distribution comparison")


def create_scenario_hare_intent(results, game_type, save_dir="graphs/scenario_comparison/hare_intent/"):
    """
    For each scenario type, compare hare hunting intent across all agent groups
    """
    save_dir_game = os.path.join(save_dir, game_type)
    os.makedirs(save_dir_game, exist_ok=True)

    agent_groups = get_all_agent_groups(results)
    all_scenarios = sorted(set(extract_scenario_category(name) for name in results.keys()))

    # Generate consistent colors for agent groups
    agent_colors = {}
    color_map = plt.cm.tab10(np.linspace(0, 1, len(agent_groups)))
    for i, agent in enumerate(agent_groups):
        agent_colors[agent] = color_map[i]

    for scenario in all_scenarios:
        scenario_hare_data = {}

        for scenario_name, data in results.items():
            if extract_scenario_category(scenario_name) == scenario:
                agent_display = get_agent_display_name(scenario_name)
                hare_intent = data.get('hare_intent_percent_total', 0)

                if hare_intent < 1:
                    hare_intent = hare_intent * 100

                scenario_hare_data[agent_display] = hare_intent

        if not scenario_hare_data:
            continue

        fig, ax = plt.subplots(figsize=(12, 7))

        agents_present = sorted(scenario_hare_data.keys())
        hare_vals = [scenario_hare_data[agent] for agent in agents_present]

        bar_colors = [agent_colors[agent] for agent in agents_present]
        bars = ax.bar(agents_present, hare_vals, color=bar_colors, alpha=0.8, edgecolor='black')

        ax.set_xlabel('Agent Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Hare Intent (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'{scenario} - {game_type}: Hare Hunting Intent by Agent', fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(agents_present)))
        ax.set_xticklabels(agents_present, rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3)

        for bar, value in zip(bars, hare_vals):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height + 1,
                    f'{value:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax.axhline(y=50, color='black', linestyle='--', alpha=0.3, linewidth=1)
        ax.text(len(agents_present) - 0.5, 52, 'More hare hunting →', ha='right', fontsize=9, style='italic', alpha=0.7)
        ax.text(len(agents_present) - 0.5, 48, '← Less hare hunting', ha='right', fontsize=9, style='italic', alpha=0.7)

        plt.tight_layout()
        plt.savefig(f'{save_dir_game}/{scenario}_hare_intent.png', dpi=150, bbox_inches='tight')
        plt.close()

        print(f"Created {scenario} {game_type} hare intent comparison")


def create_scenario_popularity(results, game_type, save_dir="graphs/scenario_comparison/popularity/"):
    """
    For each scenario type, compare popularity across all agent groups
    """
    save_dir_game = os.path.join(save_dir, game_type)
    os.makedirs(save_dir_game, exist_ok=True)

    agent_groups = get_all_agent_groups(results)
    all_scenarios = sorted(set(extract_scenario_category(name) for name in results.keys()))

    for scenario in all_scenarios:
        # Skip SelfPlay - always 100% test agents
        if 'SelfPlay' in scenario:
            continue

        scenario_pop_data = {}

        for scenario_name, data in results.items():
            if extract_scenario_category(scenario_name) == scenario:
                agent_display = get_agent_display_name(scenario_name)
                popularity = data.get('popularity_over_time', [])

                if popularity and len(popularity) >= 3:
                    total = sum(popularity) if sum(popularity) > 0 else 1

                    if any(x in scenario for x in ['1']):
                        test_pop = (popularity[0] + popularity[1]) / total * 100
                        opp_pop = popularity[2] / total * 100
                    else:  # '2' scenarios
                        test_pop = popularity[0] / total * 100
                        opp_pop = (popularity[1] + popularity[2]) / total * 100

                    scenario_pop_data[agent_display] = {
                        'test_pop': test_pop,
                        'opp_pop': opp_pop
                    }

        if not scenario_pop_data:
            continue

        fig, ax = plt.subplots(figsize=(12, 7))

        agents_present = sorted(scenario_pop_data.keys())
        x = np.arange(len(agents_present))
        width = 0.35

        test_vals = [scenario_pop_data[agent]['test_pop'] for agent in agents_present]
        opp_vals = [scenario_pop_data[agent]['opp_pop'] for agent in agents_present]

        bars1 = ax.bar(x - width / 2, test_vals, width, label='Test Agents',
                       color='#2ecc71', alpha=0.8, edgecolor='black')
        bars2 = ax.bar(x + width / 2, opp_vals, width, label='Opponent Agents',
                       color='#e74c3c', alpha=0.8, edgecolor='black')

        ax.set_xlabel('Agent Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average Popularity (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'{scenario} - {game_type}: Agent Popularity Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(agents_present, rotation=45, ha='right')
        ax.legend(loc='upper right')
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim(0, 105)
        ax.axhline(y=50, color='black', linestyle='--', alpha=0.3, linewidth=1)

        for bar in bars1:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width() / 2., min(height + 2, 102),
                        f'{height:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')

        for bar in bars2:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width() / 2., min(height + 2, 102),
                        f'{height:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')

        plt.tight_layout()
        plt.savefig(f'{save_dir_game}/{scenario}_popularity.png', dpi=150, bbox_inches='tight')
        plt.close()

        print(f"Created {scenario} {game_type} popularity comparison")


def create_scenario_stag_hunting(results, game_type, save_dir="graphs/scenario_comparison/stag_hunting/"):
    """
    Overview stag hunting comparison across all scenarios and agents
    """
    save_dir_game = os.path.join(save_dir, game_type)
    os.makedirs(save_dir_game, exist_ok=True)

    agent_groups = get_all_agent_groups(results)
    all_scenarios = sorted(set(extract_scenario_category(name) for name in results.keys()))

    agent_colors = {}
    color_map = plt.cm.tab10(np.linspace(0, 1, len(agent_groups)))
    for i, agent in enumerate(agent_groups):
        agent_colors[agent] = color_map[i]

    fig, ax = plt.subplots(figsize=(12, 7))

    x = np.arange(len(all_scenarios))
    width = 0.8 / len(agent_groups)

    for i, agent_display in enumerate(agent_groups):
        stag_scores = []
        for scenario in all_scenarios:
            score_found = 0
            for scenario_name, data in results.items():
                if get_agent_display_name(scenario_name) == agent_display and \
                        extract_scenario_category(scenario_name) == scenario:
                    scores = data.get('score_per_player', [])
                    if scores and isinstance(scores[0], list):
                        filtered_scores = filter_relevant_scores(scenario_name, scores)
                        score_found = np.mean([player[2] for player in filtered_scores])
                    break
            stag_scores.append(score_found)

        offset = (i - (len(agent_groups) - 1) / 2) * width
        bars = ax.bar(x + offset, stag_scores, width, label=agent_display,
                      color=agent_colors[agent_display], alpha=0.8)

        for bar in bars:
            height = bar.get_height()
            if height > 0.01:
                ax.text(bar.get_x() + bar.get_width() / 2., height + 0.01,
                        f'{height:.3f}', ha='center', va='bottom', fontsize=7, rotation=90)

    ax.set_xlabel('Scenario Type', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Stag Score (Cooperation)', fontsize=12, fontweight='bold')
    ax.set_title(f'{game_type} Games: Stag Hunting by Scenario', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(all_scenarios, rotation=45, ha='right')
    ax.legend(loc='upper right')
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(f'{save_dir_game}/stag_hunting_by_scenario.png', dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Created {game_type} scenario stag hunting overview")

# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    all_results = load_all_results()

    print(f"Loaded {len(all_results['Round'])} Round results and {len(all_results['Step'])} Step results\n")

    # Show detected agent groups
    all_agents = set()
    for game_type in ['Round', 'Step']:
        all_agents.update(get_all_agent_groups(all_results[game_type]))
    print(f"Detected agent groups: {sorted(all_agents)}\n")

    # OVERVIEW GRAPHS
    print("=" * 60)
    print("CREATING OVERVIEW REWARD DISTRIBUTION GRAPHS")
    print("=" * 60)
    create_overview_reward_distribution(all_results['Round'], 'Round')
    create_overview_reward_distribution(all_results['Step'], 'Step')

    # STAG HUNTING GRAPHS
    print("\n" + "=" * 60)
    print("CREATING STAG HUNTING ANALYSIS GRAPHS")
    print("=" * 60)
    create_stag_hunting_comparison(all_results['Round'], 'Round')
    create_stag_hunting_comparison(all_results['Step'], 'Step')

    # POPULARITY GRAPHS
    print("\n" + "=" * 60)
    print("CREATING POPULARITY GRAPHS")
    print("=" * 60)
    create_popularity_graphs(all_results['Round'], 'Round')
    create_popularity_graphs(all_results['Step'], 'Step')

    # HARE INTENT GRAPHS
    print("\n" + "=" * 60)
    print("CREATING HARE INTENT GRAPHS")
    print("=" * 60)
    create_hare_intent_graphs(all_results['Round'], 'Round')
    create_hare_intent_graphs(all_results['Step'], 'Step')

    # SCENARIO COMPARISON GRAPHS (Column View)
    print("\n" + "=" * 60)
    print("CREATING SCENARIO COMPARISON GRAPHS (Column View)")
    print("=" * 60)
    for game_type in ['Round', 'Step']:
        results = all_results[game_type]
        create_scenario_reward_distribution(results, game_type)
        create_scenario_hare_intent(results, game_type)
        create_scenario_popularity(results, game_type)
        create_scenario_stag_hunting(results, game_type)

    print("\n" + "=" * 60)
    print("✅ ALL GRAPHS GENERATED SUCCESSFULLY!")
    print("=" * 60)