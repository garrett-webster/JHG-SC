# this script just lets me test drive various JHG Genes, becuase I can't seem to get them to make any sense.

from tqdm import tqdm

import matplotlib.pyplot as plt
from Client.combinedLayout.ui_functions.StudyScripts.network import NodeNetwork # just for graphing the influence matrix node edges.
from matplotlib.collections import LineCollection
from matplotlib.colors import to_rgba
from offlineSimStuff.runningTools.runnerHelper import * # get all the functions


# starts the sim, could make this take command line arguments
# takes in a bot type, a number of rounds, and then runs it and plots the results. plans for expansion coming soon.
def run_trial_graphing(agents, sc_sim: "Social_Choice_Sim", jhg_sim, round_list, num_cycles, group, total_order, pops, round_logger, create_round_graphs_bool, game_logger, create_game_graphs_bool, current_jhg_sim, peep_constant):

    sc_sim.set_group(group)
    played_sc = False
    played_jhg = False
    curr_sc_round = 0
    influence_matrix = None # this should get overwritten pretty quick, but its there so there's no error.
    for list_index in (range(0, len(round_list))): # fixed, we start at 0 now.

        sc_rounds = round_list[list_index][-1] == "*"
        jhg_rounds = round_list[list_index][-1] == "-"
        curr_round = int(round_list[list_index][:-1]) # useful, yes, but not quite the logger round
        # print("this si the curr round ", curr_round)

        # print("*****************************ROUND ", curr_round, "********************************")

        if jhg_rounds:
            influence_matrix = run_jhg_stuff(jhg_sim, curr_round, agents, len(agents), current_jhg_sim)
            played_jhg = True
            pops.append(jhg_sim.get_popularity())
            # print("influence for round ", curr_round, " is \n", influence_matrix)



        if sc_rounds:
            influence_matrix, winning_vote = run_sc_stuff(sc_sim, jhg_sim.get_popularity(), total_order, influence_matrix, curr_round, num_cycles, peep_constant)
            sc_sim.set_rounds(curr_sc_round) # ???
            curr_sc_round += 1
            played_sc = True
            jhg_sim.set_new_influence(influence_matrix) # overrides the current influence matrix wiht the new one. The ONLY real way that we can have backwash.

        round_logger.save_round(curr_round, sc_rounds, jhg_rounds)


        if create_round_graphs_bool:
            create_round_graphs(round_logger, curr_round, sc_rounds, jhg_rounds)

    if create_game_graphs_bool:
        game_logger.save_game(played_sc, played_jhg)
        create_game_graphs(game_logger)

    return sc_sim, jhg_sim, pops


def draw_jhg_graphs(num_players, num_rounds, b, pops, jhg_cv, jhg_influence, avg_pop_per_round, bot_types, agent_name):
    # aight we might need to draw two different graphs, lets find out.

    pop_graph = True
    num_graphs = int(pop_graph)
    num_graphs += 2  # param graph, num_graphs, influence graph

    pops = list(zip(*pops))

    # Set up figure and axes
    import matplotlib.gridspec as gridspec

    fig = plt.figure(figsize=(7 * num_graphs, 6))
    gs = gridspec.GridSpec(1, num_graphs, width_ratios=[0.3] + [1] * (num_graphs - 1))  # First one narrower

    axes = [fig.add_subplot(gs[i]) for i in range(num_graphs)]
    current_axis = 0

    # SET UP PARAM GRAPH

    params = {
        "Agent_Name": agent_name,
        "bot_types \n": wrap_list(bot_types, items_per_line=4),
        "JGH_GAME:": pop_graph,
        "num_rounds:": num_rounds,
        "num_players:": num_players,
    }

    ax = axes[current_axis]
    ax.axis('off')  # Hide the frame for a clean text panel
    ax.text(0, 1.05, "Parameters", fontsize=14, fontweight='bold', va='bottom')
    text_lines = [f"{k} {v}" for k, v in params.items()]
    ax.text(0, 1, "\n".join(text_lines), va='top', ha='left', fontsize=12, family='monospace')
    current_axis += 1

    color_library = {
        -3: "purple",  # these are the sc pure cats.
        -2: "orange",  # my improved(?) cat agents
        -1: "red",  # standard cat agents
        0: "blue",  # Gene3agnets and variants
        1: "green",  # humans
    }

    if pop_graph:
        jhg_rounds = range(0, len(avg_pop_per_round))
        ax = axes[current_axis]

        for i, player_scores in enumerate(pops):

            label = f'P{i + 1}'
            ax.plot(jhg_rounds, player_scores, label=label, color=color_library[bot_types[i]])  # may


        ax.plot(jhg_rounds, avg_pop_per_round, color='black', linewidth=3, label='Avg')

        ax.set_title('Average Popularity Over Time', loc="left")
        ax.set_xlabel('Round')
        ax.set_ylabel('Popularity')
        ax.legend()
        ax.grid(True)

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
            f'CoV: {jhg_cv:.2f}',
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

    # plt.suptitle(f"Scenario: {scenario} | Group: {group or 'No Group'} | Chromosome: {chromosome}", fontsize=14)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    init_pop = 100
    init_pops = [init_pop for _ in range(int(num_players))]
    ax = axes[current_axis]
    curr_influence = jhg_influence  # one of em is in there, just gotta find which one.
    plot_influence_graph(ax, curr_influence, init_pops)

    plt.show()
    plt.close(fig)

