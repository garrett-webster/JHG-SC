from itertools import zip_longest
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap

from stagHare.transVecTranslatorStagHare import translateVecToIndexStagHare
from stagHare.utils.create_options_matrix import create_options_matrix

# Define color list
color_list = [
    '#FF4444',  # 0: Light red
    '#CC0000',  # 1: Dark red
    '#4444FF',  # 2: Light blue
    '#0000CC',  # 3: Dark blue
]

# assume these are prenormalized allocations in a list.
def graph_allocations(valid_allocations):
    graphing_points = valid_allocations[:, 1:]  # Just X and Y columns
    print(f"Total points: {len(allocations)}")
    print(f"Valid points (all values in [-1,1]): {len(valid_allocations)}")

    # Vectorized approach: process each allocation
    intent_indices = np.zeros(len(valid_allocations), dtype=int)

    # Since translateVecToIndexStagHare might not be vectorized,
    # we still loop but pre-allocate arrays for speed
    for i, allocation in enumerate(valid_allocations):
        intent_index = translateVecToIndexStagHare(
            allocation.tolist(),
            current_options_matrix,
            0
        )

        intent_indices[i] = intent_index
        if intent_index == 1:
            print("Here is the allocation ! ", allocation)

    # Create the 2D grid for plotting
    intent_grid = np.full(X.shape, np.nan)  # Fill with NaN for invalid points
    intent_grid_flat = np.full(X.size, np.nan)
    intent_grid_flat[valid_mask] = intent_indices
    intent_grid = intent_grid_flat.reshape(X.shape)

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 10))

    # Method 1: Plot as a colored mesh (faster for large grids)
    custom_cmap = ListedColormap(color_list)
    im = ax.pcolormesh(X, Y, intent_grid, cmap=custom_cmap,
                       vmin=0, vmax=3, shading='auto', alpha=0.9)

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, ticks=[0, 1, 2, 3])
    cbar.set_label('Intent Category', fontsize=12)
    cbar.ax.set_yticklabels(['Hare Move', 'Hare Take', 'Stag Move', 'Stag Take'])

    # Add axis lines
    ax.axhline(y=0, color='black', linestyle='-', linewidth=2, alpha=0.7)
    ax.axvline(x=0, color='black', linestyle='-', linewidth=2, alpha=0.7)

    # Add grid lines for better readability
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)

    # Labels and title
    ax.set_xlabel('Agent 1 Allocation', fontsize=14, fontweight='bold')
    ax.set_ylabel('Agent 2 Allocation', fontsize=14, fontweight='bold')
    ax.set_title('Stag Hare Action Space: Intent by Allocation',
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
    plt.show()

    # Alternative: Scatter plot version (if you prefer points over mesh)
    fig2, ax2 = plt.subplots(figsize=(12, 10))

    # Create scatter plot with colors
    colors_array = np.array(color_list)[intent_indices]
    ax2.scatter(graphing_points[:, 0], graphing_points[:, 1],
                c=colors_array, s=30, alpha=0.8, edgecolors='black',
                linewidth=0.3)

    # Add the same styling
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=2, alpha=0.7)
    ax2.axvline(x=0, color='black', linestyle='-', linewidth=2, alpha=0.7)
    ax2.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax2.set_xlabel('Agent 1 Allocation', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Agent 2 Allocation', fontsize=14, fontweight='bold')
    ax2.set_title('Stag Hare Action Space: Intent by Allocation (Scatter)',
                  fontsize=16, fontweight='bold')
    ax2.set_xlim(-1, 1)
    ax2.set_ylim(-1, 1)

    plt.tight_layout()
    plt.show()

    # Print some statistics
    print("\nIntent Distribution:")
    unique, counts = np.unique(intent_indices, return_counts=True)
    intent_names = ['Hare Move', 'Hare Take', 'Stag Move', 'Stag Take']
    for intent, count in zip(unique, counts):
        print(f"  {intent_names[intent]}: {count} ({100 * count / len(intent_indices):.1f}%)")


if __name__ == '__main__':
    # Grid parameters
    resolution = 50
    x = np.linspace(-1, 1, resolution)
    y = np.linspace(-1, 1, resolution)
    X, Y = np.meshgrid(x, y)

    # Calculate Z to make allocations sum to 1 (THE ABS THEREOF)
    Z = 1 - np.abs(X) - np.abs(Y)

    # Create and normalize options matrix
    current_options_matrix = create_options_matrix(0) # assume a 0 id (single player perspective. could be any; I chose that one)
    current_options_matrix = [row / sum(np.abs(row)) for row in current_options_matrix]
    print("Normalized options matrix:")
    for i, row in enumerate(current_options_matrix):
        print(f"  Option {i}: {row}")

    # Create flattened arrays of all allocation points
    # Shape: (resolution*resolution, 3) for allocations
    allocations = np.column_stack([Z.ravel(), X.ravel(), Y.ravel()])

    # Filter to keep only valid allocations (each value in [-1, 1])
    # also make sure that z can't be negative -- we can't steal from ourselves.
    valid_mask = np.all((allocations >= -1) & (allocations <= 1), axis=1) & (allocations[:, 0] >= 0)
    valid_allocations = allocations[valid_mask]
    graph_allocations(valid_allocations)

    # Test symmetry explicitly
    test_points = [
        (0.5, -0.5, "A1 gives, A2 takes"),
        (-0.5, 0.5, "A1 takes, A2 gives"),
        (0.7, 0.2, "Both positive, asymmetric"),
        (0.2, 0.7, "Both positive, swapped"),
        (0.1, -0.4, "Both positive, asymmetric"),
        (-0.4, 0.1, "Both positive, asymmetric"),
    ]

    for x, y, desc in test_points:
        z = 1 - abs(x) - abs(y)
        alloc = [z, x, y]
        idx = translateVecToIndexStagHare(alloc, current_options_matrix, 0)
        print(f"{desc}: ({x}, {y}) → index {idx} ({['HM', 'HT', 'SM', 'ST'][idx]})")

    # so the fetcher IS symmetric. good to know.




