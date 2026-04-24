class stagHareLogger:
    def __init__(self):
        self.game_information = []
        # self.batch_information = []

    def add_information_game(self, agent_scenario, cooperation_score, scores_per_player, agent_name,
                             hare_intent_percent_total, hare_intent_percent_player, positions_list,
                             popularity_over_time, hunters, height, width, intents):

        new_information_object = informationObject(agent_scenario, cooperation_score, scores_per_player, agent_name,
                                                   hare_intent_percent_total, hare_intent_percent_player,
                                                   positions_list, popularity_over_time, hunters, height, width, intents)
        self.game_information.append(new_information_object)

    def get_game_information(self):
        return self.game_information

    # def add_batch_information(self, batch_information):
    #     self.batch_information.append(batch_information)


class informationObject():

    # scenario_type, cooperation_score, scores_per_player, agent_names, hare_intent_percent_total, hare_intent_percent_player, agent_positions, popularity_over_time, hunters, height, width, intents)

    def __init__(self, scenario_type, coop_score, scores_per_player, agent_names, hare_intent_percent_total, hare_intent_percent_player, agent_positions, popularity_over_time, hunters, height, width, intents):
        self.scenario_type = scenario_type
        self.coop_score = coop_score
        self.scores_per_player = scores_per_player
        self.agent_names = agent_names
        self.hare_intent_percent_total = hare_intent_percent_total
        self.hare_intent_percent_player = hare_intent_percent_player
        self.position_history = agent_positions
        self.popularity_over_time = popularity_over_time
        self.hunters = hunters
        self.height = height
        self.width = width
        self.hare_hunting_history = intents



class BatchInformation():
    def __init__(self, agent_types, coop_score, scores_per_player, cabAgentType):
        pass