def draw_jhg_graphs_wrapper(sim):
    # num_players, num_rounds, b, pops, jhg_cv, jhg_influence, avg_pop_per_round, bot_types, agent_name = sim.num_players, sim.num_rounds, sim.get_b()

    num_players = sim.num_players
    num_rounds = len(sim.game_popularities) # MAYBE???
    b = sim.get_b()
    pops = sim.game_popularities # we might need to go through round by round which would suck.
    cv = sim.get_cv()
    influence = sim.get_influence()
    avg_pop_per_round = sim.avg_pop_per_round
    bot_types = sim.bot_types
    agent_names = sim.agent_names

    draw_jhg_graphs(num_players, num_rounds, b, pops, cv, influence, avg_pop_per_round, bot_types, agent_names)



def run_jhg_graphing(jhg_sim, graphing, num_rounds):

    for curr_round in range(num_rounds):

        jhg_sim.execute_round(curr_round)
        print("Here is the influence \n", jhg_sim.get_influence())

    if graphing:
        draw_jhg_graphs_wrapper(jhg_sim)

    pass

def wrap_list(lst, items_per_line=5):
    return '\n'.join(
        ', '.join(str(x) for x in lst[i:i + items_per_line])
        for i in range(0, len(lst), items_per_line)
    )

def plot_influence_graph(ax, influence_matrix, popularity):
    influence_matrix = normalize_matrix(np.array(influence_matrix)) # might want to get rid of this?
    # this section was trying to  help me understnad how clustered the fetcher was. I have since removed it, but you can stick it back in if you so desire.
    # node_clustering, global_clustering = OpsahlClustering(np.array(influence_matrix)) # leave the alpha at 0.5 rn

    net = NodeNetwork()
    net.setupPlayers([f"{i}" for i in range(np.shape(popularity)[0])])
    net.initNodes(
        init_pops=popularity)  # not sure if this is actually getting used the way that I think its getting used, but we are sure trying.
    net.update(influence_matrix, popularity)

    node_positions = np.array([node.position[-1] for node in net.nodes])
    # ax is already defined
    ax.set_aspect("equal")
    ax.axis("off")
    for i, (x, y) in enumerate(node_positions):
        ax.scatter(x, y, s=150, edgecolors="none", zorder=2)
        ax.text(x, y, str(i+1), fontsize=10, ha="center", va="center", color="black", zorder=3)

    min_weight = np.min(np.abs(influence_matrix))
    max_weight = np.max(np.abs(influence_matrix))

    def get_edge_color_and_opacity(weight):
        if max_weight != min_weight:
            normalized = (abs(weight) - min_weight) / (max_weight - min_weight)
        else:
            normalized = 0
        color = (0, 1, 0) if weight > 0 else (1, 0, 0)
        alpha = normalized
        return color, alpha

    segments = []
    colors = []
    for i, node in enumerate(net.nodes):
        for j, weight in enumerate(influence_matrix[
                                       i]):  # yeah I think this will graph to much, I htink I need to do this at just the mcfreakin uhh curr Round.

            if weight != 0:
                x0, y0 = node_positions[i]
                x1, y1 = node_positions[j]

                color, alpha = get_edge_color_and_opacity(weight)

                segments.append([(x0, y0), (x1, y1)])
                colors.append(to_rgba(color, alpha))

    lc = LineCollection(segments, colors=colors, zorder=1)
    ax.add_collection(lc)
    ax.set_title('Final Influence Matrix', loc="left")

