from graphMaker import graphMaker
import json

if __name__ == '__main__':
    curr_maker = graphMaker()
    # this is an idividual round below.
    #filename = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\Server\sc_logs_repo\individual_round\ scenariosomewhatMoreAwareGreedygroups-1round8cycle2.json"

    # human results time # these are already exactly where they need to be. don't mess with them, I don't think.
    # filepath = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\offlineSimStuff\human_results_time\human_study_results.json"
    # with open(filepath, 'r') as f:
    #     data = json.load(f)
    #
    # # aight so data is everything SO
    # for curr_round in data:
    #     if curr_round != "Conclusion":
    #         print("this is the curr_round we are passing in from up here ", curr_round)
    #         curr_maker.individual_round_from_dict(data[curr_round])
    #     else:
    #         curr_maker.big_picture_from_dict(data[curr_round])


    filepath = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\offlineSimStuff\human_results_time\machine_comparison.json"
    with open(filepath, 'r') as f:
        data = json.load(f)

    # aight so data is everything SO
    for curr_round in data:
        if curr_round != "Conclusion":
            pass
            curr_maker.individual_round_from_dict(data[curr_round])
        else:
            curr_maker.big_picture_from_dict(data[curr_round])


