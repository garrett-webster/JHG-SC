import json
from offlineSimStuff.variousGraphingTools.causeNodeGraphVisualizer import causeNodeGraphVisualizer
from offlineSimStuff.variousGraphingTools.longTermGrapher import longTermGrapher
import os


def create_stuff(big_boy_data):
    little_visualizer = causeNodeGraphVisualizer()
    big_visualizer = longTermGrapher()


    for key in big_boy_data:
        if key != "Conclusion":
            pass
            little_visualizer.create_graph_given_file(big_boy_data[key])
        else:
            big_visualizer.draw_graph_from_file(big_boy_data[key])

    print("aight that should be everything boss!")



if __name__ == "__main__":

    # #in case you ever need it again, here is the code you like to use to look at where your current file path actually sends you
    # relative_path = "../../Server/sc_logs_repo"
    # absolute_path = os.path.abspath(relative_path)
    #
    # print("Relative path:", relative_path)
    # print("Resolved to:", absolute_path)
    # print("Exists?", os.path.exists(absolute_path))
    # directory = "../../Server/sc_logs_repo"
    # filename = "human_study_results.json"
    # filepath = os.path.join(directory, filename)
    filepath = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\offlineSimStuff\sc_logs_repo\machine_comparison.json"
    # so from here, I need to recreate the results fetcher
    # Iwaht I want to do is jsut run it so I can create a godo file parser for it, but I still need to wait for all the graphs to freakin delete.
    # so big_boy_round_data has
    # key --> all teh stuff needed for little round
    # so
    with open(filepath, 'r') as f:
        big_boy_data = json.load(f)

    create_stuff(big_boy_data)