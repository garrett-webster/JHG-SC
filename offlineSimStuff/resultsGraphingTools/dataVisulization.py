import pandas as pd
import json
import ast  # to safely evaluate the list strings
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from IPython.core.pylabtools import figsize
from pytz.reference import first_sunday_on_or_after
import os
from offlineSimStuff.runningTools.runnerHelper import get_file_names
from itertools import product

def extract_lists(curr_dict):
    new_utilities_list = []
    new_popularity_list = []

    for key, subdf in curr_dict.items():
        all_utils = []
        for entry in subdf["UtilityLog"]:
            if isinstance(entry, list):
                for data in entry:
                    all_utils.append(data)
        all_pops = []
        for entry in subdf["PopularityLog"]:
            if isinstance(entry, list):
                for data in entry:
                    all_pops.append(data)

        new_utilities_list.append(all_utils)
        new_popularity_list.append(all_pops)

    return new_utilities_list, new_popularity_list


def prepare_graphing_data(data_list, peep_constants):
    """Converts a list of lists into tuples of (peep_constant, associated_list)"""
    graphing_data = []
    for i, constant in enumerate(peep_constants):
        graphing_data.append((constant, data_list[i]))
    return graphing_data


def plot_8_boxplots_separate_ylim(dataset_names, datasets_util, datasets_pop, peep_constants, figsize=(20, 10)):
    """
    Plots 8 boxplots in a single figure: 4 columns x 2 rows.
    Top row: utilities
    Bottom row: popularities
    Each row has its own global y-limits.
    """
    fig, axes = plt.subplots(2, 4, figsize=figsize)
    fig.suptitle("Peep Constant per Agent w/ Enforce Majority in Mixed")
    current_axes = axes.flatten()

    # --- Utilities global min/max ---
    util_values_flat = [val for dataset in datasets_util for inner_lists in dataset for inner in inner_lists for val in
                        inner]
    util_y_min = min(util_values_flat)
    util_y_max = max(util_values_flat)

    # --- Popularities global min/max ---
    pop_values_flat = [val for dataset in datasets_pop for inner_lists in dataset for inner in inner_lists for val in
                       inner]
    pop_y_min = min(pop_values_flat)
    pop_y_max = max(pop_values_flat)

    # Plot utilities (top row)
    for i, (name, dataset) in enumerate(zip(dataset_names, datasets_util)):
        graphing_data = prepare_graphing_data(dataset, peep_constants)
        boxplot_data = []
        labels = []
        for peep, lists in graphing_data:
            flat_values = [val for inner_list in lists for val in inner_list]
            boxplot_data.append(flat_values)
            labels.append(peep)
        current_axes[i].boxplot(boxplot_data, tick_labels=labels)
        current_axes[i].set_title(f"Utilities {name}")
        current_axes[i].set_ylim(util_y_min, util_y_max)

    # Plot popularities (bottom row)
    for i, (name, dataset) in enumerate(zip(dataset_names, datasets_pop)):
        graphing_data = prepare_graphing_data(dataset, peep_constants)
        boxplot_data = []
        labels = []
        for peep, lists in graphing_data:
            flat_values = [val for inner_list in lists for val in inner_list]
            boxplot_data.append(flat_values)
            labels.append(peep)
        current_axes[i + 4].boxplot(boxplot_data, tick_labels=labels)  # offset by 4 for second row
        current_axes[i + 4].set_title(f"Popularities {name}")
        current_axes[i + 4].set_ylim(pop_y_min, pop_y_max)

    plt.tight_layout()
    plt.show()


def flatten(nested):
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item

def create_jhg_stuff(subsets, directory):
    pure_jhg = subsets

    filtered_pure_jhg = pure_jhg[pure_jhg["EnforceMajority"] == True]

    homo = filtered_pure_jhg[filtered_pure_jhg["AgentType"] == "homoJHGSelfPlay.csv"]["PopularityLog"]
    mixed = filtered_pure_jhg[filtered_pure_jhg["AgentType"] == "mixedJHGSelfPlay.csv"]["PopularityLog"]

    flat_values_homo = list(flatten(homo))
    flat_values_mixed = list(flatten(mixed))

    max_value = max(max(flat_values_homo), max(flat_values_mixed))
    min_value = min(min(flat_values_homo), min(flat_values_mixed))

    fig, axes = plt.subplots(1, 2)
    fig.suptitle("Agent Performance in Pure JHG")
    current_axes = axes.flatten()

    current_axes[0].boxplot(flat_values_homo)
    current_axes[0].set_title("HomoSelfPlay")
    current_axes[0].set_ylim(min_value, max_value)

    current_axes[1].boxplot(flat_values_mixed)
    current_axes[1].set_title("MixedSelfPlay")
    current_axes[1].set_ylim(min_value, max_value)


    # for graph in new_list

    filepath = os.path.join(directory, "JHGPureReults.png")
    plt.savefig(str(filepath), dpi=300, bbox_inches="tight")

    plt.show()

