import numpy as np
from copy import deepcopy

from Server.Engine.engine import JHGEngine
from Server.Engine.blackboard import BlackBoard

class JHGReverse():
    def __init__(self, alpha=0.2, beta=0.75, give=1.4, keep=1.0, steal=1.1,
                 num_players=3, base_popularity=100.0, poverty_line=0.):
        self.inner_engine = JHGEngine(alpha, beta, give, keep, steal, 
                                        num_players, base_popularity)
        self.blackboard = BlackBoard()

    def T_hat(self, I):
        #TODO: Handle deaths
        #TODO: Handle scaling due to over kill
        #TODO: Handle blackboard usage
        P0 = self.inner_engine.get_popularity()
        self.inner_engine.apply_transaction(np.zeros_like(I), normalize=False)
        I0 = self.inner_engine.get_influence()

        neg_infl = np.sum(np.abs(np.minimum(I - I0, 0)), axis=1)
        I_prime = I - I0 - np.diag(neg_infl)
        np.fill_diagonal(I_prime, np.maximum(np.diag(I_prime), 0.))

        c_g = self.inner_engine.C_g
        c_k = self.inner_engine.C_k
        c_s = self.inner_engine.C_s

        alpha = self.inner_engine.alpha

        coefs_prime = np.ones_like(I_prime)
        coefs_prime[I_prime > 0] = c_g
        coefs_prime[I_prime < 0] = c_s
        np.fill_diagonal(coefs_prime, c_k)

        with np.errstate(divide='ignore', invalid='ignore'):
            T_prime = I_prime / (coefs_prime * P0[:, np.newaxis] * alpha)
            T_prime[np.isnan(T_prime)] = 0.0
            T_prime[np.isinf(T_prime)] = 0.0
            #T_prime = np.clip(T_prime, -1., 1.)
        
        sigma = np.sum(np.abs(T_prime), axis=1)

        T_hat = deepcopy(T_prime)

        for i_ in np.argwhere(sigma < 1.0):
            i = i_[0]
            if P0[i] <= 0.0:
                continue
            for j_ in np.argwhere(T_hat[i] < 0):
                j = j_[0]
                curr_ratio = np.abs(T_hat[j, j]) * P0[j] \
                                / (np.abs(np.minimum(T_hat[:, j], 0.0)) @ P0)
                ratio_adjust = np.abs(I_prime[i, j]) \
                                / (alpha * c_s * np.abs(T_hat[i, j]) * P0[i])
                phi = ratio_adjust + curr_ratio
                T_prime[i, j] = phi * T_prime[i, j]

        for i in np.argwhere(np.linalg.norm(T_prime, ord=1, axis=1) == 0).flatten():
            T_prime[i] = np.eye(self.inner_engine.N)[i]

        self.inner_engine.step_back()
        self.inner_engine.apply_transaction(T_prime, normalize=False)
        pred_infl = self.inner_engine.get_influence()

        mat_error = pred_infl - I
        infl_error = np.sum(np.abs(mat_error))

        return T_prime, infl_error

    def get_transaction(self):
        return self.inner_engine.get_transaction()

