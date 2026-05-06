"""
the goal of this script is to make a JHG engine that can run
and then from there, I can test the allocations and whatnot from that JHG script to try and understand intent
I want to see if the staghunt_to_jhg function is broken or what.
steps: get just a jhg game running and make sure it works
track the allocations
run them through the thing, track intents
measure with various bots.
break.
"""
from tqdm import tqdm
from offlineSimStuff.runningTools.runnerHelper import * # get all the functions
from Server.Engine.simulator import GameSimulator
from stagHare.environment.jhgToStaghunt import allocation_to_movement, allocation_to_intent
from stagHare.runnerHelper import create_hunters_with_list

if __name__ == "__main__":

    random_agents = False
    forced_random = True
    agents = ["GHare", "Ghare", "GHare"] # anticipated behavior

    hunters = create_hunters_with_list(random_agents, forced_random, agents)


    current_jhg_sim = create_jhg_engine(3) # just create a nice lil engine.


    # need to create a JHG engine and a STAGHare engine
    # JHG is way easier.