def create_sc_stuff(subsets, directory):
    pure_sc = subsets


    pure_sc_true = pure_sc[pure_sc["EnforceMajority"] == True]
    pure_sc_false = pure_sc[pure_sc["EnforceMajority"] == False]


    homo_true = pure_sc_true[pure_sc_true["AgentType"] == "homoJHGSelfPlay.csv"]["UtilityLog"]
    homo_false = pure_sc_false[pure_sc_false["AgentType"] == "homoJHGSelfPlay.csv"]["UtilityLog"]


    mixed_true = pure_sc_true[pure_sc_true["AgentType"] == "mixedJHGSelfPlay.csv"]["UtilityLog"]
    mixed_false = pure_sc_false[pure_sc_false["AgentType"] == "mixedJHGSelfPlay.csv"]["UtilityLog"]

    fig, axes = plt.subplots(1, 4, figsize=(15, 5))
    fig.suptitle("Agents and Enforce Majority in Pure SC")
    current_axes = axes.flatten()


    homo_true_flat = list(flatten(homo_true))
    homo_false_flat = list(flatten(homo_false))

    mixed_true_flat = list(flatten(mixed_true))
    mixed_false_flat = list(flatten(mixed_false))

    min_val = min(
        min(homo_true_flat),
        min(homo_false_flat),
        min(mixed_true_flat),
        min(mixed_false_flat)
    )

    max_val = max(
        max(homo_true_flat),
        max(homo_false_flat),
        max(mixed_true_flat),
        max(mixed_false_flat)
    )


    current_axes[0].boxplot(homo_true_flat)
    current_axes[0].set_title("homo_true")
    current_axes[0].set_ylim(min_val, max_val)

    current_axes[1].boxplot(homo_false_flat)
    current_axes[1].set_title("homo_false")
    current_axes[1].set_ylim(min_val, max_val)

    current_axes[2].boxplot(mixed_true_flat)
    current_axes[2].set_title("mixed_true")
    current_axes[2].set_ylim(min_val, max_val)

    current_axes[3].boxplot(mixed_false_flat)
    current_axes[3].set_title("mixed_false")
    current_axes[3].set_ylim(min_val, max_val)

    filepath = os.path.join(directory, "SCPureReults.png")
    plt.savefig(str(filepath), dpi=300, bbox_inches="tight")
    plt.show()

def create_mixed_stuff(subsets, directory):
    mixed = subsets

    mixed_true = mixed[mixed["EnforceMajority"] == True]
    mixed_false = mixed[mixed["EnforceMajority"] == False]


    homo_true = mixed_true[mixed_true["AgentType"] == "homoJHGSelfPlay.csv"]
    homo_false = mixed_false[mixed_false["AgentType"] == "homoJHGSelfPlay.csv"]

    mixed_true = mixed_true[mixed_true["AgentType"] == "mixedJHGSelfPlay.csv"]
    mixed_false = mixed_false[mixed_false["AgentType"] == "mixedJHGSelfPlay.csv"]

    peep_values = mixed_true["PeepConstant"].unique()  # get all unique peep values

    homo_true_dict = {}
    for p in peep_values:
        homo_true_dict[p] = homo_true[homo_true["PeepConstant"] == p].copy()

    homo_false_dict = {}
    for p in peep_values:
        homo_false_dict[p] = homo_false[homo_false["PeepConstant"] == p].copy()

    mixed_true_dict = {}
    for p in peep_values:
        mixed_true_dict[p] = mixed_true[mixed_true["PeepConstant"] == p].copy()

    mixed_false_dict = {}
    for p in peep_values:
        mixed_false_dict[p] = mixed_false[mixed_false["PeepConstant"] == p].copy()

    peep_constants = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    homo_true_utilities, homo_true_popularities = extract_lists(homo_true_dict)
    homo_false_utilities, homo_false_popularities = extract_lists(homo_false_dict)

    mixed_true_utilities, mixed_true_popularities = extract_lists(mixed_true_dict)
    mixed_false_utilities, mixed_false_popularities = extract_lists(mixed_false_dict)

    dataset_names = ["Homo True", "Homo False", "Mixed True", "Mixed False"]
    plot_8_boxplots_separate_ylim(
        dataset_names,
        datasets_util=[homo_true_utilities, homo_false_utilities, mixed_true_utilities, mixed_false_utilities],
        datasets_pop=[homo_true_popularities, homo_false_popularities, mixed_true_popularities,
                      mixed_false_popularities],
        peep_constants=peep_constants
    )

    filepath = os.path.join(directory, "MixedResults.png")
    plt.savefig(str(filepath), dpi=300, bbox_inches="tight")


