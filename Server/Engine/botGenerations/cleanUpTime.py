import csv
import os
import glob

from collections import defaultdict


data_dir = "MelissasGenes.csv"

generation_stats = {}


if __name__ == "__main__":
    num_genes_new = 33
    num_genes_old = 40
    file_path = r"C:\Users\Sean Smith\Documents\GitHub\JHG-SC\Server\Engine\botGenerations\MelissasGenes.csv"
    all_new_genes = []
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            words = row[0].split("_")
            old_world = words.pop(0)
            new_gene = ""
            for i in range(3): # num gene pools
                for j in range(40): # going through all the old genes
                    if j <= 33:
                        index = j + (i*j)
                        new_gene += "_" + str((words[index]))
                    else:
                        pass
            new_string = "genes_" + new_gene
            all_new_genes.append(new_string)
    print("here are the new genes \n", all_new_genes)





