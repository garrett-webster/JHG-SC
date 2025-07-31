class InfluenceEngine():
    def __init__(self, num_players):
        self.N = num_players

        ## current round number
        self.t = 0

        ## historical transaction matrices
        self.T = []
        self.T.append(np.zeros((self.N, self.N)))

        ## influence matrices
        self.I = []
        self.I.append(np.eye(self.N))  # i = influences => j

