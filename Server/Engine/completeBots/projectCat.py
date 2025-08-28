# purpose is to make these cats like
# actually viable within the SC thing.
# should be easier than trying to adapt the gene3 bot.
# lets find out.

from Server.Engine.completeBots.baseagent import AbstractAgent
import numpy as np
from Server.SC_Bots.transVecTranslator import translateVecToIndex



class ProjectCat(AbstractAgent):

    def __init__(self):
        super().__init__()
        self.whoami = 'jake cat'
        self.is_initialized = False
        self.the_assassins = {}
        self.attacks_by = None
        self.gives_by = None
        self.did_no_no = None
        self.attacks_on_me = 0.0
        self.gameParams = {}
        # completley made up btyw
        self.max_size = {
            1: 1,
            2: 1,
            3: 1,
            4: 1,
            5: 1,
            6: 2,
            7: 2,
            8: 2,
            9: 2,
            10: 1,
            11: 8,
            12: 9,
            13: 10,
        }

    def _init_vars(self, num_players):
        self.attacks_by = np.zeros(num_players)
        self.gives_by = np.zeros(num_players)
        self.did_no_no = np.array([False for _ in range(num_players)])
        self.the_assassins = {i for i in range(num_players)}
        self.attacks_on_me = 0.0

    def _update_vars(self, num_players, player_idx, influence, round_num):
        # print("here are the assassins going into this ", self.the_assassins)
        if round_num == 1: # this checks SPECIFICALLY for all 0 saved in the first round.
            to_remove = []
            for i in range(num_players):
                if i in self.the_assassins:
                    for j in range(num_players):
                        if i == j:
                            continue
                        else:
                            if influence[i][j] > 0:
                                to_remove.append(i)
            for i in range(num_players):
                if i in self.the_assassins and i in to_remove:
                    self.the_assassins.remove(i)


        else: # this one is more general, and checks for transactions between kitties and non kitties. anyone who gives to a non kitty
                # get a stick to the face.
            for i in range(num_players):
                self.attacks_by[i] = 0.0
                self.gives_by[i] = 0.0
                self.did_no_no[i] = False
                if i in self.the_assassins:
                    for j in range(num_players):
                        if i == j: # don't check self references, just gets weird.
                            continue

                        if influence[i][j] < 0.0: # if there has been an attack
                            self.attacks_by[i] -= influence[i][j] # make sure we can guard ourselves
                            if j in self.the_assassins: # if this was an attack on a fellow kitty
                                self.did_no_no[i] = True # he is no longer a brother.

                        # lets make it so that they can in fact give to other assassins.
                        elif influence[i][j] > 0.0: # if a "give" has taken place
                            self.gives_by[i] += influence[i][j]
                            if j not in self.the_assassins: # if he has given to a non assassin
                                self.did_no_no[i] = True # he is no longer a brother.

            for i in range(num_players): # iterate through and throw out all of the no no squares
                if i in self.the_assassins and (
                        self.did_no_no[i] or ((self.attacks_by[player_idx] > 0.0) and (self.attacks_by[i] == 0.0))):
                    # print("this is who we are removing ", i, " and this is why ", self.did_no_no[i], " ", (self.attacks_by[player_idx] > 0.0 and self.attacks_by[i] == 0))
                    self.the_assassins.remove(i)

    def _attacks_on_self(self, numPlayers, received, popularities):
        amount = 0.0
        for i in range(numPlayers):
            if received[i] < 0:
                amount += received[i] * popularities[i]

        return -amount

    def _get_my_proportion(self, player_idx):
        assassin_damage = 0.0
        for i in self.the_assassins:
            assassin_damage += self.attacks_by[i]

        return ((self.attacks_by[player_idx] + 0.000001) / (assassin_damage + 0.000001))

    def play_round(self, player_idx, round_num, recieved, popularities, influence, extra_data, extra_flag=False):
        # the extra flag does not matter to him, but it matters to teh other bots.
        #print("This is if we are playing SC ", extra_flag, " and here are the assassins ", self.the_assassins)

        if not extra_flag: # normal stuff
            allocations = self.jhg_kitty_behavior(player_idx, round_num, recieved, popularities, influence, extra_data)

        else:
            allocations = self.sc_kitty_behavior(player_idx, round_num, recieved, popularities, influence, extra_data)

        return allocations


    def sc_kitty_behavior(self, player_idx, round_num, recieved, popularities, influence, extra_data):
        # Don't allow the agent to update the init_vars or assassin list here, becuase it doesn't have the information it needs. just don't touch it.
        allocations = np.zeros_like(popularities)
        num_players = len(popularities)
        num_tokens = 2 * num_players

        if round_num == 0:  # save ALL ya tokens. simple as.
            self._init_vars(num_players)
            allocations[player_idx] = min(10, num_tokens)
            return allocations
        else:  # now we ahve to do like, actual math. bleh.

            prey_idxs = []
            prey_pop = -99999.0

            for i in range(num_players):
                if i not in self.the_assassins: # find the highest utility person to strike. gives a nice rotation system.
                    if len(prey_idxs) < num_players - len(self.the_assassins): # we are appending, sire.
                        prey_idxs.append(i)
                    else: # lets try rotation again just to see what happens.
                        for prey in prey_idxs:
                            if popularities[i] > popularities[prey] and i != prey and i not in prey_idxs: # this statement is starting to smell.
                                prey_idxs.remove(prey)
                                prey_idxs.append(i)


            if len(prey_idxs) != 0:  # just how bad can we mash them up
                # we can't take more than 10 from a person
                steal_tokens = 10 # we can always steal 10 https://www.reddit.com/r/MemeRestoration/comments/mqoiv7/its_morally_correct_requested_by_ujustvolted/
                for prey in prey_idxs:
                    allocations[prey] = -steal_tokens
                available_tokens = num_tokens + (steal_tokens * len(prey_idxs)) # utility works different here
                # split everyone into followers
                num_followers = num_players - len(self.the_assassins) - len(prey_idxs)
                total_allocation = (num_followers * 0.8) + len(self.the_assassins)
                if total_allocation == 0:
                    total_allocation = 0.0001
                allocation_tokens = available_tokens // total_allocation
                if allocation_tokens > 10:
                    allocation_tokens = 10

                for i in range(num_players):
                    if i in prey_idxs: # https://www.tiktok.com/@b0bch3rry_2/video/7485691586265926958
                        allocations[i] = -10
                    else: # friends! depends on by how much tho
                        if i in self.the_assassins: # big friend :)
                            allocations[i] = allocation_tokens
                        else: # we need them for tax purposes.
                            allocations[i] = allocation_tokens // 1.25 # make sure this is an integer.



            else:  # there is no prey, play social welfare with yo buddies. or something like that.
                # print("NO MORE PREY! GIVE TO FREN :)")
                allocations[player_idx] = num_tokens  # here we have no prey, so there is no one to attack
                num_tokens_to_allocate = num_tokens / (len(self.the_assassins))
                for i in self.the_assassins:
                    allocations[i] = num_tokens_to_allocate


            # allocations = (allocations / np.linalg.norm(allocations, ord=1)) * 2 * len(allocations)
            #allocations = self.adjust_for_sc(allocations, num_tokens)
            # print("this is the player idx ", player_idx, " and here is the allocation ", allocations)
            # if sum(allocations) < -50:
            #     print("hey something si wrong ", player_idx, " has an allocatino of ", allocations, " . on standby")
            return allocations  # return it to a more normal magnitude. # the engine doesn't care if its normalized or not, but the SC sim does care. deeply.

    # def adjust_for_sc(self, allocations, num_tokens):
    #     max_pos_sum = sum(x for x in allocations if x > 0)
    #     max_neg = min((x for x in allocations if x < 0), default=-1)  # most negative (smallest)
    #
    #     result = []
    #     for x in allocations:
    #         if x > 0:
    #             result.append(x / max_pos_sum)
    #         elif x < 0:
    #             result.append(-x / abs(max_neg) * -1)  # keep sign, scale between -1 and 0
    #         else:
    #             result.append(0)
    #
    #     # aight we do negatives first
    #     for i, x in enumerate(result):
    #         if x < 0:
    #             result[i] = x * 10 # max negative we can have is -10 and having it be the range should solve that
    #
    #     neg_sum = sum(x for x in allocations if x < 0) # get to the total negatives
    #     num_tokens -= neg_sum # increase the num tokens by that much
    #     # this is where stuff gets weird.
    #     # so we need to find the max allocation and scale that to 10, and then go from there
    #     for i, x in enumerate(result):
    #         if x > 0:
    #             result[i] = min(10, x * num_tokens)
    #     print("these are the results we are returning from the kitties ", result)
    #     return result

    def jhg_kitty_behavior(self, player_idx, round_num, recieved, popularities, influence, extra_data):

        allocations = np.zeros_like(popularities)
        num_players = len(popularities)
        num_tokens = 2 * num_players

        if round_num == 0: # save ALL ya tokens. simple as.
            self._init_vars(num_players)
            allocations[player_idx] = num_tokens
            return allocations
        else: # now we ahve to do like, actual math. bleh.
            alpha = self.gameParams.get('alpha', 0.15)
            steal_coef = self.gameParams.get('steal', 1.6)
            keep_coef = self.gameParams.get('keep', 0.95)

            self._update_vars(num_players, player_idx, influence, round_num) # try to figure out who the other kitties are.



            if popularities[player_idx] >= 0.5: # if we have more than half a rating point, nuke someone.
                attacked = self._attacks_on_self(num_players, recieved, popularities)
                w = 0.65
                self.attacks_on_me = w * attacked + (1 - w) * self.attacks_on_me
                keep_tokens = min((int)((self.attacks_on_me / popularities[player_idx]) + 0.5), num_tokens) # figure out how many people attacked me last round and try to plan accordinly

                prey_idx = None  # Changed from -1 cause python (This was weird)
                prey_pop = 99999.0
                attack_proportion = 0.0
                prop_assassin_attack = self._get_my_proportion(player_idx)
                attack_power = (popularities[player_idx] / prop_assassin_attack) * steal_coef * alpha # figure out how much power I am actually weilding
                for i in range(num_players):
                    if i not in self.the_assassins: # check all the non friends
                        # teh 2 is a magical little number, I assume its do the to the presencse of 2 cats but I can't actually confirm that.
                        if (popularities[i] < prey_pop) and (popularities[i] >= (attack_power / 2.0)): # can I actually take them out? Do I have the attack power and do they have low enough popularity?
                            prey_idx = i # pop them in my sights
                            prey_pop = popularities[i]
                            attack_proportion = min(popularities[i] / attack_power, 1.0) # calculate just how badly we will destroy them

                if prey_idx is not None: # just how bad can we mash them up

                    steal_tokens = (int)((attack_proportion * 0.9) * (num_tokens - keep_tokens))
                    allocations[prey_idx] = -steal_tokens
                    allocations[player_idx] = num_tokens - steal_tokens
                else: # this is what we need to change, her and here.
                        # we have no prey, so we give to our friends :)
                    new_tokens = (num_tokens - keep_tokens) // len(self.the_assassins)
                    for i in self.the_assassins:
                        allocations[i] = new_tokens
                    #allocations[player_idx] = num_tokens # here we have no prey, so there is no one to attack

            else:
                allocations[player_idx] = num_tokens # here there is no one WORTH attacking. big difference. # lets make social welfare here.

            # allocations = (allocations / np.linalg.norm(allocations, ord=1)) * 2 * len(allocations)
            return allocations # return it to a more normal magnitude. # the engine doesn't care if its normalized or not, but the SC sim does care. deeply.

    def setGameParams(self, gameParams, _forcedRandom):
        self.gameParams = gameParams
        self.forced_random = _forcedRandom

    def getType(self):
        return self.whoami

    def get_vote(self, player_idx, round_num, received, popularities, influence, extra_data, current_options_matrix, enforce_majority):
        transaction_vector = self.play_round(player_idx, round_num, received, popularities, influence, extra_data, True)
        final_vote = translateVecToIndex(transaction_vector, current_options_matrix, enforce_majority)
        return final_vote  # please let this work

