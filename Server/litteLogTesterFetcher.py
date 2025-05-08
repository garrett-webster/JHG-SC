from graphMaker import graphMaker


if __name__ == '__main__':
    curr_maker = graphMaker()
    filename = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\Server\logs_repo\individual_round\ scenariosomewhatMoreAwareGreedygroups-1round8cycle2.json"
    curr_maker.individual_round(filename)