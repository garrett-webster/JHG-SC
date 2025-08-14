class PopularityOverTime():
    def __init__(self, jhg_sim):
        self.jhg_sim = jhg_sim


    def draw_graph_from_sim(self):
        popularites = self.jhg_sim.get_popularity()
        self.draw_graph(popularites)


    def draw_graph(self, popularites):
        pass # I haven't implemented this yet. work on it more when you have the json format that garrett is working on.

