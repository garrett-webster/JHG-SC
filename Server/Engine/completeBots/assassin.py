from baseagent import AbstractAgent
from utils.blackboard import BlackBoard

import numpy as np
from copy import deepcopy

class AssassinAgent(AbstractAgent):

    def __init__(self, pay_taxes=False):
        super().__init__()
        self.pay_taxes = pay_taxes
        self.blackboard = BlackBoard()
        self.whoami = 'assassin'

    def get_tokens(self, alpha, coef, targ_inf, pop):
        with np.errstate(divide='ignore', invalid='ignore'):
            tkns =  targ_inf / (alpha * pop * coef)
            if np.isscalar(tkns):
                if np.isnan(tkns) or np.isinf(tkns):
                    return 0.
            else:
                tkns[np.logical_or(np.isnan(tkns), np.isinf(tkns))] = 0.
        return tkns

    def get_my_taxes(self, extra_data):
        taxes = {}
        for p_id, data in extra_data.items():
            if data is not None and data.get('is_government', False):
                taxes[p_id] = data.get('taxes', 0.)
        return taxes

    def setGameParams(self, gameParams, _forcedRandom):
        pass # doesn't actually do anything, I just need it to do nothing.

    def play_round(self, player_idx, round_num, recieved, popularities, influence, extra_data):
        self.blackboard.scribe(f'recieved_{round_num}', recieved)
        self.blackboard.scribe(f'popularities_{round_num}', popularities)
        self.blackboard.scribe(f'influence_{round_num}', influence)
        self.blackboard.scribe(f'extra_data_{round_num}', extra_data)

        my_taxes = self.get_my_taxes(extra_data)

        my_pop = popularities[player_idx]

        if my_pop == 0:
            transaction_vec = np.zeros_like(popularities)
            transaction_vec[player_idx] = 1
            return transaction_vec

        tkns = len(popularities) * 2
        ###print(f'\n{"".join(["@@"]*40)}\n')
        ###print(f'Round {round_num}')
        ###print(f'Assassin @ {player_idx} w/ {popularities[player_idx]:.2f}\n')
        ###print(f'infl:\n{np.round(influence, decimals=2)}\n')
        if round_num >= 1:
            alpha = extra_data[player_idx].get('alpha', 0.15)
            steal_coef = extra_data[player_idx].get('steal', 1.6)
            keep_coef = extra_data[player_idx].get('keep', 0.95)

            my_pop = popularities[player_idx]
            processed_pops = deepcopy(popularities)
            processed_pops[player_idx] = 0
            
            transaction_vec =  np.zeros_like(popularities)

            for i, taxes in my_taxes.items():
                tax_tkns = taxes
                transaction_vec[i] = min(tax_tkns, max(0., tkns - np.linalg.norm(transaction_vec, ord=1))) if tax_tkns != 0 and self.pay_taxes else transaction_vec[i]

            prev_infl = self.blackboard.read(f'influence_{max(0, round_num - 1)}')
            prev_pop = self.blackboard.read(f'popularities_{max(0, round_num - 1)}')

            if round_num == 1:
                likely_assissins = np.isclose(np.diag(influence), prev_pop * alpha * keep_coef, rtol=0.01)
                likely_assissins[player_idx] = False
                self.blackboard.scribe('likely_assassins', likely_assissins)
            else:
                likely_assissins = self.blackboard.read('likely_assassins')
                infl_copy = deepcopy(influence)
                np.fill_diagonal(infl_copy, 0)
                ###print(f'sum infl: {np.sum(infl_copy > 0, axis=1)}')
                all_attacks = np.sum(infl_copy > 0, axis=1) == 0
                self.blackboard.scribe('likely_assassins', likely_assissins * all_attacks)

            delta_inf_mag = np.abs(influence) - np.abs(prev_infl)
            ###print(f'delta:\n{np.round(delta_inf_mag, decimals=2)}\n')

            stealer_mat = (delta_inf_mag > 0) * (influence < 0)
            ###print(f'stealers:\n{stealer_mat.astype(int)}\n')
            ###print(f'{stealer_mat[player_idx].astype(int)} v. {stealer_mat[:, player_idx].astype(int)}\nw/ {np.round(recieved, decimals=2)}\n')

            expected_assassins = self.blackboard.read('likely_assassins')

            ###print(f'other assassins: {np.argwhere(expected_assassins)}')

            for idx in np.argsort(processed_pops):
                if idx == player_idx or (self.pay_taxes and idx == 0) or expected_assassins[idx]:
                    continue

                ###print(f'\nassessing p{idx}')
                remaining_tkns = tkns - np.linalg.norm(transaction_vec, ord=1)
                ###print(f'tkns remaining: {remaining_tkns:.3f}')
                if remaining_tkns <= 0:
                    break

                weak_pop = popularities[idx]
                ###print(f'targ @ {weak_pop:.3f} pop')
                # TODO: add in knowledge of other attacks
                if weak_pop <= 0:
                    continue

                attackers = stealer_mat[:, idx]
                attackers[player_idx] = 0 # ignore yourself
                attackers[expected_assassins] = 0 # ignore other assassins for now
                attackers[popularities <= 0] = 0
                attackers[np.arange(len(attackers))] = False
                attacker_pops = prev_pop[attackers]
                infl_delta = delta_inf_mag[attackers, idx]
                attack_tkns = self.get_tokens(alpha, steal_coef, infl_delta, attacker_pops)
                ###print(f'attackers vec: {attackers.astype(int)}')
                ###print(f'attacker tkns: {attack_tkns}')
                attacker_curr_pops = popularities[attackers]

                assassin_pops = popularities[expected_assassins]

                targ_prop = self.get_tokens(alpha, steal_coef, weak_pop, my_pop)
                potential_inf = my_pop * min( 1.0, targ_prop)
                assassin_infl = np.sum(assassin_pops * np.minimum(self.get_tokens(alpha, steal_coef, weak_pop, assassin_pops), 1.0))
                likely_ratio = potential_inf / (np.sum(attack_tkns * attacker_curr_pops) + potential_inf + assassin_infl)
                ###print(f'likely ratio: {likely_ratio:.3f}')
                likely_prop = likely_ratio * targ_prop
                ###print(f'raw action: -{targ_prop:.3f}')
                ###print(f'recommended action: -{likely_prop:.3f}')
                tkn_alloc = min(remaining_tkns, likely_prop * tkns)
                ###print(f'taking action: -{tkn_alloc:.3f}')
                transaction_vec[idx] = -tkn_alloc
                ###print(f'{"".join(["~"]*10)}')


        else:
            transaction_vec = np.zeros_like(popularities)
            for i, taxes in my_taxes.items():
                tax_tkns = taxes
                transaction_vec[i] = min(tax_tkns, max(0., tkns - np.linalg.norm(transaction_vec, ord=1))) if tax_tkns != 0 and self.pay_taxes else transaction_vec[i]
            
        transaction_vec[player_idx] = tkns - np.linalg.norm(transaction_vec, ord=1)

        ###print(f'\n{"".join(["<>"]*40)}\n')
        ###print(f'assassin transaction: {np.round(transaction_vec, decimals=2)}')
        ###print(f'\n{"".join(["@@"]*40)}\n')
        transaction_vec = transaction_vec / (np.linalg.norm(transaction_vec, ord=1) + 1e-6)
        return transaction_vec
