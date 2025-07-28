def create_graphs_with_file(self, file_path):
    # so the JSON saves everything and this is sort fo supposed to get called round by round
    # so breaking this down might be a little weird.
    with open(file_path, "r") as f:
        data = json.load(f)

    for curr_round in data:
        if "JHG_STUFF" in data[curr_round]:
            jhg = data[curr_round].get("JHG_STUFF")
            allocations, popularity, influence, old_popularity = self.extract_keys(jhg, ["T", "Popularity", "Influence",
                                                                                         "Old_Popularity"])
            self.create_jhg_graphs(allocations, popularity, influence, curr_round, old_popularity)
        if "SC_STUFF" in data[curr_round]:
            sc = data[curr_round].get("SC_STUFF")
            all_nodes, all_votes, winning_vote_list, current_options_matrix, types_list, scenario, group, curr_round, cycle, chromosome, influence_matrix, results_sums, results, peeps = (
                self.extract_keys(sc, ["all_nodes", "all_votes", "winning_vote", "current_options_matrix", "types_list",
                                       "scenario", "group", "curr_round", "cycle", "chromosome", "influence_matrix",
                                       "results_sums", "results", "peeps"]))
            self.create_sc_graphs(all_nodes, all_votes, winning_vote_list, current_options_matrix, types_list, scenario,
                                  group, curr_round, cycle, chromosome, influence_matrix, results_sums, results, peeps)



    def create_graph_with_sims(self, curr_round, sc_sim, jhg_sim, sc_played, jhg_played):
        if jhg_played:# very important that this comes first, as we alwas PLAY this one first, makes sure the graphs are printed in the right order. for now. might need to adjust some stuff.
            allocations, popularity, influence, old_popularity = jhg_sim.individual_round_deets_for_logger(curr_round)
            self.create_jhg_graphs(allocations, popularity, influence, curr_round, old_popularity)

        if sc_played:
            all_nodes, all_votes, winning_vote_list, current_options_matrix, types_list, scenario, group, round, cycle, chromosome, influence_matrix, results_sums, results, peeps = sc_sim.prepare_graph()
            self.create_sc_graphs(all_nodes, all_votes, winning_vote_list, current_options_matrix, types_list, scenario,  group, round, cycle, chromosome, influence_matrix, results_sums, results, peeps)

    def extract_keys(self, d, keys, default=None):
        return tuple(d.get(k, default) for k in keys)



    def build_bot_mappings(self):
        bot_color_map = {
            # -1 is player, 0 is random, 1 is socialWelfare, 2 is greediest, 3 is betterGreedy, 4 is limitedAwareness, 5 is secondChoice
            "-1": "lightgreen",
            "0": "purple",
            "1": "black",
            "2": "purple",
            "3": "blue",
            "4": "orange",
            "5": "plum",
            "6": "lightblue",
            "7": "darkgreen",
            "8": "green",
            "9": "orange",
            "10": "violet",
            "default": "gray"
        }

        bot_name_map = {
            "-1": "player",
            "0": "random",
            "1": "socialWelfare",
            "2": "Greedy",
            "3": "betterGreedy",
            "4": "limitedAwareness",
            "5": "secondChoice",
            "6": "somewhatMoreAwareness",
            "7": "optimalHuman",
            "8": "humanAttempt2",
            "9": "humanAttempt3",
            "10": "cheetahBot",
        }
        return bot_color_map, bot_name_map

    def draw_long_term_graphs_given_logger(self, current_logger):
        num_attempts = current_logger.big_boy_data["CONCLUSION"]["num_attempts"]
        num_players = current_logger.big_boy_data["CONCLUSION"]["num_players"]
        avg_rise = current_logger.big_boy_data["CONCLUSION"]["SC_CONCLUSION"][0][
            "avg_rise"] if current_logger.sc_sim else 0
        b = current_logger.big_boy_data["CONCLUSION"]["JHG_CONCLUSION"][0]["b"] if current_logger.jhg_sim else 0
        avg_pop_per_round, per_player_per_round, avg_utility_per_round, utility_per_player_per_round = current_logger.calculate_long_term_stats()
        jhg_bot_type, sc_bot_type, allocation_bot_types = current_logger.get_all_bot_types()
        cooperation_score, number_of_attempts, cv, influence = (
            self.get_coop_score(current_logger) if current_logger.sc_sim else (0, 0, 0, 0))
        jhg_cv_score = self.get_cv_score(current_logger) if current_logger.jhg_sim else 0
        self.draw_two_long_graphs(avg_pop_per_round, per_player_per_round, avg_utility_per_round,
                                  utility_per_player_per_round, jhg_bot_type, sc_bot_type, allocation_bot_types,
                                  cooperation_score, number_of_attempts, cv, jhg_cv_score, num_attempts, influence,
                                  num_players, avg_rise, b)

    def draw_long_term_graphs_given_file(self, file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
        num_attempts = data["CONCLUSION"]["num_attempts"]
        num_players = data["CONCLUSION"]["num_players"]
        dict_to_pass = data["CONCLUSION"]["LONG_TERM_DATA"]
        dict_to_check = data["CONCLUSION"]
        avg_rise = dict_to_check["SC_CONCLUSION"][0]["avg_rise"] if "SC_CONCLUSION" in dict_to_check else 0
        b = dict_to_check["JHG_CONCLUSION"][0]["b"] if "JHG_CONCLUSION" in dict_to_check else 0
        complete_logger = CompleteLogger()
        avg_pop_per_round, per_player_per_round, avg_utility_per_round, utility_per_player_per_round = complete_logger.get_long_term_stats_from_dict(
            dict_to_pass)
        jhg_bot_type, sc_bot_type, allocation_bot_types = complete_logger.get_bot_types_from_json(data["CONCLUSION"])
        cooperation_score, number_of_attempts, cv, influence = self.get_coop_score_from_file(data)
        jhg_cv_score = self.get_cv_score_from_file(data)
        self.draw_two_long_graphs(avg_pop_per_round, per_player_per_round, avg_utility_per_round,
                                  utility_per_player_per_round, jhg_bot_type, sc_bot_type, allocation_bot_types,
                                  cooperation_score, number_of_attempts, cv, jhg_cv_score, num_attempts, influence,
                                  num_players, avg_rise, b)




    def draw_two_long_graphs(self, avg_pop_per_round, per_player_per_round, avg_utility_per_round, utility_per_player_per_round,
                             jhg_bot_type, sc_bot_type, allocation_bot_types, cooperation_score, number_of_attempts, cv, jhg_cv_score,
                             num_attempts, influence, num_players, avg_rise, b_one):
        # aight we might need to draw two different graphs, lets find out.

        pop_graph = avg_pop_per_round is not None and len(avg_pop_per_round) > 0
        util_graph = avg_utility_per_round is not None and len(avg_utility_per_round) > 0
        num_graphs = int(pop_graph) + int(util_graph)
        plot_influence = number_of_attempts == 1 and influence is not None
        if plot_influence:
            num_graphs += 1

        # I could put the starting amounts in there by hand and trace it all the way down or just accept that they are likely to never change.
        if not plot_influence:
            avg_rise_utility = ((avg_utility_per_round[-1] - 10)) / len(avg_utility_per_round) if avg_utility_per_round else 0
        else:
            avg_rise_utility = avg_rise


        sc_bot_name_map = {
            "-1": "player",
            "0": "random",
            "1": "sW",
            "2": "G",
            "3": "bG",
            "4": "lA",
            "5": "sC",
            "6": "sMA",
            "7": "hA1",
            "8": "hA2",
            "9": "hA3",
            "10": "cH",
        }

        allocation_bot_name_map = {
            "-1": "player",
            "0": "random",
            "1": "sW",
            "2": "G"

        }

        jhg_bot_name_map = {
            "0" : "GA3",
            "1" : "player",
            "2" : "sW",
            "3" : "random"
        }

        jhg_rounds = range(1, len(avg_pop_per_round)+1)

        # Set up figure and axes
        fig, axes = plt.subplots(1, num_graphs, figsize=(7 * num_graphs, 6))
        if num_graphs == 1:
            axes = [axes]  # Make it iterable
        current_axis = 0

        # -- determining line of best fit for JHG
        if pop_graph:
            ax = axes[current_axis]
            if plot_influence:
                for i, player_scores in enumerate(per_player_per_round):
                    bot_type_id = jhg_bot_type[i] if i < len(jhg_bot_type) else "?"
                    bot_type_name = jhg_bot_name_map.get(str(bot_type_id), f"Bot {bot_type_id}")
                    label = f'P{i + 1} ({bot_type_name})'
                    ax.plot(jhg_rounds, player_scores, label=label)

            ax.plot(jhg_rounds, avg_pop_per_round, color='black', linewidth=3, label='Avg Popularity')
            ax.set_title('Average Popularity Over Time', loc="left")
            ax.set_xlabel('Round')
            ax.set_ylabel('Popularity')
            ax.legend()
            ax.grid(True)

            # Fit exponential model for population
            if not plot_influence:
                starting_pop = 100
                log_ratio = np.log(np.array(avg_pop_per_round) / starting_pop)
                b = np.dot(jhg_rounds, log_ratio) / np.dot(jhg_rounds, jhg_rounds) if jhg_rounds else 0
            else:
                b = b_one

            # add the average increase in pop and utility as part of the legend.
            ax.text(
                0.5, 1.05,  # x, y in axis coordinates
                f'Exp. fit vars: {b:3e}',
                transform=ax.transAxes,
                ha='center',
                va='bottom',
                fontsize=12,
                color='black',
                weight='bold'
            )
            ax.text(
                0.1, -0.15,  # x, y in axis coordinates
                f'CoV: {jhg_cv_score:.2f}',
                transform=ax.transAxes,
                ha='center',
                va='bottom',
                fontsize=12,
                color='black',
                weight='bold'
            )
            current_axis += 1


        else:
            b = 0

        # ---- Utility Graph ----
        if util_graph:

            ax = axes[current_axis]
            sc_rounds = range(1, len(avg_utility_per_round) + 1)
            if plot_influence:
                for i, player_scores in enumerate(utility_per_player_per_round):
                    bot_type_id = sc_bot_type[i] if i < len(sc_bot_type) else "?"
                    alloc_bot_type_id = allocation_bot_types[i] if i < len(allocation_bot_types) else "?"
                    bot_type_name = sc_bot_name_map.get(str(bot_type_id), f"Bot {bot_type_id}")
                    alloc_type_name = allocation_bot_name_map.get(str(alloc_bot_type_id), f"Alloc {alloc_bot_type_id}")
                    label = f'P{i + 1} ({bot_type_name} {alloc_type_name})'
                    ax.plot(sc_rounds, player_scores, label=label)

            ax.plot(sc_rounds, avg_utility_per_round, color='black', linewidth=3, label='Avg Utility')
            ax.set_title('Average Utility Over Time', loc="left")
            ax.set_xlabel('Round')
            ax.set_ylabel('Utility')
            ax.legend()
            ax.grid(True)

            current_axis += 1

            # Add text to right plot (utility)

            ax.text(
                0.5, 1.05,  # x, y in axis coordinates
                f'Avg Rise (Util): {avg_rise_utility:.2f}',
                transform=ax.transAxes,
                ha='center',
                va='bottom',
                fontsize=12,
                color='black',
                weight='bold'
            )

            # add the coop score as text to bottom right
            ax.text(
                0.8, -0.15,  # Bottom center of the axis
                f"coop_score: {cooperation_score:.2f}",
                transform=ax.transAxes,
                ha="center",
                va="top",
                fontsize=12,
                color="black",
                weight="bold",
            )

            ax.text(
                0.1, -0.15,  # Left bottom of axis
                f"CoV: {cv:.2f}",
                transform=ax.transAxes,
                ha="center",
                va="top",
                fontsize=12,
                color="black",
                weight="bold",
            )


        # plt.suptitle(f"Scenario: {scenario} | Group: {group or 'No Group'} | Chromosome: {chromosome}", fontsize=14)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])

        fig.text(
            0.5, 0.95,
            f"no. of attempts: {number_of_attempts}",
            ha="center",
            va="bottom",
            fontsize=12,
            color="black",
            weight="bold",
        )

        if plot_influence:
            init_pop = 10 if util_graph and not pop_graph else 100
            init_pops = [init_pop for _ in range(num_players)]
            ax = axes[current_axis]
            self.plot_influence_graph(ax, influence, init_pops)



        # # Save the figure
        # my_path = os.path.dirname(os.path.abspath(__file__))
        # scenario_str = f"scenario_{scenario}"
        # group_str = f"group_{group or 'NoGroup'}"
        # dir_path = os.path.join(my_path, "popularityUtilityGraphs", scenario_str, group_str)
        # os.makedirs(dir_path, exist_ok=True)
        #
        # file_name = f"PopularityUtility_Chromosome_{chromosome}.png"
        # file_path = os.path.join(dir_path, file_name)
        # plt.savefig(file_path, dpi=300)


        plt.show()



    def get_coop_score(self, current_logger):
        new_dict = current_logger.get_coop_data()
        new_sum = 0
        new_cv_sum = 0
        new_dict_keys = new_dict.keys()
        last_attempt = None
        for attempt in new_dict_keys:
            new_sum += new_dict[attempt]["cooperation_score"]
            new_cv_sum += new_dict[attempt]["cv"]
            last_attempt = attempt
        new_sum = new_sum / len(new_dict_keys)
        new_cv_sum = new_sum / len(new_dict_keys)
        influence = new_dict[last_attempt]["influence"] # yeah this doesn't make any sense, don't think about it too hard rn
        # get the new influence in here while we are here
        # fetch it we are going to get the CV while we are in here


        return new_sum, len(new_dict_keys), (new_cv_sum / len(new_dict_keys)), influence








    def get_coop_score_from_file(self, data):
        new_dict = data["CONCLUSION"]["SC_CONCLUSION"]
        new_sum = 0
        new_cv_sum = 0
        new_dict_keys = new_dict.keys()
        last_attempt = None
        for attempt in new_dict_keys:
            new_sum += new_dict[attempt]["cooperation_score"]
            new_cv_sum += new_dict[attempt]["cv"]
            last_attempt = attempt
        new_sum = new_sum / len(new_dict_keys)
        influence = new_dict[last_attempt]["influence"]
        return new_sum, len(new_dict_keys), (new_cv_sum / len(new_dict_keys)), influence








    def get_cv_score(self, current_logger):
        new_dict = current_logger.get_jhg_cv_data()
        new_sum = 0
        new_dict_keys = new_dict.keys()
        for attempt in new_dict_keys:
            new_sum += new_dict[attempt]["cv"]
        new_sum = new_sum / len(new_dict_keys)
        return new_sum # this is the new cv

    def get_cv_score_from_file(self, data):
        new_dict = data["CONCLUSION"]["JHG_CONCLUSION"]
        new_sum = 0
        new_dict_keys = new_dict.keys()
        for attempt in new_dict_keys:
            new_sum += new_dict[attempt]["cv"]
        new_sum = new_sum / len(new_dict_keys)
        return new_sum  # this is the new cv