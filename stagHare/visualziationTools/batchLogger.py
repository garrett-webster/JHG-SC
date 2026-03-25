class BatchLogger():
    def __init__(self):
        pass
        self.results = 0 # log whether they got a stag or hare.
        self.attempts = 0


    def add_game(self, stag_hare):

        self.attempts += 1

        if not stag_hare.state.hare_captured():
            self.results += 1



    def get_results(self):
        return self.results / self.attempts # this is a ratio of how often they went for the stag vs the hare.
        # the higher this number, the more they went for the stag (which in my head is the better behavior, but thats just me)