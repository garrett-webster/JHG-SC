class stagHareLogger:
    def __init__(self):
        self.information = []

    def add_information(self, agent_types, coop_score, scores_per_player, cabAgentType):
        new_information_object = informationObject(agent_types, coop_score, scores_per_player, cabAgentType)
        self.information.append(new_information_object)


class informationObject():
    def __init__(self, agent_types, coop_score, scores_per_player, cabAgentType):
        self.agent_types = agent_types
        self.coop_score = coop_score
        self.scores_per_player = scores_per_player
        self.cabAgentType = cabAgentType