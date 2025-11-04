import pandas as pd
import json
import seaborn as sns
import matplotlib.pyplot as plt

if __name__ == "__main__":

    # just trust the system on the file path
    df = pd.read_csv("subsetForFormatting/simulation_results.csv")

    json_columns = ["RoundType", "UtilityLog", "PopularityLog"]
    for col in json_columns:
        df[col] = df[col].apply(lambda x: json.loads(x) if pd.notna(x) else None)

    numeric_cols = [
        "PeepConstant",
        "AverageUtilityNonCats",
        "AverageUtilityCats",
        "AveragePopularityNonCats",
        "AveragePopularityCats"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce") # not really sure what this does but we will roll with it


    # for this version, we don't need the averageUtilityNonCats or averagePopNonCats, as they will be none
    df.drop("AverageUtilityCats", axis=1, inplace=True)
    df.drop("AveragePopularityCats", axis=1, inplace=True)

    print(df.columns)

    group_cols = ["AgentType", "Scenario", "EnforceMajority", "PeepConstant", "RoundType", "AveragePopularityNonCats", "AverageUtilityNonCats"]
    grouped = df.groupby(group_cols) # thats WACK. so cool.

    g = sns.FacetGrid(
        df,
        row="AgentType",
        col="Scenario",
        hue="EnforceMajority",
        margin_titles=True,
        height=4,  # height of each facet
        aspect=2  # width/height ratio; increase to make wider
    )
    g.map(sns.boxplot, "PeepConstant", "AverageUtilityNonCats")
    g.add_legend()

    # Rotate x-axis labels for readability
    for ax in g.axes.flat:
        for label in ax.get_xticklabels():
            label.set_rotation(45)

    plt.tight_layout()
    plt.show()