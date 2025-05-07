class simLogger:
    def __init__(self, current_sim):
        self.sim = current_sim

    def record_round(self):
        current_node_json, final_votes, winning_vote, current_options_matrix, bots, results, cooperation_score, bot_type, num_rounds = self.sim.get_everything_for_logger()