def normalize_matrix(matrix):
    max_val = np.max(matrix)
    if max_val == 0:
        return matrix  # All zeros? No change.
    return matrix / max_val



if __name__ == "__main__":

    import random
    # import numpy as np
    #

    # Uncomment this to freeze the seed for better comparison
    # SEED = 42  # pick any constant
    #
    # random.seed(SEED)  # Python’s stdlib RNG
    # np.random.seed(SEED)  # NumPy’s RNG

    jhg_games_per_sc_round = ["J", 30]
    # jhg_games_per_sc_round = ["S", 30]
    forcedRandom = True # TRUE uses the list, so thats cool.
    enforce_majority = True # what we used in the other fetcher.
    random_agents = True # HAVE THIS SET TO TRUE UNLESS YOU HAVE A REALLY GOOD REASON NOT TOO

    round_list = determine_rounds(jhg_games_per_sc_round)


    num_humans = 0
    create_round_graphs_bool = False
    create_game_graphs_bool = True
    create_influence = True

    # cat_scenario = "2SCKitties"
    # these paths are relative to the file location, so as long as you don't move the file it can and will run from anywhere.
    jhg_bot_type = 0 # 0 is gene bots, 2 is social welfare and 3 is random. 4 is the new social welfare that I am developing that is just a hair smarter.

    num_attempts = 1 # number of batches to do.
    # num_vanilla_bots = num_players - num_humans
    # bot_types = [jhg_bot_type for _ in range(num_vanilla_bots)]

    # for individual testing
    graphing = True
    num_rounds = 30
    # just start here.
    # agent_name_list = ["new3Gene", "new3Gene", "new3Gene", "new3Gene", "new3Gene", "new3Gene", "new3Gene", "new3Gene", "new3Gene", "new3Gene"]
    # agent_name_list = ["new3Gene", "new3Gene", "new3Gene"]
    # agent_name_list = ["ECab199","ECab199","ECab199", "ECab199","ECab199","ECab199","ECab199","ECab199","ECab199","ECab199"]
    # agent_name_list = ["HCab", "HCab", "HCab", "HCab", "HCab", "HCab", "HCab", "HCab", "HCab", "HCab"]
    agent_name_list = ["HCab","HCab","HCab"]
    # agent_name_list = ["ECab3","ECab3","ECab3"]
    # agent_name_list = ["ECab3","ECab3","ECab3","ECab3","ECab3","ECab3","ECab3","ECab3","ECab3","ECab3"]
    # agent_name_list = ["CCab","CCab","CCab","CCab","CCab","CCab","CCab","CCab","CCab","CCab"]
    # agent_name_list = ["HardHomo", "HardHomo", "HardHomo", "HardHomo", "HardHomo", "HardHomo", "HardHomo", "HardHomo", "HardHomo", "HardHomo"]
    # agent_name_list = ["CCab","CCab","CCab"]
    # agent_name_list = ["NCab", "NCab", "NCab", "NCab", "NCab", "NCab", "NCab", "NCab", "NCab", "NCab"]
    # agent_name_list = ["NCab", "NCab", "NCab"]

    agents = create_agents_with_list(agent_name_list, forcedRandom, random_agents)

    # I JUST want to run bots here. Don't worry about humans -- this rewrites a few assumptions.
    for attempt in tqdm(range(num_attempts)): # create a new sim for each attempt to prevent bleeding over.
        # all I want to do is as follows: pass in a list of agents, run it through a jhg sim, and return the pops one some level.
        new_pops = [] # this might be a bad way to do this.

        new_simulator = create_jhg_sim_stripped(agents, forcedRandom) # thats literally it.
        run_jhg_graphing(new_simulator, graphing, num_rounds)


