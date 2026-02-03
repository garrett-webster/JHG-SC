# from Server.SC_Bots.transVecTranslator import translateVecToIndex
from stagHare.transVecTranslatorStagHare import translateVecToIndexStagHare
import numpy as np
from stagHare.utils.a_star import AStar


from stagHare.utils.pathfindingTime import findPath





# so at a high level
# what I need is

# take in an allocation, and then return a tuple, which is the new movement.
def jhg_to_staghunt(allocation: list) -> tuple[int, int]:
    pass
    # allocation to generators (for which we have the translator)
        # htis is sort of a p --> np problem, as this direction is pretty easy.

    # then we return a move from the generators, taking the most likely one
    # then we return the move.




# old allcation to movement. needs work. tank needs fuel.
def allocation_to_movement(new_allocation, id, state):
    pass
    # hare = [-2, -2, 2] # just for simplicity sake. # This is just as easy as it gets.
    # stag = [2, 2, 2]

    # this SHOULD be better.
    # this was the old version want
    hare_move = np.zeros(3)
    hare_move.fill(-2)
    hare_move[id] = 2

    # way less altruistic version we got going on here.
    hare = np.zeros(3)
    hare.fill(0)
    hare[id] = 6


    stag = np.zeros(3)
    stag.fill(2)

    # print("we are working with id ", id)
    # print("this is the new allocation ", new_allocation)
    # print("this is the corresponding hare thing ", hare)
    # nothing should be created automatically.
    new_current_options_matrix = [hare, stag, hare_move]
    # return this so we have a means with which we can specify the bots current eating desire.
    new_index = translateVecToIndexStagHare(new_allocation, new_current_options_matrix, False)
    new_movement = generate_movement(state, id, new_index)

    type = "Stag"
    if new_index == 0:
        type = "Hare"
    # print("Here is teh agent ", id, " and here is the movement type ", type)

    # print('this is the new movement ', new_movement)
    return new_movement[0], new_movement[1], new_index==0

def generate_movement(state, id, new_index):
    player_name = "R" + str(id) # zero index, then 2 agetns in front of them.
    player_position = state.agent_positions[player_name]
    curr_row, curr_col = player_position[0], player_position[1]

    if new_index == 0:
        goal_row, goal_col = state.agent_positions["hare"][0], state.agent_positions["hare"][1]

    elif new_index == 1:
        goal_row, goal_col = state.agent_positions["stag"][0], state.agent_positions["stag"][1]

    elif new_index == 2:
        goal_row, goal_col = state.agent_positions["hare"][0], state.agent_positions["hare"][1]

    else:
        return curr_row, curr_col

    path =  findPath(state, curr_row, curr_col, goal_row, goal_col)
    return path