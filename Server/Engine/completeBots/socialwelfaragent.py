from Server.Engine.completeBots.baseagent import AbstractAgent


class SocialWelfareAgent(AbstractAgent):

    def __init__(self, tokens_per_player):
        super().__init__()
        self.whoami = "SocialWelfare"
        self.tokens_per_player = tokens_per_player
        self.pop_history = []  # just slap this up here.
        self.gameParams = {}


    def setGameParams(self, gameParams, _forcedRandom):
        self.gameParams = gameParams


    def getType(self):
        return self.whoami


    def play_round(self, player_idx, round_num, received, popularities, influence, extra_data):
        numPlayers = len(received)
        transaction_vector = [self.tokens_per_player] * numPlayers
        return transaction_vector

