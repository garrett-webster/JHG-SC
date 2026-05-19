import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from stagHare.transVecTranslatorStagHare import translateVecToIndexStagHare
from stagHare.utils.create_options_matrix import create_options_matrix


def process_allocations_for_intent_graphing(allocations):
    """
    Takes a list of player allocations and returns dict ready for meshing.

    Input: [player0_allocs, player1_allocs, player2_allocs]
    where each player_allocs is a list of [self, x, y] per round

    Returns: dict with player_id as key and list of (round_num, x, y) tuples
    """
    # Transpose to get each player's allocations across rounds
    p0_allocs, p1_allocs, p2_allocs = [[list(a) for a in player] for player in zip(*allocations)]

    # Normalize each allocation
    for player_allocs in [p0_allocs, p1_allocs, p2_allocs]:
        for alloc in player_allocs:
            total = abs(alloc[0]) + abs(alloc[1]) + abs(alloc[2])
            if total > 0:
                alloc[0] /= total
                alloc[1] /= total
                alloc[2] /= total

    # Apply transformations to reorder
    for sublist in p0_allocs:
        sublist[0], sublist[1], sublist[2] = sublist[0], sublist[1], sublist[2]

    for sublist in p1_allocs:
        sublist[0], sublist[1], sublist[2] = sublist[1], sublist[0], sublist[2]

    for sublist in p2_allocs:
        sublist[0], sublist[1], sublist[2] = sublist[2], sublist[0], sublist[1]

    # Build result: drop self-allocation, keep x,y with round number
    player_allocations = {
        0: [(round_num, p0_allocs[round_num][1], p0_allocs[round_num][2]) for round_num in range(len(p0_allocs))],
        1: [(round_num, p1_allocs[round_num][1], p1_allocs[round_num][2]) for round_num in range(len(p1_allocs))],
        2: [(round_num, p2_allocs[round_num][1], p2_allocs[round_num][2]) for round_num in range(len(p2_allocs))]
    }

    return player_allocations

def create_player_tracking_mesh(player_id, player_allocations=None, round_range=None):
    """
    Create a mesh for a specific player with their allocation points plotted.

    Parameters:
    - player_id: The ID of this player (used to generate the mesh from their perspective)
    - player_allocations: Dict of {round_num: (x, y)} or list of (round_num, x, y) tuples
    - round_range: Optional tuple of (min_round, max_round) to filter which rounds to show
    """
    # Create the base mesh from this player's perspective
    fig, ax, intent_grid, X, Y, intent_indices, valid_allocations = create_intent_mesh(
        resolution=50,
        player_id=player_id
    )

    # Update title to show which player's perspective
    ax.set_title(f'Player {player_id} Action Space: Allocation Tracking',
                 fontsize=16, fontweight='bold')

    if player_allocations:
        # Convert to array format if it's a dict
        if isinstance(player_allocations, dict):
            points_data = [(round_num, x, y) for round_num, (x, y) in player_allocations.items()]
        else:
            points_data = player_allocations

        # Filter by round range if specified
        if round_range:
            min_round, max_round = round_range
            points_data = [(r, x, y) for r, x, y in points_data
                           if min_round <= r <= max_round]

        if points_data:
            rounds, xs, ys = zip(*points_data)
            rounds = np.array(rounds)
            points = np.column_stack([xs, ys])

            # Color mapping based on round number
            norm = plt.Normalize(rounds.min(), rounds.max())
            cmap = plt.cm.viridis  # You can change this to any colormap

            # Plot points with colors indicating round
            scatter = ax.scatter(points[:, 0], points[:, 1],
                                 c=rounds, cmap=cmap, s=150,
                                 edgecolors='black', linewidth=2,
                                 zorder=10, norm=norm)

            # Add round number labels
            for i, (round_num, x, y) in enumerate(points_data):
                ax.annotate(f'R{round_num}', (x, y),
                            xytext=(5, 5), textcoords='offset points',
                            fontsize=8, fontweight='bold',
                            bbox=dict(boxstyle='round,pad=0.2',
                                      facecolor='white', alpha=0.8),
                            zorder=15)

            # Draw lines connecting rounds in order
            if len(points) > 1:
                ax.plot(points[:, 0], points[:, 1], 'k--',
                        linewidth=1, alpha=0.5, zorder=5,
                        label='Allocation path')

            # Add colorbar for rounds
            cbar = plt.colorbar(scatter, ax=ax, label='Round Number')

            ax.legend()

    return fig, ax


