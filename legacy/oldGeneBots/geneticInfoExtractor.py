import csv
import os
import glob

from collections import defaultdict


data_dir = "../oldGeneTraining/longerConvexResults/theGenerations"

generation_stats = {}


if __name__ == "__main__":
    pattern = os.path.join(data_dir, "gen_*.csv")
    print("looking for files iwth patterh ", pattern)
    for filepath in glob.glob(os.path.join(data_dir, "gen_*.csv")):
        try:
            gen_num = int(os.path.basename(filepath).split("_")[1].split(".")[0])
        except (IndexError, ValueError):
            continue # don't do anything about it yet.

        rel_utilities = []
        abs_utilities = []

        with open(filepath, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) < 4:
                    continue  # Skip short/bad rows
                try:
                    # to have it parse POPS instead of UTIL, use 4 and 5
                    rel_util = float(row[4])  # Relative Utility
                    abs_util = float(row[5])  # Absolute Utility
                    rel_utilities.append(rel_util)
                    abs_utilities.append(abs_util)
                except ValueError:
                    continue # skip bad or missing rows

        if rel_utilities and abs_utilities:
            avg_rel = sum(rel_utilities) / len(rel_utilities)
            avg_abs = sum(abs_utilities) / len(abs_utilities)
            generation_stats[gen_num] = (avg_rel, avg_abs)


    print("Generation | Avg relative utiliyt | Avg absolute utiliyt")
    print("___________|______________________|_____________________")
    for gen, (avg_rel, avg_abs) in sorted(generation_stats.items(), key=lambda item: item[1][1], reverse=True):
        print(f"{gen:10} | {avg_rel:20.4f} | {avg_abs:20.4f}")