import json
import os
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def load_all_results(directory_path="results/"):
    """Load all result files from the directory"""
    results = {}

    for file in os.listdir(directory_path):
        if file.endswith('.json'):
            file_path = os.path.join(directory_path, file)
            scenario_name = file.replace('.json', '')

            with open(file_path, 'r') as f:
                data = json.load(f)
                results[scenario_name] = data

    return results


def extract_agent_type(scenario_name):
    """Extract agent type from scenario name (SCab, HCab, ECab)"""
    if scenario_name.startswith('SCab'):
        return 'SCab'
    elif scenario_name.startswith('HCab'):
        return 'HCab'
    elif scenario_name.startswith('ECab'):
        return 'ECab'
    return 'Unknown'


def extract_scenario_category(scenario_name):
    """Extract scenario category (SelfPlay, VGHare1, VGHare2, etc.)"""
    if scenario_name.startswith('SCab'):
        category = scenario_name[4:]  # Remove 'SCab'
    elif scenario_name.startswith('HCab'):
        category = scenario_name[4:]  # Remove 'HCab'
    elif scenario_name.startswith('ECab'):
        category = scenario_name[4:]  # Remove 'ECab'
    else:
        category = scenario_name
    return category


def create_agent_type_comparison(results, metric="coop_scores", save_dir="graphs/"):
    """Create graphs comparing within each agent type across scenarios"""
    os.makedirs(save_dir, exist_ok=True)

    agent_types = ["SCab", "HCab", "ECab"]

    for agent_type in agent_types:
        agent_results = {name: data for name, data in results.items()
                         if extract_agent_type(name) == agent_type}

        if not agent_results:
            continue

        scenarios = []
        values = []

        for scenario_name, data in agent_results.items():
            category = extract_scenario_category(scenario_name)
            metric_data = data.get(metric, 0)

            # Handle score_per_player specially - average across players for overview
            if metric == "score_per_player" and isinstance(metric_data, list) and isinstance(metric_data[0], list):
                # Calculate average score per player, then average across players
                avg_player_scores = [np.mean(player_scores) for player_scores in metric_data]
                metric_value = np.mean(avg_player_scores)
            elif isinstance(metric_data, list):
                metric_value = np.mean(metric_data)
            else:
                metric_value = metric_data

            scenarios.append(category)
            values.append(metric_value)

        plt.figure(figsize=(12, 6))
        colors = plt.cm.tab10(np.linspace(0, 1, len(scenarios)))
        bars = plt.bar(scenarios, values, color=colors)

        plt.title(f"{agent_type} - Average Score Comparison Across Scenarios", fontsize=14, fontweight='bold')
        plt.xlabel("Scenario Type", fontsize=12)
        plt.ylabel("Average Score", fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis="y", alpha=0.3)

        for bar, value in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                     f"{value:.3f}", ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        plt.savefig(f'{save_dir}{agent_type}_average_score.png', dpi=100, bbox_inches='tight')
        plt.close()

        print(f"Created {agent_type} average score comparison graph")


