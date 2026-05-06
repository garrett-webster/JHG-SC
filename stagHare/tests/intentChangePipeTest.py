"""
the goal of this script is to make a JHG engine that can run
and then from there, I can test the allocations and whatnot from that JHG script to try and understand intent
I want to see if the staghunt_to_jhg function is broken or what.
steps: get just a jhg game running and make sure it works
track the allocations
run them through the thing, track intents
measure with various bots.
break.
"""
from tqdm import tqdm
from offlineSimStuff.runningTools.runnerHelper import * # get all the functions
from Server.Engine.simulator import GameSimulator
from stagHare.environment.jhgToStaghunt import allocation_to_movement, allocation_to_intent
import json
import os
from tqdm import tqdm

from stagHare.loggingStuff.stagHareLogger import GameInformationResultsCompiler
from concurrent.futures import ProcessPoolExecutor, as_completed
from stagHare.runnerHelper import *  # this SHOULD be all we need.


def flatten_and_remove_nulls(nested_list, null_value=[2, 2, 2]):
    """
    Flatten a deeply nested list, removing null values.
    Returns a flat list of all non-null values.
    """
    flat = []

    for item in nested_list:
        if isinstance(item, list):
            if item == null_value:
                continue  # Skip null values
            # Recursively flatten
            flat.extend(flatten_and_remove_nulls(item, null_value))
        else:
            flat.append(item)

    return flat


def subtract_lists(pre_intents, post_intents, null_value=[2, 2, 2]):
    """
    Flatten both lists, remove nulls, and subtract pre from post.
    Returns the differences as a flat list.
    """
    pre_flat = flatten_and_remove_nulls(pre_intents, null_value)
    post_flat = flatten_and_remove_nulls(post_intents, null_value)

    # Ensure they're the same length
    if len(pre_flat) != len(post_flat):
        print(f"Warning: Different lengths after flattening! Pre: {len(pre_flat)}, Post: {len(post_flat)}")
        # Truncate to shorter length
        min_len = min(len(pre_flat), len(post_flat))
        pre_flat = pre_flat[:min_len]
        post_flat = post_flat[:min_len]

    # Element-wise subtraction
    differences = [post - pre for post, pre in zip(post_flat, pre_flat)]

    return differences


def analyze_intent_changes(pre_intents, post_intents):
    """
    Analyze how intents changed from pre to post.
    """
    differences = subtract_lists(pre_intents, post_intents)

    if not differences:
        print("No valid data to compare")
        return

    # Count changes
    increased = sum(1 for d in differences if d > 0)
    decreased = sum(1 for d in differences if d < 0)
    unchanged = sum(1 for d in differences if d == 0)
    total = len(differences)

    print(f"Total non-null intent values: {total}")
    print(f"Increased (post > pre): {increased} ({increased / total * 100:.1f}%)")
    print(f"Decreased (post < pre): {decreased} ({decreased / total * 100:.1f}%)")
    print(f"Unchanged: {unchanged} ({unchanged / total * 100:.1f}%)")
    print(f"Mean change: {np.mean(differences):.3f}")
    print(f"Max increase: {max(differences)}, Max decrease: {min(differences)}")

    return differences

if __name__ == "__main__":
    bots = [["gen_Z.csv", "gen_Z.csv", "gen_Z.csv"], ["gen_199.csv", "gen_199.csv", "gen_199.csv"]]
    forcedRandom = True
    enforce_majority = True
    random_agents = True

    num_players = 3
    num_humans = 0

    height = 16
    width = 16
    forced_random = False
    RandomAgent = True
    scenario_type = ["SelfPlay"]
    GamesPerRound = 10
    graphing = False

    jhg_bot_type = 0
    num_vanilla_bots = 10

    bot_types = [jhg_bot_type for _ in range(num_vanilla_bots)]
    popularity_to_log = []
    num_attempts = 100
    total_order = create_total_order(num_players,
                                     num_humans)  # unfortunately we have to make that in here now just bc we are changing the num players
    add_agents = [] # make this empty.
    num_rounds = 30
    intents = [[] for _ in range(num_players)] # creates a list of lists


    for bot in bots:
        print("Bot type ", bot)
        pre_intents = []
        post_intents = []
        for attempt in tqdm(range(num_attempts)):
            # how many resources can we actually devote to this??
            max_workers = max(1, os.cpu_count() - 2)  # save just a few for other processes, plz don't crash.
            # max_workers = 1 # spawns only a single thread, simplifying debugging.
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for attempt in range(num_attempts):
                    futures.append(
                        executor.submit(run_trial_all_debugging, bot, height, width, random_agents, forced_random,
                                        scenario_type, GamesPerRound, graphing))

                for future in as_completed(futures):
                    pre_intents.append(future.result()[0])
                    post_intents.append(future.result()[1])
                    # results.append(future.result())


            # assert(len(pre_intents[0]) == len(post_intents[0]))
        analyze_intent_changes(pre_intents, post_intents)