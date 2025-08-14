from Server.Engine.completeBots.baseagent import AbstractAgent
from Server.Engine.blackboard import BlackBoard  # get micheal to hand these over at some point and work with em when you can.
from Server.Engine.reversejhg import JHGReverse
from Server.Engine.engine import JHGEngine

import numpy as np
from copy import deepcopy
from time import time
from scipy.optimize import minimize, NonlinearConstraint
import warnings

from Server.SC_Bots.transVecTranslator import translateVecToIndex

# Suppress specific warning
warnings.filterwarnings('ignore', message='delta_grad == 0.0. Check if the approximated')


"""
kitty rules:
	1. no attacking other kitties
	2. victims are chosen as such:
		potential of lowering other kitty scores
		potential for increasing other kitty scores

		or rather
		choose the target that more decreases the potential damage that they could do with some kind of discount factor

		or rather
		attack the easiest target with lowest potential for damage should that node convert into an enemy node

		or rather
		determine the target that would decrease the relative power of the kitties most
			this would be a combination of attacking the weakest, least connected first while also determining how we want to handle other attackers on the cats
"""

def world_model(action, game_params, pred_func, opt_func, pred_args=(), opt_args=()):
    engine = JHGEngine(**game_params)

    T = pred_func(action, *pred_args)
    engine.apply_transaction(T)
    #print(f'{action} => {opt_func(engine.get_popularity(), engine.get_influence(), *opt_args)}')
    return opt_func(engine.get_popularity(), engine.get_influence(), *opt_args)

def row_sum_constraint(action):
    return np.ones_like(action) @ np.abs(action)

def row_sum_constraint_J(action):
    return np.sign(action)