def generalized_graphing_code(subset, scenario_name):

    agent_types = subset["AgentType"].unique()
    enforce_majority = subset["EnforceMajority"].unique()
    peep_constants = subset["PeepConstant"].unique()

    possible_logs = ["UtilityLog", "PopularityLog"]

    available_logs = [col for col in possible_logs if col in subset.columns] # this line feels weird, idk what it does

    for log_col in available_logs:
        if subset[log_col].apply(lambda x: len(x) == 0 if isinstance(x, list) else True).all():
            print("skipping this col bc its all empty ", log_col)
            continue

        data_to_plot = []
        labels = []

        for agent_type, enforced, peep_const in product(agent_types, enforce_majority, peep_constants):
            filtered = subset[
                (subset["AgentType"] == agent_type) &
                (subset["EnforceMajority"] == enforced) &
                (subset["PeepConstant"] == peep_const)
            ]
            flat_values = list(flatten(filtered[log_col]))
            if len(flat_values) == 0:
                continue # this should never happen but allas here we are
            if enforced == True:
                new_char = "T"
            elif enforced == False:
                new_char = "F"

            coop_score = filtered["CoopToLog"].iloc[0]
            if isinstance(coop_score, float):
                coop_score = round(coop_score, 4) # round it to 4 digits.;

            label = f"{agent_type} E:{new_char} Pc: {peep_const} \n Coop: {coop_score}"
            data_to_plot.append(flat_values)
            labels.append(label)

        if data_to_plot:
            plt.figure(figsize=(12, 6), dpi=450)
            plt.boxplot(data_to_plot, tick_labels=labels, widths=0.2)
            plt.title(f"{scenario_name} - {log_col} - {enforced}")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()

            # filename = f"{scenario_name}_{log_col}.png"
            # filepath = os.path.join(directory, filename)
            # plt.savefig(str(filepath), dpi=1000, bbox_inches="tight")
            # plt.close()
            # print(f"saved to {filepath}")
        else:
            print("NO VALID DATA CHEIF")

def get_file_paths(directory):
    file_names = get_file_names(directory)
    file_directories = [os.path.join(directory, x) for x in file_names]
    return file_directories



if __name__ == "__main__":

    # file_path = "../simulationResults/thirdRun/simulation_results.csv"
    # need to make the super csv
    for i in range(2):

        converters = {
            "UtilityLog": json.loads,  # this should making loading the list of lists better.
            "PopularityLog": json.loads,
            "RoundType": json.loads,
            "CoopToLog": json.loads,
        }

        # file_directory = r"C:\Users\Sean Smith\Documents\GitHub\JHG-SC\offlineSimStuff\resultsGraphingTools\burned\results2actual"
        file_directory_1 = r"C:\Users\Sean Smith\Documents\GitHub\JHG-SC\offlineSimStuff\resultsGraphingTools\burned\results4actual"
        file_paths_1 = get_file_paths(file_directory_1)
        dfs_1 = [pd.read_csv(df, converters=converters) for df in file_paths_1]

        file_directory_2 = r"C:\Users\Sean Smith\Documents\GitHub\JHG-SC\offlineSimStuff\resultsGraphingTools\burned\optimalHuman"
        file_paths_2 = get_file_paths(file_directory_2)
        dfs_2 = [pd.read_csv(df, converters=converters) for df in file_paths_2]

        all_dfs = dfs_1 + dfs_2


        df = pd.concat(all_dfs, ignore_index=True)

        if i == 0:
            df = df[df.EnforceMajority != True] # drop some stuff
        else:
            df = df[df.EnforceMajority == True]

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
        scenario_names = []
        for round_variant in df["RoundType"].unique():
            subsets.append(df[df["RoundType"] == round_variant])
            scenario_names.append(round_variant)


        # uncomment this out once you get it working
        # Get the absolute path to the directory containing this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # filepath = os.path.join(script_dir, file_directory)
        # filepath = os.path.join("../..", filepath)

        # directory = os.path.dirname(filepath)

        # os.makedirs(directory, exist_ok=True)
        #
        for i, subset in enumerate(subsets):
            # feel free to add the directory back in later if you so desire.
            generalized_graphing_code(subset, scenario_names[i])



    # create_jhg_stuff(subsets[0], directory)
    # create_sc_stuff(subsets[1], directory)
    # create_mixed_stuff(subsets[2], directory)