class JHGReverseOld():
    def __init__(self, alpha=0.2, beta=0.75, give=1.4, keep=1.0, steal=1.1,
                 num_players=3, base_popularity=100.0):
        # Scalars
        # Weight the value of previous exchanges
        self.alpha = alpha

        # Weights the value of previous popularity scores
        self.beta = beta

        # scaling coefficient for tokens given, kept and stolen
        self.C_g = give
        self.C_k = keep
        self.C_s = steal

        # total number of players
        self.N = num_players

        # Popularity of player i at time t
        self.p0 = base_popularity  # can be either a scalar or a vector
        self.P = []
        self.P.append(np.ones(self.N) * self.p0)

        # current round number
        self.t = 0

        # historical transaction matrices
        self.T = []
        self.T.append(np.zeros((self.N, self.N)))

        # influence matrices
        self.I = []
        self.I.append(np.eye(self.N))  # i = influences => j

        # approximation params
        self._default_theta = 1
        self._default_phi = 1
        self.theta = [self._default_theta]
        self.phi = [self._default_phi]

        # inner engine
        self.inner_engine = JHGEngine(alpha=self.alpha, beta=self.beta, 
            give=self.C_g, keep=self.C_k, steal=self.C_s, num_players=self.N, 
            base_popularity=self.p0)

    def T_hat(self, tau, t, I_prime):
        res = np.zeros_like(I_prime)
        numer = I_prime - (1-self.alpha)*self.V(tau-1, t)
        coefs = (numer > 0) * self.C_g + (numer < 0) * self.C_s
        np.fill_diagonal(coefs, self.C_k)
        with np.errstate(divide='ignore', invalid='ignore'):
            res = numer / (self.alpha * coefs * self.W(tau, t)[:, np.newaxis])
            res[np.isnan(res)] = 0.0
            res[np.isinf(res)] = 0.0

            steal_infl = np.linalg.norm(np.abs(np.minimum(I_prime, 0.)), axis=1, ord=1)
            keep_raw = (numer - np.diag(steal_infl)) / (self.alpha * self.C_k * self.W(tau, t)[:, np.newaxis])
            keep_res = np.zeros_like(keep_raw)
            np.fill_diagonal(keep_res, np.maximum(0.0, np.diag(keep_raw)))

            give_res = numer / (self.alpha * self.C_g * self.W(tau, t)[:, np.newaxis])
            give_res[give_res < 0] = 0
            np.fill_diagonal(give_res, 0)

            '''
            w = self.W(tau, t)
            Cs = np.zeros_like(w)
            with np.errstate(divide='ignore', invalid='ignore'):
                Cs = self.C_s * np.maximum(1 - (give_res * w) / (np.ones((1, self.N)) @ (np.abs(T_minus) * w[:, np.newaxis])), 0)
                Cs[np.isnan(Cs)] = 0.0
                Cs[np.isinf(Cs)] = 0.0
            '''
            steal_res = numer / (self.alpha * self.C_s * self.W(tau, t)[:, np.newaxis])
            steal_res[steal_res > 0] = 0
            np.fill_diagonal(steal_res, 0)


            np.fill_diagonal(res, 0)
            np.fill_diagonal(res, 
                np.maximum(0.0, 1.0 - np.linalg.norm(res, axis=1, ord=1)))

            print('give:\n', np.round(give_res, decimals=3))
            print('steal:\n', np.round(steal_res, decimals=3))
            print('keep:\n', np.round(keep_res, decimals=3))
            print(f'conf cnt:\n{np.sum(np.logical_and(give_res != 0, steal_res != 0))}')
            print(f'res norm: {np.linalg.norm(res, axis=1, ord=1)}')

        return res

    def V(self, tau, t):
        if tau >= 1:
            return self.alpha * self.phi[tau] * self.V_hat(tau, t) \
                + (1 - self.alpha) * self.V(tau - 1, t)
        else:
            return 0

    def V_hat(self, tau, t):
        T_ = self.T[tau]

        T_plus = np.clip(T_, 0, 1)
        np.fill_diagonal(T_plus, 0)

        T_minus = np.clip(T_, -1, 0)
        T_minus = T_minus * (self.P[tau - 1] > 0)
        np.fill_diagonal(T_minus, 0)

        T_diag = np.zeros_like(T_)
        np.fill_diagonal(T_diag, np.diag(T_))

        w = self.W(tau, t)

        pK = self.C_k * T_diag
        pG = self.C_g * T_plus
        pS = np.zeros_like(T_)
        np.fill_diagonal(
            pS, np.sum(-(self.C_s * self.theta[tau] * T_minus), axis=1))

        pS += self.C_s * self.theta[tau] * T_minus
        return w[:, np.newaxis] * (pK + pG + pS)

    def W(self, tau, t):
        return self.beta * self.P[tau - 1] \
            + self.eta(tau, t) * (1 - self.beta) * self.P[t - 1]

    def eta(self, tau, t):
        return sum(self.P[tau - 1]) / sum(self.P[t-1])

    def update(self, I, p, r, g, idx):
        # Update with the Influence, popularity, recieved and given matrices
        #TODO: update this to approximate theta and phi
        self._add_influence(I)
        self._add_popularity(p)
        T_ = np.zeros((self.N, self.N))
        T_[idx] = g
        T_[:, idx] = r
        self._add_transaction(T_)
        self.theta.append(self._default_theta)
        self.phi.append(self._default_phi)

    def update_action(self, reciever, giver, amount, tau):
        self.T[tau][giver, reciever] = amount

    def _add_popularity(self, popularity):
        self.P.append(popularity)

    def _add_influence(self, influence):
        self.I.append(influence)

    def _add_transaction(self, T_):
        self.T.append(T_)

