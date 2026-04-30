import json
import os
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def load_all_results(directory_path="results/"):
    # lets load all the results, separated into two dfs: Round and Step, to make sure we can process those separately.
    results = {'Round': {}, 'Step': {}}

    # for all the files in the directory.
    for file in os.listdir(directory_path):
        if file.endswith('.json'):
            file_path = os.path.join(directory_path, file)
            scenario_name = file.replace('.json', '')

            # determine if its round or step.
            if scenario_name.endswith('Round'):
                game_type = 'Round'
                base_name = scenario_name[:-5]  # we don't want this tag post sorting.
            elif scenario_name.endswith('Step'):
                game_type = 'Step'
                base_name = scenario_name[:-4]  # ditto.
            else:
                continue

            with open(file_path, 'r') as f:
                data = json.load(f)
                results[game_type][base_name] = data

    return results


def extract_agent_type(scenario_name):
    # take the scenario, and return the base agent that we are working with.
    if scenario_name.startswith('SCab'):
        return 'SCab'
    elif scenario_name.startswith('HCab'):
        return 'HCab'
    elif scenario_name.startswith('ECab'):
        return 'ECab'
    return 'Unknown'


def extract_scenario_category(scenario_name):
    # take the scenario and remove the base agnet, for filtering purposes.
    if scenario_name.startswith('SCab'):
        return scenario_name[4:]  # Remove 'SCab'
    elif scenario_name.startswith('HCab'):
        return scenario_name[4:]  # Remove 'HCab'
    elif scenario_name.startswith('ECab'):
        return scenario_name[4:]  # Remove 'ECab'
    return scenario_name


# IMPORTANT IMPORTANT IMPORTANT: FILTER SCORES FOR ONLY TEST AGENTS, NOT BACKGROUND AGENTS.
def filter_relevant_scores(scenario_name, score_per_player):
    # WE ONLY WANT SCORES FROM TEST AGENTS, NOT SCENARIO AGENTS. FILTER.
    category = extract_scenario_category(scenario_name)

    if not score_per_player or not isinstance(score_per_player[0], list):
        return score_per_player

    if 'SelfPlay' in category:
        return score_per_player  # Keep all 3
    elif any(x in category for x in ['VGHare1', 'VGStag1', 'Allegtr1']):
        return score_per_player[:2]  # Keep first 2 (test agents)
    elif any(x in category for x in ['VGHare2', 'VGStag2', 'Allegtr2']):
        return score_per_player[:1]  # Keep first 1 (test agent)
    return score_per_player


def get_agent_labels(scenario_name):
    # match the scenario to teh agent list that we want.
    category = extract_scenario_category(scenario_name)
    agent_type = extract_agent_type(scenario_name)

    if 'SelfPlay' in category:
        return [f'{agent_type}_1', f'{agent_type}_2', f'{agent_type}_3']
    elif 'VGHare1' in category:
        return [f'{agent_type}_1', f'{agent_type}_2', 'GHare']
    elif 'VGHare2' in category:
        return [f'{agent_type}_1', 'GHare']
    elif 'VGStag1' in category:
        return [f'{agent_type}_1', f'{agent_type}_2', 'GStag']
    elif 'VGStag2' in category:
        return [f'{agent_type}_1', 'GStag']
    elif 'VAllegtr1' in category:
        return [f'{agent_type}_1', f'{agent_type}_2', 'Allegatr']
    elif 'VAllegtr2' in category:
        return [f'{agent_type}_1', 'Allegatr']
    return ['Agent 1', 'Agent 2', 'Agent 3']


