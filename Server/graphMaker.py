# the purpose of this thing is to repurpose the json logs and turn them into something that makes sense. Will likely be leveraging a crap ton of code from
# the offlineSim graphers. lets get it.
import json
from offlineSimStuff.variousGraphingTools.causeNodeGraphVisualizer import causeNodeGraphVisualizer

class graphMaker():
    def __init__(self):
        pass

    def individual_round(self, file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)

        currentVisualizer = causeNodeGraphVisualizer()
        currentVisualizer.create_graph_given_file(data)