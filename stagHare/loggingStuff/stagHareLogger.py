import numpy as np

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

    def __str__(self):
        return (f"informationObject(scenario_type={self.scenario_type}, "
                f"coop_score={self.coop_score}, "
                f"hunters={self.hunters}, "
                f"hare_intent_percent_total={self.hare_intent_percent_total})")


class BigBatchLogger():
    def __init__(self, height, width, agent_names, scenario_type):
        self.height = height
        self.width = width
        self.agent_names = agent_names
        self.scenario_type = scenario_type
        self.coop_scores = []
        self.score_per_player = []
        self.hare_intent_percent_total = []
        self.hare_intent_percent_player = []
        self.popularity_over_time = []

    def add_game(self, new_game: informationObject):
        self.coop_scores.append(new_game.coop_score)
        self.score_per_player.append(new_game.scores_per_player)
        self.hare_intent_percent_total.append(new_game.hare_intent_percent_total)
        self.hare_intent_percent_player.append(new_game.hare_intent_percent_player)
        self.popularity_over_time.append(new_game.popularity_over_time[-1]) # make sure to just get the ending popularities.

    # processing stuff. Make this single purpose, big ol logger.
    def get_batch_results(self):
        coop_scores = np.mean(self.coop_scores)
        # first find the new mean, make it a list, and then normalize it.
        score_per_player = (np.mean(self.score_per_player, axis=0) /
            np.mean(self.score_per_player, axis=0).sum(axis=1, keepdims=True)).tolist()
        assert len(score_per_player) == len(self.agent_names) # BARS
        hare_intent_percent_total = np.round(np.mean(self.hare_intent_percent_total), 3)
        # for this, we need a ranking system. this is gonna suck.
        popularity_over_time = self.get_popularity_over_time_ranking()
        print("here are the coop scores ", coop_scores)
        print("here ar ethe scores per plaeyr ", score_per_player)
        print("here is the hare percent total ", hare_intent_percent_total, " and here is the pop over time ", popularity_over_time)
        return coop_scores, score_per_player, hare_intent_percent_total, popularity_over_time # I think thats a good baseline.

    def get_popularity_over_time_ranking(self):
        list = [0 for _ in range(len(self.agent_names))]
        for entry in self.popularity_over_time:
            list[np.argmax(entry)] += 1

        return list




