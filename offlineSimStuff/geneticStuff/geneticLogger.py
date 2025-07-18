import json
import dataclasses
import os # useful for creating directory paths

# custom encoder that can deal with the custom data struct thing
class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


"""
This genetic logger is based loosely off of the pre-existing JHG genetic logger, but formated for my own needs.
Will this work? is it even a good idea? who knows! But we are going to give it a whirl anyway.
"""
class geneticLogger():

    def __init__(self):
        self.genetic_data = {}
        self.generation = -1 # should never happen

    def start_generation(self, generation):
        self.genetic_data = {} # clears out the fetcher
        self.generation = generation

    def save_round(self, pmetrics, generation):
        print("this is the pmetrics object, ", pmetrics, " and this is the generatyion ", generation)
        filename = "gen" + str(generation) # could make this more explicit but this is a goo dplace to start
        base_dire = os.path.dirname(os.path.abspath(__file__))
        relative_path = os.path.join(base_dire, "geneticLogs", filename + ".json")
        os.makedirs(os.path.dirname(relative_path), exist_ok=True)

        with open(relative_path, "w") as f:
            json.dump(pmetrics, f, cls=EnhancedJSONEncoder) # bars