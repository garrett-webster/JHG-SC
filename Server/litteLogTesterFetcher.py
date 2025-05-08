from graphMaker import graphMaker


if __name__ == '__main__':
    curr_maker = graphMaker()
    # this is an idividual round below.
    #filename = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\Server\logs_repo\individual_round\ scenariosomewhatMoreAwareGreedygroups-1round8cycle2.json"

    # this is a big picture
    filename = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\Server\logs_repo\big_picture\ scenariosomewhatMoreAwareGreedygroups-1.json"

    #curr_maker.individual_round(filename)
    curr_maker.big_picture(filename)