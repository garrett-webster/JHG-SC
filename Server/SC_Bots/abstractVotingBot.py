from abc import ABC, abstractmethod

class AbstractVotingBot(ABC):
    pass
    # self.self_id = self_id  # how we know who we are.
    # self.type = "BG"  # used for the long term grapher. could probably consolidate iwth number type
    # self.chromosome # a bunch fo values that dictate excactrly how the voting algorithm behaves.
    # self.risk_adversity = "MAX" # this is never used. legacy code we should delete.
    # self.number_type = 6 used to keep track of the bot type in name maps and whatnot.
    # self.social_lubrication How likely we are to give in for the sake of society.
    # self.bad_vote what we hold on too.
    # no need to define an init statement, but maybe having the whole list here could be helpful.

    @abstractmethod
    def set_chromosome(self, chromosome):
        pass

    @abstractmethod
    def get_number_type(self):
        pass

    @abstractmethod
    def get_vote(self, current_options_matrix, previous_votes, cycle=0, max_cycle=3):
        pass