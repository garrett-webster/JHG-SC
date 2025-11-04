import pandas as pd
import json
import ast  # to safely evaluate the list strings
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from pytz.reference import first_sunday_on_or_after


def extract_lists(df_dict):
    all_utilities = []
    all_popularities = []

    for df in df_dict.values():
        all_utilities.extend(df["UtilityLog"].tolist())
        all_popularities.extend(df["PopularityLog"].tolist())

    return all_utilities, all_popularities


def create_jhg_stuff(subsets):
    pure_jhg = subsets[1]

    filtered_pure_jhg = pure_jhg[pure_jhg["EnforceMajority"] == True]

    # still beign pissy, idk why.

    homo = filtered_pure_jhg[filtered_pure_jhg["AgentType"] == "homoSelfPlay.csv"]["PopularityLog"]
    mixed = filtered_pure_jhg[filtered_pure_jhg["AgentType"] == "mixedSelfPlay.csv"]["PopularityLog"]

    fig, axes = plt.subplots(1, 2)
    current_axes = axes.flatten()

    current_axes[0].boxplot(homo)
    current_axes[0].set_title("HomoSelfPlay")
    current_axes[0].set_ylim(105,135)

    current_axes[1].boxplot(mixed)
    current_axes[1].set_title("MixedSelfPlay")
    current_axes[1].set_ylim(105,135)

    plt.show()

def create_sc_stuff(subsets):
    pure_sc = subsets[0]


    pure_sc_true = pure_sc[pure_sc["EnforceMajority"] == True]
    pure_sc_false = pure_sc[pure_sc["EnforceMajority"] == False]


    homo_true = pure_sc_true[pure_sc_true["AgentType"] == "homoSelfPlay.csv"]["UtilityLog"]
    homo_false = pure_sc_false[pure_sc_false["AgentType"] == "homoSelfPlay.csv"]["UtilityLog"]


    mixed_true = pure_sc_true[pure_sc_true["AgentType"] == "mixedSelfPlay.csv"]["UtilityLog"]
    mixed_false = pure_sc_false[pure_sc_false["AgentType"] == "mixedSelfPlay.csv"]["UtilityLog"]

    fig, axes = plt.subplots(1, 4, figsize=(15, 5))
    current_axes = axes.flatten()

    current_axes[0].boxplot(homo_true)
    current_axes[0].set_title("homo_true")
    current_axes[0].set_ylim(8, 24)

    current_axes[1].boxplot(homo_false)
    current_axes[1].set_title("homo_false")
    current_axes[1].set_ylim(8, 24)

    current_axes[2].boxplot(mixed_true)
    current_axes[2].set_title("mixed_true")
    current_axes[2].set_ylim(8, 24)

    current_axes[3].boxplot(mixed_false)
    current_axes[3].set_title("mixed_false")
    current_axes[3].set_ylim(8, 24)

    plt.show()


if __name__ == "__main__":

    # just trust the system on the file pathD
    df = pd.read_csv("subsetForFormatting/simulation_results.csv")

    df.to_excel("my_data.xlsx", index=False)  # index=False to skip row numbers

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

    # this creates the 3 unique variations that we have.
    df["RoundType"] = df["RoundType"].apply(lambda x: "_".join(map(str, x)) if isinstance(x, list) else x)
    # so now I want to create 3 different graphs, depending on the scenario
    subsets = []
    for round_variant in df["RoundType"].unique():
        subsets.append(df[df["RoundType"] == round_variant])

    # create_jhg_stuff(subsets)
    # create_sc_stuff(subsets)

    mixed = subsets[2]


    mixed_true = mixed[mixed["EnforceMajority"] == True]
    mixed_false = mixed[mixed["EnforceMajority"] == False]


    homo_true = mixed_true[mixed_true["AgentType"] == "homoSelfPlay.csv"]
    homo_false = mixed_false[mixed_false["AgentType"] == "homoSelfPlay.csv"]

    mixed_true = mixed_true[mixed_true["AgentType"] == "mixedSelfPlay.csv"]
    mixed_false = mixed_false[mixed_false["AgentType"] == "mixedSelfPlay.csv"]

    peep_values = mixed_true["PeepConstant"].unique()  # get all unique peep values

    homo_true_dict = {}
    for p in peep_values:
        homo_true_dict[p] = homo_true[homo_true["PeepConstant"] == p]

    homo_false_dict = {}
    for p in peep_values:
        homo_false_dict[p] = homo_false[homo_false["PeepConstant"] == p]

    mixed_true_dict = {}
    for p in peep_values:
        mixed_true_dict[p] = mixed_true[mixed_true["PeepConstant"] == p]

    mixed_false_dict = {}
    for p in peep_values:
        mixed_false_dict[p] = mixed_false[mixed_false["PeepConstant"] == p]

    homo_true_utilities, homo_true_popularities = extract_lists(homo_true_dict)
    homo_false_utilities, homo_false_popularities = extract_lists(homo_false_dict)
    mixed_true_utilities, mixed_true_popularities = extract_lists(mixed_true_dict)
    mixed_false_utilities, mixed_false_popularities = extract_lists(mixed_false_dict)







    fig, axes = plt.subplots(1, 4, figsize=(15, 5))
    current_axes = axes.flatten()

    current_axes[0].boxplot(homo_true)
    current_axes[0].set_title("homo_true")
    current_axes[0].set_ylim(8, 24)

    current_axes[1].boxplot(homo_false)
    current_axes[1].set_title("homo_false")
    current_axes[1].set_ylim(8, 24)

    current_axes[2].boxplot(mixed_true)
    current_axes[2].set_title("mixed_true")
    current_axes[2].set_ylim(8, 24)

    current_axes[3].boxplot(mixed_false)
    current_axes[3].set_title("mixed_false")
    current_axes[3].set_ylim(8, 24)

    plt.show()


