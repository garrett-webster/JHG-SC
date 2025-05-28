# the purpose of this program is to take in json and compare how close they are
# I think we should just focus on the comparison of votes between the two
# we will still need a way to custom set the current options matrix before every round
# from the other json
# so lets get it
import json
import textdistance

if __name__ == "__main__":

    human_result_file_path = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\offlineSimStuff\sc_logs_repo\20250523_140645human_study_results.json.json"
    machine_result_file_path = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\offlineSimStuff\sc_logs_repo\machine_comparison.json"

    with open(human_result_file_path, 'r') as f:
        human_data = json.load(f)

    with open(machine_result_file_path, 'r') as f:
        machine_data = json.load(f)


    #ok lets flatten these votes
    flattened_old_votes = []
    flattened_new_votes = []
    for round in human_data:
        if round == "Conclusion":
            for vote in human_data[round]:
                flattened_new_votes.append(str(human_data[round][vote]))
                flattened_old_votes.append(str(machine_data[round][vote]))

    #distance = textdistance.levenshtein.distance(flattened_old_votes, flattened_new_votes) # distance doesn't make any sense in this context. here for reference only.
    similarity = textdistance.levenshtein.normalized_similarity(flattened_old_votes, flattened_new_votes)

    print("old ", flattened_old_votes)
    print("new ", flattened_new_votes)

    print(f"Normalized similarity: {similarity:.2f}")