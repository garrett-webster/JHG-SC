
def loadPopulationFromFile(theFolder, startIndex, popSize, numGeneCopies):
    for i in range(popSize):
        #open the file, get the file, etc. 



if __name__ == "__main__":
    #./jhgsim evolve ../Results/theGenerations 100 3 0 100 100 10 30 0 basicConfig varied
    # using the default arguments from the ijacai documentation.
    theFolder = "SomeFolder"
    popSize = 100
    numGeneGopies = 3
    startIndex = 0
    num_gens = 100
    numAgents = 100
    numRounds = 10
    roounds_per_game = 30
    poverty_line = 0
    config = "basicConfig"
    lastFetcher = "varied" # I have no real clue what this is doing.
    theGenePools_odl = loadPopulationFromFile(theFolder, startIndex-1, popSize, numGeneCopies)