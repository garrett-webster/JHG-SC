import csv
import os
import glob

from collections import defaultdict


data_dir = "../../../legacy/old_bot_generations/MelissasGenes.csv"

generation_stats = {}


if __name__ == "__main__":
    num_genes_new = 33
    num_genes_old = 40
    num_pools = 3
    file_path = r"/legacy/old_bot_generations/MelissasGenes.csv"
    all_new_genes = []
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            words = row[0].split("_")
            old_world = words.pop(0)  # assuming first element is a label
            new_gene = ""
            for i in range(num_pools):
                for j in range(num_genes_new):  # only up to 33
                    index = i * num_genes_old + j  # correct indexing across pools
                    new_gene += "_" + str(words[index])
            new_string = "genes" + new_gene
            all_new_genes.append(new_string)

    print("here are the new genes \n", all_new_genes)