def create_score_breakdown_by_agent(results, save_dir="graphs/"):
    """
    Create graphs showing the score breakdown by reward type for each agent.
    Scores are: [nothing_score, hare_score, stag_score]
    """
    os.makedirs(save_dir, exist_ok=True)

    agent_types = ["SCab", "HCab", "ECab"]
    reward_labels = ['Nothing', 'Hare', 'Stag']
    colors = ['#e74c3c', '#f39c12', '#2ecc71']  # Red for nothing, Orange for hare, Green for stag

    for agent_type in agent_types:
        agent_results = {name: data for name, data in results.items()
                         if extract_agent_type(name) == agent_type}

        if not agent_results:
            continue

        # Create a separate graph for each scenario within this agent type
        for scenario_name, data in agent_results.items():
            scores = data.get('score_per_player', [])

            if not scores or not isinstance(scores[0], list):
                continue

            category = extract_scenario_category(scenario_name)
            num_players = len(scores)

            # Create grouped bar chart
            fig, ax = plt.subplots(figsize=(12, 6))

            x = np.arange(num_players)
            width = 0.25

            # For each player, extract their three scores
            nothing_scores = [player[0] for player in scores]
            hare_scores = [player[1] for player in scores]
            stag_scores = [player[2] for player in scores]

            # Create bars for each reward type
            bars1 = ax.bar(x - width, nothing_scores, width, label='Nothing', color=colors[0])
            bars2 = ax.bar(x, hare_scores, width, label='Hare', color=colors[1])
            bars3 = ax.bar(x + width, stag_scores, width, label='Stag', color=colors[2])

            ax.set_xlabel('Players', fontsize=12)
            ax.set_ylabel('Score Value', fontsize=12)
            ax.set_title(f'{agent_type} - {category}: Score Breakdown by Reward Type', fontsize=14, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels([f'Player {i + 1}' for i in range(num_players)])
            ax.legend()
            ax.grid(axis='y', alpha=0.3)

            # Add value labels
            for bars in [bars1, bars2, bars3]:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0.01:  # Only label non-zero values
                        ax.text(bar.get_x() + bar.get_width() / 2., height + 0.01,
                                f'{height:.3f}', ha='center', va='bottom', fontsize=8)

            plt.tight_layout()
            plt.savefig(f'{save_dir}{agent_type}_{category}_score_breakdown.png', dpi=100, bbox_inches='tight')
            plt.close()

            print(f"Created {agent_type} - {category} score breakdown graph")


def create_score_breakdown_comparison(results, save_dir="graphs/"):
    """
    Create comparison graphs showing how different reward types vary across scenarios
    for each agent type
    """
    os.makedirs(save_dir, exist_ok=True)

    agent_types = ["SCab", "HCab", "ECab"]
    reward_labels = ['Nothing', 'Hare', 'Stag']
    colors = ['#e74c3c', '#f39c12', '#2ecc71']

    for agent_type in agent_types:
        agent_results = {name: data for name, data in results.items()
                         if extract_agent_type(name) == agent_type}

        if not agent_results:
            continue

        # Prepare data for plotting
        scenarios = []
        nothing_avgs = []
        hare_avgs = []
        stag_avgs = []

        for scenario_name, data in agent_results.items():
            scores = data.get('score_per_player', [])

            if not scores or not isinstance(scores[0], list):
                continue

            category = extract_scenario_category(scenario_name)
            scenarios.append(category)

            # Average each reward type across all players
            nothing_avg = np.mean([player[0] for player in scores])
            hare_avg = np.mean([player[1] for player in scores])
            stag_avg = np.mean([player[2] for player in scores])

            nothing_avgs.append(nothing_avg)
            hare_avgs.append(hare_avg)
            stag_avgs.append(stag_avg)

        # Create grouped bar chart
        fig, ax = plt.subplots(figsize=(14, 6))

        x = np.arange(len(scenarios))
        width = 0.25

        bars1 = ax.bar(x - width, nothing_avgs, width, label='Nothing (0 points)', color=colors[0])
        bars2 = ax.bar(x, hare_avgs, width, label='Hare (1 point)', color=colors[1])
        bars3 = ax.bar(x + width, stag_avgs, width, label='Stag (2 points)', color=colors[2])

        ax.set_xlabel('Scenario Type', fontsize=12)
        ax.set_ylabel('Average Score', fontsize=12)
        ax.set_title(f'{agent_type} - Reward Type Distribution Across Scenarios', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(scenarios, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        # Add value labels
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                if height > 0.01:
                    ax.text(bar.get_x() + bar.get_width() / 2., height + 0.01,
                            f'{height:.3f}', ha='center', va='bottom', fontsize=8, rotation=90)

        plt.tight_layout()
        plt.savefig(f'{save_dir}{agent_type}_reward_distribution.png', dpi=100, bbox_inches='tight')
        plt.close()

        print(f"Created {agent_type} reward distribution graph")


def create_scenario_comparison_by_reward(results, save_dir="graphs/"):
    """
    Compare the same scenario across different agent types, showing reward breakdown
    """
    os.makedirs(save_dir, exist_ok=True)

    # Get all unique scenario categories
    all_categories = set()
    for name in results.keys():
        all_categories.add(extract_scenario_category(name))

    colors = ['#3498db', '#e74c3c', '#2ecc71']  # Blue for SCab, Red for HCab, Green for ECab

    for category in sorted(all_categories):
        # Collect data for this category across agent types
        agent_scores = {}

        for scenario_name, data in results.items():
            if extract_scenario_category(scenario_name) == category:
                agent_type = extract_agent_type(scenario_name)
                scores = data.get('score_per_player', [])

                if scores and isinstance(scores[0], list):
                    # Average stag scores (index 2) across all players
                    stag_avg = np.mean([player[2] for player in scores])
                    agent_scores[agent_type] = stag_avg

        if not agent_scores:
            continue

        # Create bar chart comparing stag hunting success
        agent_types = list(agent_scores.keys())
        stag_values = [agent_scores[at] for at in agent_types]

        plt.figure(figsize=(10, 6))
        bars = plt.bar(agent_types, stag_values, color=colors[:len(agent_types)])

        plt.title(f'{category} - Average Stag Hunting Score Comparison', fontsize=14, fontweight='bold')
        plt.xlabel('Agent Type', fontsize=12)
        plt.ylabel('Average Stag Score (Cooperation Success)', fontsize=12)
        plt.grid(axis='y', alpha=0.3)

        for bar, value in zip(bars, stag_values):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                     f'{value:.3f}', ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        plt.savefig(f'{save_dir}{category}_stag_comparison.png', dpi=100, bbox_inches='tight')
        plt.close()

        print(f"Created {category} stag score comparison graph")


def create_agent_type_score_breakdown(results, save_dir="graphs/"):
    """
    Create grouped bar charts showing Nothing, Hare, and Stag scores
    for each scenario within each agent type
    """
    os.makedirs(save_dir, exist_ok=True)

    agent_types = ["SCab", "HCab", "ECab"]
    reward_labels = ['Nothing', 'Hare', 'Stag']
    colors = ['#e74c3c', '#f39c12', '#2ecc71']  # Red, Orange, Green

    for agent_type in agent_types:
        agent_results = {name: data for name, data in results.items()
                         if extract_agent_type(name) == agent_type}

        if not agent_results:
            continue

        # Prepare data
        scenarios = []
        nothing_avgs = []
        hare_avgs = []
        stag_avgs = []

        for scenario_name, data in agent_results.items():
            category = extract_scenario_category(scenario_name)
            scores = data.get('score_per_player', [])

            if not scores or not isinstance(scores[0], list):
                continue

            scenarios.append(category)

            # Average each reward type across all players
            nothing_avgs.append(np.mean([player[0] for player in scores]))
            hare_avgs.append(np.mean([player[1] for player in scores]))
            stag_avgs.append(np.mean([player[2] for player in scores]))

        # Create grouped bar chart
        fig, ax = plt.subplots(figsize=(14, 7))

        x = np.arange(len(scenarios))
        width = 0.25

        bars1 = ax.bar(x - width, nothing_avgs, width, label='Nothing (0 pts)', color=colors[0], alpha=0.8)
        bars2 = ax.bar(x, hare_avgs, width, label='Hare (1 pt)', color=colors[1], alpha=0.8)
        bars3 = ax.bar(x + width, stag_avgs, width, label='Stag (2 pts)', color=colors[2], alpha=0.8)

        ax.set_xlabel('Scenario Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average Score Value', fontsize=12, fontweight='bold')
        ax.set_title(f'{agent_type} - Score Breakdown by Reward Type', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(scenarios, rotation=45, ha='right')
        ax.legend(loc='upper right')
        ax.grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                if height > 0.01:
                    ax.text(bar.get_x() + bar.get_width() / 2., height + 0.01,
                            f'{height:.3f}', ha='center', va='bottom', fontsize=8, rotation=90)

        # Add explanation text
        fig.text(0.5, 0.01,
                 'Nothing: Failed to catch anything (0 pts) | Hare: Solo hunting success (1 pt) | Stag: Cooperative hunting success (2 pts)',
                 ha='center', fontsize=10, style='italic')

        plt.tight_layout()
        plt.savefig(f'{save_dir}{agent_type}_score_breakdown.png', dpi=150, bbox_inches='tight')
        plt.close()

        print(f"Created {agent_type} score breakdown graph")


if __name__ == "__main__":
    # Load all results
    results = load_all_results()

    print(f"Loaded {len(results)} result files")

    # Create overview graphs
    print("\n=== Creating Overview Comparisons ===")
    # create_agent_type_comparison(results, 'coop_scores')
    # create_agent_type_comparison(results, 'hare_intent_percent_total')

    # Create detailed score breakdown graphs
    print("\n=== Creating Score Breakdown Graphs ===")
    create_score_breakdown_by_agent(results)
    create_score_breakdown_comparison(results)

    # Create scenario comparisons
    print("\n=== Creating Scenario Comparisons ===")
    create_scenario_comparison_by_reward(results)

    print("\n✅ All graphs generated successfully in the 'graphs/' directory!")