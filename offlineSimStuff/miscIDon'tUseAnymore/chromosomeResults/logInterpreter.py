import json
import os

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def create_heatmap(corr):
    # this code creates a heatmap to show the correlation values, as well as print a few out.
    sns.heatmap(corr, annot=True, cmap="coolwarm")
    plt.title("Corrleation Matrix")

    my_path = os.path.abspath(os.path.dirname(__file__))
    file_name = os.path.join(my_path, "chromosomeCorrMatrix.png")
    plt.savefig(file_name)


    plt.show()

    print("Corr 1 & increase:", df['chromosome_1'].corr(df['total_average_increase']))
    print("Corr 2 & increase:", df['chromosome_2'].corr(df['total_average_increase']))


def scatter_plots_2D():
    # this code creates scatter plots for chromosome 1 vs total increase and chromosome 2 vs total increase
    max1 = df.loc[df["total_average_increase"].idxmax()]
    min1 = df.loc[df["total_average_increase"].idxmin()]
    print("🔺 Max Total Increase Entry:\n", max1)
    print("🔻 Min Total Increase Entry:\n", min1)

    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    sns.scatterplot(data=df, x="chromosome_1", y="total_average_increase")
    plt.xscale("log")
    plt.title("chromosome 1 vs total increase")

    plt.subplot(1, 2, 2)
    sns.scatterplot(data=df, x="chromosome_2", y="total_average_increase")
    plt.xscale("log")
    plt.title("chromosome 2 vs total increase")

    plt.tight_layout()
    plt.show()

def create_3d_plots(df): # doesn't seem to work, doesn't want to set the log limits for whatever reason. IDEK
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')

    # Plot points
    sc = ax.scatter(
        df['chromosome_1'], df['chromosome_2'], df['total_average_increase'],
        c=df['total_average_increase'], cmap='viridis', s=50
    )

    # Axis labels
    ax.set_xlabel('Chromosome 1')
    ax.set_ylabel('Chromosome 2')
    ax.set_zlabel('Total Average Increase')

    # # Optional: set log scale for better spread
    print("X-axis limits before log scale:", ax.get_xlim())
    ax.set_xscale('log')

    # Colorbar to show what values mean
    fig.colorbar(sc, label='Total Average Increase')

    plt.title("3D Scatter Plot: Chromosome Pairs vs Total Increase")
    plt.tight_layout()
    my_path = os.path.abspath(os.path.dirname(__file__))
    file_name = os.path.join(my_path, "3dThingy.png")
    plt.savefig(file_name)


    plt.show()


if __name__ == "__main__":

    # this code here creates the actual dataFrame given the json.
    with open('chromosomeLoggingTime.txt', 'r') as f:
        data = json.load(f)

    rows = []
    for filename, metrics in data.items():
        chrom1, chrom2 = map(float, filename.replace(".txt", "").split(","))
        row = {
            "chromosome_1": chrom1,
            "chromosome_2": chrom2,
            **metrics
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    max_row = df.loc[df['total_average_increase'].idxmax()]

    # Print the relevant details
    print("🔝 Highest Total Average Increase:")
    print(f"Chromosome 1: {max_row['chromosome_1']}")
    print(f"Chromosome 2: {max_row['chromosome_2']}")
    print(f"Total Average Increase: {max_row['total_average_increase']}")