def create_combined_tracking_view(all_players_allocations, num_players=3):
    """
    Create a single figure with subplots for each player's perspective.

    Parameters:
    - all_players_allocations: Dict mapping player_id to list of (round_num, x, y) tuples
    - num_players: Total number of players to show
    """
    fig, axes = plt.subplots(1, num_players, figsize=(18, 6))

    if num_players == 1:
        axes = [axes]

    for player_id in range(num_players):
        ax = axes[player_id]

        # Create mesh for this player
        _, _, intent_grid, X, Y, _, _ = create_intent_mesh(
            resolution=50,
            player_id=player_id
        )

        # Clear the existing axis and replot on our subplot axis
        ax.clear()

        # Recreate mesh on this axis
        from matplotlib.colors import ListedColormap
        color_list = ['#FF4444', '#CC0000', '#4444FF', '#0000CC']
        custom_cmap = ListedColormap(color_list)

        im = ax.pcolormesh(X, Y, intent_grid, cmap=custom_cmap,
                           vmin=0, vmax=3, shading='auto', alpha=0.7)

        # Add styling
        ax.axhline(y=0, color='black', linestyle='-', linewidth=2, alpha=0.7)
        ax.axvline(x=0, color='black', linestyle='-', linewidth=2, alpha=0.7)
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_xlabel('Other Agent 1', fontsize=12, fontweight='bold')
        ax.set_ylabel('Other Agent 2', fontsize=12, fontweight='bold')
        ax.set_title(f'Player {player_id} Perspective', fontsize=14, fontweight='bold')

        # Plot this player's allocations
        if player_id in all_players_allocations:
            points_data = all_players_allocations[player_id]

            if points_data:
                rounds, xs, ys = zip(*points_data)
                points = np.column_stack([xs, ys])

                # Plot points
                norm = plt.Normalize(min(rounds), max(rounds))
                scatter = ax.scatter(points[:, 0], points[:, 1],
                                     c=rounds, cmap='viridis', s=100,
                                     edgecolors='black', linewidth=1.5,
                                     zorder=10)

                # Add labels
                for round_num, x, y in points_data:
                    ax.annotate(f'R{round_num}', (x, y),
                                xytext=(3, 3), textcoords='offset points',
                                fontsize=7, fontweight='bold',
                                bbox=dict(boxstyle='round,pad=0.1',
                                          facecolor='white', alpha=0.7))

                # Draw path
                if len(points) > 1:
                    ax.plot(points[:, 0], points[:, 1], 'k--',
                            linewidth=1, alpha=0.5)

    plt.tight_layout()
    return fig, axes


# Define color list
color_list = [
    '#FF4444',  # 0: Light red - Hare Move
    '#CC0000',  # 1: Dark red - Hare Take
    '#4444FF',  # 2: Light blue - Stag Move
    '#0000CC',  # 3: Dark blue - Stag Take
]


def create_intent_mesh(resolution=50, player_id=0):
    """
    Creates the intent zone mesh without displaying it.
    EXACT MATCH to working original code.
    """
    # Grid parameters
    x = np.linspace(-1, 1, resolution)
    y = np.linspace(-1, 1, resolution)
    X, Y = np.meshgrid(x, y)

    # Calculate Z to make allocations sum to 1 (absolute values)
    Z = 1 - np.abs(X) - np.abs(Y)

    # Create flattened arrays of all allocation points
    allocations = np.column_stack([Z.ravel(), X.ravel(), Y.ravel()])

    # Filter to keep only valid allocations
    valid_mask = np.all((allocations >= -1) & (allocations <= 1), axis=1) & (allocations[:, 0] >= 0)
    valid_allocations = allocations[valid_mask]

    # Calculate intent for each valid allocation
    intent_indices = np.zeros(len(valid_allocations), dtype=int)
    for i, allocation in enumerate(valid_allocations):
        # Match the original call signature - 2 args like the original!
        intent_index = translateVecToIndexStagHare(
            allocation.tolist(),
            0,  # Just player_id, no options matrix
        )
        intent_indices[i] = intent_index

    # Create the 2D grid for plotting
    intent_grid = np.full(X.shape, np.nan)
    intent_grid_flat = np.full(X.size, np.nan)
    intent_grid_flat[valid_mask] = intent_indices
    intent_grid = intent_grid_flat.reshape(X.shape)

    # Create the plot with just the mesh
    fig, ax = plt.subplots(figsize=(12, 10))

    custom_cmap = ListedColormap(color_list)
    im = ax.pcolormesh(X, Y, intent_grid, cmap=custom_cmap,
                       vmin=0, vmax=3, shading='auto', alpha=0.7)

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, ticks=[0, 1, 2, 3])
    cbar.set_label('Intent Category', fontsize=12)
    cbar.ax.set_yticklabels(['Hare Move', 'Hare Take', 'Stag Move', 'Stag Take'])

    # Add axis lines and grid
    ax.axhline(y=0, color='black', linestyle='-', linewidth=2, alpha=0.7)
    ax.axvline(x=0, color='black', linestyle='-', linewidth=2, alpha=0.7)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)

    # Labels and title
    ax.set_xlabel('Agent 1 Allocation', fontsize=14, fontweight='bold')
    ax.set_ylabel('Agent 2 Allocation', fontsize=14, fontweight='bold')
    ax.set_title('Stag Hare Action Space: Intent Zones',
                 fontsize=16, fontweight='bold')

    # Set axis limits
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)

    # Add quadrant labels
    ax.text(0.5, 0.5, 'Both Give', ha='center', va='center',
            fontsize=10, alpha=0.5, transform=ax.transData)
    ax.text(-0.5, 0.5, 'A1 Takes, A2 Gives', ha='center', va='center',
            fontsize=10, alpha=0.5, transform=ax.transData)
    ax.text(0.5, -0.5, 'A1 Gives, A2 Takes', ha='center', va='center',
            fontsize=10, alpha=0.5, transform=ax.transData)
    ax.text(-0.5, -0.5, 'Both Take', ha='center', va='center',
            fontsize=10, alpha=0.5, transform=ax.transData)

    plt.tight_layout()

    return fig, ax, intent_grid, X, Y, intent_indices, valid_allocations