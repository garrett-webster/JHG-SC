import matplotlib.pyplot as plt
import numpy as np
import os


class longTermGrapher():
    def __init__(self):
        pass # don't do anything




    def draw_graph(self, sim):
        results, cooperation_score, bot_type, num_rounds = sim.get_results()

        sums_per_round = {}
        for bot in results:
            sums_per_round[bot] = []
            current_sum = 0
            for i, new_sum in enumerate(results[bot]):
                current_sum += new_sum
                sums_per_round[bot].append(current_sum)

        new_list = []
        for bot in sums_per_round:
            new_list.append(sums_per_round[bot][num_rounds - 1])
        std = np.std(new_list)
        mean = np.mean(new_list)
        cv = std / abs(mean)  # measures distribution bet  ter than, say, std or mean on their own.

        cooperation_score = cooperation_score / num_rounds  # as a percent, how often we cooperated. (had a non negative cause pass)

        # Prepare the x-axis (rounds)
        rounds = range(num_rounds)  # just generates a list so we can zip with it later

        # total score per round (for the black line)
        total_scores_per_round = [sum(results[player][round_num] for player in results) for round_num in rounds]

        # average score per round, by using the total score and num playres.
        num_players = len(results)  # Number of players (bots)
        average_scores_per_round = [total_score / num_players for total_score in total_scores_per_round]

        # cum average score and total score increase
        cumulative_average_score = [sum(average_scores_per_round[:i + 1]) for i in range(len(average_scores_per_round))]
        total_average_increase = cumulative_average_score[-1] / num_rounds

        # print statements go here.
        print("this was the total average increase ", total_average_increase)
        print("this was the cooperatino score ", cooperation_score)
        print("this was the cv ", cv)

        # create da plot
        plt.figure(figsize=(10, 6))

        # goes through that big ol fetcher and plots all the polayer socres per round
        for player, scores_list in sums_per_round.items():
            plt.plot(rounds, scores_list, marker='o', label=f'Player {player}')

        plt.plot(rounds, cumulative_average_score, marker='x', label='Cumulative Total Score', linewidth=3,
                 color='black')

        plt.text(0.95, 0.90, f'Coefficient of Variation: {cv:.2f}',
                 # should display the average standard deviation as well.
                 horizontalalignment='right', verticalalignment='top',
                 transform=plt.gca().transAxes, fontsize=12, color='black', weight='bold')

        plt.text(0.95, 0.95, f'Avg Increase: {total_average_increase:.2f}',
                 horizontalalignment='right', verticalalignment='top',
                 transform=plt.gca().transAxes, fontsize=12, color='black', weight='bold')

        plt.text(0.95, 0.85, f'Cooperation Score: {cooperation_score:.2f}',
                 # should display the average standard deviation as well.
                 horizontalalignment='right', verticalalignment='top',
                 transform=plt.gca().transAxes, fontsize=12, color='black', weight='bold')

        # labels and a title
        plt.xlabel('Round')
        plt.ylabel('Score')
        plt.title('Scores per Round for Each Player With Algorithm ' + str(bot_type))
        plt.legend()

        # I would like to see the baby
        plt.grid(True)
        plt.tight_layout()

        bot_name = ""
        if bot_type == 1:
            bot_name = "Pareto"
        if bot_type == 2:
            bot_name = "Greedy"
        if bot_type == 3:
            bot_name = "Random"
        if bot_type == 4:
            bot_name = "betterGreedy"
        if bot_type == 5:
            bot_name = "limitedAwarenessGreedy"

        # what we are naming this new graph
        file_name = str(bot_name)
        # where do we put him.
        directory = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\offlineSimStuff\Graphs"
        # directory = r"C:\Users\Sean\Documents\GitHub\IJCAI2024_SM\Code\GeneSimulation_py\Server\Graphs"

        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, f"{file_name}.png")

        plt.savefig(file_path, dpi=300, bbox_inches='tight')  # save the fetcher
        #plt.show()