class KittyAgent(AbstractAgent):

    PLAYER_CLASS_CAT = 'mow'
    PLAYER_CLASS_ENEMY = 'enemy'
    PLAYER_CLASS_FRIENDLY = 'friend'
    PLAYER_CLASS_OTHER = 'other'
    PLAYER_CLASS_UNKNOWN = 'unknown'
    PLAYER_CLASSES = [
        PLAYER_CLASS_CAT,
        PLAYER_CLASS_ENEMY,
        PLAYER_CLASS_FRIENDLY,
        PLAYER_CLASS_OTHER,
        PLAYER_CLASS_UNKNOWN
    ]


    def __init__(self, game_params={}, pay_taxes=False):
        super().__init__()
        self.pay_taxes = pay_taxes
        self.blackboard = BlackBoard()
        self.whoami = 'kitty_kat'
        self.class_weights = {
            self.PLAYER_CLASS_CAT: 100,
            self.PLAYER_CLASS_ENEMY: -100,
            self.PLAYER_CLASS_FRIENDLY: -5,
            self.PLAYER_CLASS_OTHER: -25,
            self.PLAYER_CLASS_UNKNOWN: -1000
        }
        self.game_params = game_params
        self.reverse_engine = JHGReverse(**self.game_params)

    def get_tokens(self, alpha, coef, targ_inf, pop):
        with np.errstate(divide='ignore', invalid='ignore'):
            tkns =  targ_inf / (alpha * pop * coef)
            if np.isscalar(tkns):
                if np.isnan(tkns) or np.isinf(tkns):
                    return 0.
            else:
                tkns[np.logical_or(np.isnan(tkns), np.isinf(tkns))] = 0.
        return tkns

    def rank(self, popularities, influences, player_classes, class_weights, player_idx):
        score = 0.
        my_influence = influences[player_idx]
        for cls in self.PLAYER_CLASSES:
            cls_ids = np.argwhere(player_classes == cls)
            if len(cls_ids) > 0:
                my_impact = np.sum(my_influence[cls_ids])
                pop_score = np.sum(popularities[cls_ids])
                score += class_weights[cls] * (pop_score * (cls != self.PLAYER_CLASS_UNKNOWN) + np.abs(my_impact) * (cls == self.PLAYER_CLASS_UNKNOWN))
        return -score

    def predict(self, action, prev_actions, player_classes, player_idx):
        T = np.eye(len(player_classes))
        for idx, cls in enumerate(player_classes):
            if idx == player_idx:
                T[idx] = action
            elif cls == self.PLAYER_CLASS_CAT:
                other_action = deepcopy(action)
                other_action[idx], other_action[player_idx] = other_action[player_idx], other_action[idx]
                T[idx] = other_action
            else:
                T[idx] = prev_actions[idx] if np.any(prev_actions[idx] != 0) else np.eye(len(player_classes))[idx]
        return T

    def setGameParams(self, game_params, placeholder):
        self.game_params = game_params
        self.reverse_engine = JHGReverse(**self.game_params)

    def class_partition(self, player_idx, round_num):
        infl_mat = self.blackboard.read(f'influence_{round_num}')
        prev_pop_vec = self.blackboard.read(f'popularities_{max(0, round_num - 1)}')
        extra_data = self.blackboard.read(f'extra_data_{round_num}')
        alpha = self.game_params.get('alpha', 0.2)
        steal_coef = self.game_params.get('steal', 1.6)
        keep_coef = self.game_params.get('keep', 0.95)

        if round_num > 1:
            prev_infl_mat = self.blackboard.read(f'influence_{round_num-1}')
        else:
            prev_infl_mat = np.zeros_like(infl_mat)

        delta_infl_mat = infl_mat - prev_infl_mat

        """
            rules for mow partition:
                keep in round 1
                only steal form non-mows
                only give to fellow mows
            rules for enemies:
                steal from mows
            rules for friendlies:
                steal from a current victim
                not a mow
            rules for others:
                not any of the above
        """
        if round_num == 0:
            player_classes = np.array([self.PLAYER_CLASS_CAT if i == player_idx else self.PLAYER_CLASS_UNKNOWN for i in range(len(infl_mat))])
        elif round_num == 1:
            likely_mow = np.isclose(np.diag(delta_infl_mat), prev_pop_vec * alpha * keep_coef, rtol=0.01)
            player_classes = np.array([self.PLAYER_CLASS_CAT if m else self.PLAYER_CLASS_OTHER for m in likely_mow])
            #player_classes[player_idx] = self.PLAYER_CLASS_CAT
        else:
            prev_player_classes = self.blackboard.read('player_classes')
            player_classes = np.array([self.PLAYER_CLASS_UNKNOWN for _ in range(len(prev_player_classes))])
            for i, prev_class in enumerate(prev_player_classes):
                num_cat_attacks = np.sum(
                    (prev_player_classes == self.PLAYER_CLASS_CAT) \
                        * (infl_mat[i] < 0)
                )
                num_cat_gives = np.sum(
                    (prev_player_classes == self.PLAYER_CLASS_CAT) \
                        * (infl_mat[i] > 0)
                )
                num_notcat_gives = np.sum(
                    (prev_player_classes != self.PLAYER_CLASS_CAT) \
                        * (infl_mat[i] > 0) * (prev_pop_vec > 0)
                )
                num_notcat_attacks = np.sum(
                    (prev_player_classes != self.PLAYER_CLASS_CAT) \
                        * (infl_mat[i] < 0) * (prev_pop_vec > 0)
                )

                if prev_class == self.PLAYER_CLASS_CAT:
                    if num_cat_attacks > 0:
                        player_classes[i] = self.PLAYER_CLASS_ENEMY
                    elif num_notcat_gives > 0:
                        player_classes[i] = self.PLAYER_CLASS_OTHER
                    elif num_notcat_attacks > 0 or num_cat_gives > 0:
                        player_classes[i] = self.PLAYER_CLASS_CAT
                    else:
                        player_classes[i] = self.PLAYER_CLASS_OTHER
                elif prev_class == self.PLAYER_CLASS_ENEMY:
                    player_classes[i] = self.PLAYER_CLASS_ENEMY
                elif prev_class == self.PLAYER_CLASS_FRIENDLY:
                    if num_cat_attacks > 0:
                        player_classes[i] = self.PLAYER_CLASS_ENEMY
                    elif num_notcat_attacks > 0:
                        player_classes[i] = self.PLAYER_CLASS_FRIENDLY
                    elif num_notcat_gives > 0:
                        player_classes[i] = self.PLAYER_CLASS_OTHER
                    else:
                        player_classes[i] = self.PLAYER_CLASS_OTHER
                elif prev_class == self.PLAYER_CLASS_OTHER:
                    if num_cat_attacks > 0:
                        player_classes[i] = self.PLAYER_CLASS_ENEMY
                    elif num_notcat_attacks > 0:
                        player_classes[i] = self.PLAYER_CLASS_FRIENDLY
                    elif num_notcat_gives > 0:
                        player_classes[i] = self.PLAYER_CLASS_OTHER
                    else:
                        player_classes[i] = self.PLAYER_CLASS_OTHER
                else:
                    print(f'ERROR: unknown player class `{prev_class}`')

                if i == player_idx:
                    player_classes[i] = self.PLAYER_CLASS_CAT

        self.blackboard.scribe('player_classes', player_classes)


    def play_round(self, player_idx, round_num, recieved, popularities, influence, extra_data, extra_flag=False):
        start_time = time()
        self.blackboard.scribe(f'recieved_{round_num}', recieved)
        self.blackboard.scribe(f'popularities_{round_num}', popularities)
        self.blackboard.scribe(f'influence_{round_num}', influence)
        self.blackboard.scribe(f'extra_data_{round_num}', extra_data)

        my_pop = popularities[player_idx]
        n = len(popularities)
        tkns = 2 * n

        self.class_partition(player_idx, round_num)

        transaction_vec = np.zeros_like(popularities)

        if my_pop == 0:
            transaction_vec[player_idx] = 1
            return transaction_vec


        """
        if round 1:
            give sign
        else:
            detect other thieves:
                kept first round
                attacks non-thieves
                gave evenly to only other thieves
            while tokens remain:
                choose victim according to the following:
                    the strongest attacker of any thief
                    the weakest non-thief
                pred additional attacks based on other thieves and currently attacking players
                choose attack such that given the above the victim will at worst have X pop remaining

                if no victim and other thieves:
                    give remaining tokens to other thieves evenly
                if non one else is alive:
                    keep remaining tokens
        """

        _, _ = self.reverse_engine.T_hat(influence)

        T_bar = self.reverse_engine.get_transaction()

        num_players = self.game_params['num_players']
        self.game_params['base_popularity'] = popularities

        nonlinear_constraint = NonlinearConstraint(row_sum_constraint,
                        lb=1-1e-5,
                        ub=1+1e-5,
                        jac=row_sum_constraint_J
        )

        player_classes = self.blackboard.read('player_classes')
        inital_actions = []
        if np.any(player_classes != self.PLAYER_CLASS_CAT):
            total_steal = (player_classes != self.PLAYER_CLASS_CAT).astype(float)
            total_steal = total_steal / np.sum(total_steal)
            inital_actions.append(total_steal)

        mutual_CAT_give = (player_classes == self.PLAYER_CLASS_CAT).astype(float)
        mutual_CAT_give = mutual_CAT_give / np.sum(mutual_CAT_give)
        inital_actions.append(mutual_CAT_give)

        best_action = np.eye(num_players)[player_idx]
        best_rank = np.inf
        for init_vec in inital_actions:
            result = minimize(world_model,
                            init_vec,
                            args=(
                                    self.game_params,
                                    self.predict,
                                    self.rank,
                                    (T_bar, player_classes, player_idx),
                                    (player_classes, self.class_weights, player_idx)
                                ),
                            method='trust-constr',
                            constraints=nonlinear_constraint)
            #print(f'inital value: {init_vec}')
            #print(f'\tresult value: {result.x}')
            #print(f'\trank value: {result.fun}')
            if best_rank > result.fun:
                best_rank = result.fun
                best_action = result.x

        transaction_vec = np.round(best_action, decimals=2)

        #print(f'Classes: {player_classes}')
        #print(f'Popularities: {np.round(popularities, decimals=2)}')
        #print(f'{transaction_vec} = {np.sum(np.abs(transaction_vec))}')
        #print(f'Final action rank: {best_rank}')
        #print(f'Total time: {time() - start_time}\n\n')

        return transaction_vec


    def setGameParams(self, gameParams, _forcedRandom):
        self.gameParams = gameParams
        self.forced_random = _forcedRandom

    def getType(self):
        return self.whoami

    def get_vote(self, player_idx, round_num, received, popularities, influence, extra_data, current_options_matrix):
        transaction_vector = self.play_round(player_idx, round_num, received, popularities, influence, extra_data, True)
        final_vote = translateVecToIndex(transaction_vector, current_options_matrix)
        return final_vote # please let this work
