class stagHareLogger:
    def __init__(self):
        self.game_information = []
        self.batch_information = []

    def add_information_game(self, agent_scenario, cooperation_score, scores_per_player, agent_name, hare_intent_percent_total, hare_intent_percent_player):
        new_information_object = informationObject(agent_scenario, cooperation_score, scores_per_player, agent_name, hare_intent_percent_total, hare_intent_percent_player)
        self.game_information.append(new_information_object)

    def get_game_information(self):
        return self.game_information

    def add_batch_information(self, batch_information):
        self.batch_information.append(batch_information)


class informationObject():
    def __init__(self, agent_types, coop_score, scores_per_player, cabAgentType, hare_intent_percent_total, hare_intent_percent_player):
        self.agent_types = agent_types
        self.coop_score = coop_score
        self.scores_per_player = scores_per_player
        self.cabAgentType = cabAgentType
        self.hare_intent_percent_total = hare_intent_percent_total
        self.hare_intent_percent_player = hare_intent_percent_player


class BatchInformation():
    def __init__(self, agent_types, coop_score, scores_per_player, cabAgentType):
        pass