# ==================== OVERVIEW GRAPHS ====================
def create_overview_reward_distribution(results, game_type, save_dir="graphs/overview/"):
    """OVERVIEW FOLDER: ECab, HCab, SCab reward distribution graphs"""
    save_dir_game = os.path.join(save_dir, game_type)
    os.makedirs(save_dir_game, exist_ok=True)

    agent_types = ["SCab", "HCab", "ECab"]
    colors = ['#e74c3c', '#f39c12', '#2ecc71']  # Red for Nothing, Orange for Hare, Green for Stag

    for agent_type in agent_types: # grab the agent results filtered by agent type.
        agent_results = {name: data for name, data in results.items()
                         if extract_agent_type(name) == agent_type}

        if not agent_results:
            continue

        # init stuff.
        scenarios = []
        nothing_avgs = []
        hare_avgs = []
        stag_avgs = []

        # grab all the scores from all the scenarios by agent.
        for scenario_name, data in agent_results.items():
            category = extract_scenario_category(scenario_name)
            scores = data.get('score_per_player', [])

            if not scores or not isinstance(scores[0], list): # error handling IG.
                continue

            # FILTER ONLY THE SCORES THAT WE WANT -- REMOVE BACKGROUND AGENTS
            filtered_scores = filter_relevant_scores(scenario_name, scores)

            # append all the stuff to the lists.
            scenarios.append(category)
            nothing_avgs.append(np.mean([player[0] for player in filtered_scores]))
            hare_avgs.append(np.mean([player[1] for player in filtered_scores]))
            stag_avgs.append(np.mean([player[2] for player in filtered_scores]))

        if not scenarios:
            continue

        # create a grouped bar chart with the percentages. I hate writing these things.
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

        x = np.arange(len(scenarios))
        width = 0.25

        bars1 = ax1.bar(x - width, nothing_avgs, width, label='Nothing (0 pts)', color=colors[0], alpha=0.8)
        bars2 = ax1.bar(x, hare_avgs, width, label='Hare (1 pt)', color=colors[1], alpha=0.8)
        bars3 = ax1.bar(x + width, stag_avgs, width, label='Stag (2 pts)', color=colors[2], alpha=0.8)

        ax1.set_xlabel('Scenario Type', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Average Score (Test Agents Only)', fontsize=12, fontweight='bold')
        ax1.set_title(f'{agent_type} - {game_type}: Reward Distribution', fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(scenarios, rotation=45, ha='right')
        ax1.legend(loc='upper right')
        ax1.grid(axis='y', alpha=0.3)

        # create the actual bars.
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                if height > 0.01:
                    ax1.text(bar.get_x() + bar.get_width() / 2., height + 0.01,
                             f'{height:.3f}', ha='center', va='bottom', fontsize=8, rotation=90)

        # Stacked percentage
        # calcualte the totals for each scenario first
        totals = [n + h + s for n, h, s in zip(nothing_avgs, hare_avgs, stag_avgs)]
        # convert each component in the totals to a percentage.
        nothing_pct = [n / t * 100 if t > 0 else 0 for n, t in zip(nothing_avgs, totals)]
        # get how often the hare happened as a percent
        hare_pct = [h / t * 100 if t > 0 else 0 for h, t in zip(hare_avgs, totals)]
        # get how often the stag happened as a percent.
        stag_pct = [s / t * 100 if t > 0 else 0 for s, t in zip(stag_avgs, totals)]

        ax2.bar(scenarios, nothing_pct, label='Nothing', color=colors[0], alpha=0.8)
        ax2.bar(scenarios, hare_pct, bottom=nothing_pct, label='Hare', color=colors[1], alpha=0.8)
        ax2.bar(scenarios, stag_pct, bottom=[n + h for n, h in zip(nothing_pct, hare_pct)],
                label='Stag', color=colors[2], alpha=0.8)

        ax2.set_xlabel('Scenario Type', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Percentage of Actions', fontsize=12, fontweight='bold')
        ax2.set_title(f'{agent_type} - {game_type}: Action Distribution (%)', fontsize=14, fontweight='bold')
        ax2.set_xticks(range(len(scenarios)))
        ax2.set_xticklabels(scenarios, rotation=45, ha='right')
        ax2.legend(loc='upper right')
        ax2.grid(axis='y', alpha=0.3)
        ax2.set_ylim(0, 100)

        plt.suptitle(f'{agent_type} - {game_type} Games: Complete Analysis', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{save_dir_game}/{agent_type}_reward_distribution.png', dpi=150, bbox_inches='tight')
        plt.close()

        print(f"Created {agent_type} {game_type} overview graph")


# ==================== STAG HUNTING GRAPHS ====================
def create_stag_hunting_comparison(results, game_type, save_dir="graphs/stag_hunting/"):
    # create graphs for cooperation success.
    save_dir_game = os.path.join(save_dir, game_type)
    os.makedirs(save_dir_game, exist_ok=True)

    agent_types = ["SCab", "HCab", "ECab"]
    agent_colors = ['#3498db', '#e74c3c', '#2ecc71']

    all_scenarios = sorted(set(extract_scenario_category(name) for name in results.keys()))

    # 1. Heatmap
    matrix = np.zeros((len(agent_types), len(all_scenarios)))

    for i, agent_type in enumerate(agent_types):
        for j, scenario in enumerate(all_scenarios):
            for scenario_name, data in results.items():
                if extract_agent_type(scenario_name) == agent_type and extract_scenario_category(
                        scenario_name) == scenario:
                    scores = data.get('score_per_player', [])
                    if scores and isinstance(scores[0], list):
                        filtered_scores = filter_relevant_scores(scenario_name, scores)
                        matrix[i, j] = np.mean([player[2] for player in filtered_scores])
                    break

    fig, ax = plt.subplots(figsize=(14, 8))
    im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto', vmin=0, vmax=1)

    for i in range(len(agent_types)):
        for j in range(len(all_scenarios)):
            text_color = "white" if matrix[i, j] > 0.6 else "black"
            ax.text(j, i, f'{matrix[i, j]:.3f}', ha="center", va="center",
                    color=text_color, fontweight='bold', fontsize=12)

    ax.set_xticks(np.arange(len(all_scenarios)))
    ax.set_yticks(np.arange(len(agent_types)))
    ax.set_xticks(range(len(all_scenarios)))
    ax.set_xticklabels(all_scenarios, rotation=45, ha='right')
    ax.set_yticklabels(agent_types)
    ax.set_xlabel('Scenario Type', fontsize=12, fontweight='bold')
    ax.set_ylabel('Agent Type', fontsize=12, fontweight='bold')
    ax.set_title(f'{game_type} Games: Stag Hunting Success Heatmap', fontsize=14, fontweight='bold')

    cbar = plt.colorbar(im)
    cbar.set_label('Average Stag Score (Test Agents)', rotation=270, labelpad=20)

    plt.tight_layout()
    plt.savefig(f'{save_dir_game}/stag_hunting_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()

    # 2. Direct comparison bar chart
    fig, ax = plt.subplots(figsize=(14, 7))
    x = np.arange(len(all_scenarios))
    width = 0.25

    for i, agent_type in enumerate(agent_types):
        stag_scores = []
        for scenario in all_scenarios:
            score_found = 0
            for scenario_name, data in results.items():
                if extract_agent_type(scenario_name) == agent_type and extract_scenario_category(
                        scenario_name) == scenario:
                    scores = data.get('score_per_player', [])
                    if scores and isinstance(scores[0], list):
                        filtered_scores = filter_relevant_scores(scenario_name, scores)
                        score_found = np.mean([player[2] for player in filtered_scores])
                    break
            stag_scores.append(score_found)

        offset = (i - 1) * width
        bars = ax.bar(x + offset, stag_scores, width, label=agent_type, color=agent_colors[i], alpha=0.8)

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

    names = [f"{extract_agent_type(name)}\n{extract_scenario_category(name)}" for name, _ in top_combinations]
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

    agent_types = ["SCab", "HCab", "ECab"]

    for agent_type in agent_types:
        agent_results = {name: data for name, data in results.items()
                         if extract_agent_type(name) == agent_type}

        if not agent_results:
            continue

        print(f"\nDEBUG: Processing {agent_type} {game_type}")
        print(f"DEBUG: Found {len(agent_results)} scenarios: {list(agent_results.keys())}")

        # First pass: collect all valid data
        scenario_data = []

        for scenario_name, data in agent_results.items():
            category = extract_scenario_category(scenario_name)
            popularity = data.get('popularity_over_time', [])

            print(f"DEBUG: {scenario_name} -> popularity: {popularity[:5] if popularity else 'EMPTY'}...")

            if not popularity or len(popularity) < 3:
                print(f"DEBUG: Skipping {scenario_name} - insufficient popularity data")
                continue

            # Calculate average popularity percentages
            total = sum(popularity) if sum(popularity) > 0 else 1

            if 'SelfPlay' in category:
                # All three are test agents - they should split ~33% each
                test_pop = sum(popularity) / total * 100  # Should be ~100%
                opp_pop = 0  # No opponents
            elif any(x in category for x in ['VGHare1', 'VGStag1', 'VAllegtr1']):
                # 2 test agents + 1 opponent
                test_pop = (popularity[0] + popularity[1]) / total * 100
                opp_pop = popularity[2] / total * 100
            elif any(x in category for x in ['VGHare2', 'VGStag2', 'VAllegtr2']):
                # 1 test agent + 2 opponents
                test_pop = popularity[0] / total * 100
                opp_pop = (popularity[1] + popularity[2]) / total * 100
            else:
                print(f"DEBUG: Unknown category: {category}")
                continue

            scenario_data.append({
                'category': category,
                'test_pop': test_pop,
                'opp_pop': opp_pop
            })

        if not scenario_data:
            print(f"DEBUG: No valid data for {agent_type} {game_type}")
            continue

        # Extract aligned lists
        scenarios = [d['category'] for d in scenario_data]
        test_vals = [d['test_pop'] for d in scenario_data]
        opp_vals = [d['opp_pop'] for d in scenario_data]

        print(f"DEBUG: Creating graph with {len(scenarios)} scenarios")
        print(f"DEBUG: test_vals: {test_vals}")
        print(f"DEBUG: opp_vals: {opp_vals}")

        # Create grouped bar chart
        fig, ax = plt.subplots(figsize=(14, 8))

        x = np.arange(len(scenarios))
        width = 0.35

        bars1 = ax.bar(x - width / 2, test_vals, width,
                       label=f'{agent_type} (Test Agents)',
                       color='#2ecc71', alpha=0.8, edgecolor='black')

        # Only add opponent bars if there are opponents
        if any(v > 0 for v in opp_vals):
            bars2 = ax.bar(x + width / 2, opp_vals, width,
                           label='Opponent Agents',
                           color='#e74c3c', alpha=0.8, edgecolor='black')

        ax.set_xlabel('Scenario Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average Popularity (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'{agent_type} - {game_type}: Test Agents vs Opponents Popularity',
                     fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(scenarios, rotation=45, ha='right')
        ax.legend(loc='upper right')
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim(0, 105)

        # Add value labels
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

        # Add 50% reference line
        ax.axhline(y=50, color='black', linestyle='--', alpha=0.3, linewidth=1)

        plt.tight_layout()
        plt.savefig(f'{save_dir_game}/{agent_type}_popularity.png', dpi=150, bbox_inches='tight')
        plt.close()

        print(f"Created {agent_type} {game_type} popularity graph")

# ==================== HARE INTENT GRAPHS ====================
def create_hare_intent_graphs(results, game_type, save_dir="graphs/hare_intent/"):
    """HARE INTENT FOLDER: Show percentage of time agents attempt to hunt hares"""
    save_dir_game = os.path.join(save_dir, game_type)
    os.makedirs(save_dir_game, exist_ok=True)

    agent_types = ["SCab", "HCab", "ECab"]

    for agent_type in agent_types:
        agent_results = {name: data for name, data in results.items()
                         if extract_agent_type(name) == agent_type}

        if not agent_results:
            continue

        fig, ax = plt.subplots(figsize=(14, 8))

        scenarios = []
        hare_intent_values = []

        for scenario_name, data in agent_results.items():
            category = extract_scenario_category(scenario_name)
            hare_intent = data.get('hare_intent_percent_total', 0)

            scenarios.append(category)
            # Convert to percentage if it's a decimal
            if hare_intent < 1:
                hare_intent_values.append(hare_intent * 100)
            else:
                hare_intent_values.append(hare_intent)

        # Create bar chart
        colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(scenarios)))
        bars = ax.bar(scenarios, hare_intent_values, color=colors, alpha=0.8, edgecolor='black')

        ax.set_xlabel('Scenario Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Hare Intent (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'{agent_type} - {game_type}: Hare Hunting Intent Percentage',
                     fontsize=14, fontweight='bold')
        ax.set_xticklabels(scenarios, rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3)

        # Add value labels
        for bar, value in zip(bars, hare_intent_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height + 1,
                    f'{value:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Add interpretation guide
        ax.axhline(y=50, color='black', linestyle='--', alpha=0.3, linewidth=1)
        ax.text(len(scenarios) - 0.5, 52, 'More hare hunting →', ha='right', fontsize=9, style='italic', alpha=0.7)
        ax.text(len(scenarios) - 0.5, 48, '← Less hare hunting', ha='right', fontsize=9, style='italic', alpha=0.7)

        plt.tight_layout()
        plt.savefig(f'{save_dir_game}/{agent_type}_hare_intent.png', dpi=150, bbox_inches='tight')
        plt.close()

        print(f"Created {agent_type} {game_type} hare intent graph")


# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    # Load all results
    all_results = load_all_results()

    print(f"Loaded {len(all_results['Round'])} Round results and {len(all_results['Step'])} Step results\n")

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

    print("\n" + "=" * 60)
    print("✅ ALL GRAPHS GENERATED SUCCESSFULLY!")
    print("=" * 60)
    print("""
📁 Graph Directory Structure:
  📁 graphs/
    📁 overview/
      📁 Round/    - SCab/HCab/ECab reward distributions (Round)
      📁 Step/     - SCab/HCab/ECab reward distributions (Step)
    📁 stag_hunting/
      📁 Round/    - Cooperation heatmaps & comparisons (Round)
      📁 Step/     - Cooperation heatmaps & comparisons (Step)
    📁 popularity/
      📁 Round/    - Test agent vs opponent popularity (Round)
      📁 Step/     - Test agent vs opponent popularity (Step)
    📁 hare_intent/
      📁 Round/    - Hare hunting intent percentages (Round)
      📁 Step/     - Hare hunting intent percentages (Step)
    """)